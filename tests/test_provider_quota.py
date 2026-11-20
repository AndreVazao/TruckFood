import threading
import unittest

from truckfood_providers.quota import (
    QuotaExceeded, QuotaManager, QuotaPolicy, QuotaPolicyMissing,
    QuotaReservationConflict, QuotaReservationNotFound,
)


class FakeClock:
    def __init__(self):
        self.value = 0.0

    def now(self):
        return self.value

    def advance(self, seconds):
        self.value += seconds


class QuotaManagerTests(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.manager = QuotaManager(
            {("provider-a", "geocode"): QuotaPolicy(
                max_units=5, window_seconds=60, reservation_ttl_seconds=10
            )},
            clock=self.clock.now,
        )

    def test_reservation_holds_capacity_before_provider_call(self):
        reservation = self.manager.reserve(
            "provider-a", "geocode", units=3, reservation_id="request-1"
        )
        snapshot = self.manager.snapshot("provider-a", "geocode")
        self.assertEqual(reservation.units, 3)
        self.assertEqual(snapshot.reserved_units, 3)
        self.assertEqual(snapshot.remaining_units, 2)

    def test_limit_is_enforced_including_concurrent_reservations(self):
        self.manager.reserve("provider-a", "geocode", units=3, reservation_id="r1")
        with self.assertRaises(QuotaExceeded):
            self.manager.reserve("provider-a", "geocode", units=3, reservation_id="r2")

    def test_settlement_converts_reserved_units_to_actual_consumption(self):
        self.manager.reserve("provider-a", "geocode", units=3, reservation_id="r1")
        snapshot = self.manager.settle("r1", actual_units=2)
        self.assertEqual(snapshot.consumed_units, 2)
        self.assertEqual(snapshot.reserved_units, 0)
        self.assertEqual(snapshot.remaining_units, 3)

    def test_settlement_defaults_to_full_reserved_amount(self):
        self.manager.reserve("provider-a", "geocode", units=2, reservation_id="r1")
        snapshot = self.manager.settle("r1")
        self.assertEqual(snapshot.consumed_units, 2)

    def test_actual_usage_cannot_exceed_reservation(self):
        self.manager.reserve("provider-a", "geocode", units=2, reservation_id="r1")
        with self.assertRaises(QuotaExceeded):
            self.manager.settle("r1", actual_units=3)
        self.assertEqual(self.manager.snapshot("provider-a", "geocode").reserved_units, 2)

    def test_release_returns_reserved_capacity(self):
        self.manager.reserve("provider-a", "geocode", units=4, reservation_id="r1")
        snapshot = self.manager.release("r1")
        self.assertEqual(snapshot.reserved_units, 0)
        self.assertEqual(snapshot.remaining_units, 5)

    def test_expired_reservation_keeps_capacity_until_explicit_reconciliation(self):
        self.manager.reserve("provider-a", "geocode", units=5, reservation_id="r1")
        self.clock.advance(10)
        snapshot = self.manager.snapshot("provider-a", "geocode")
        self.assertEqual(snapshot.reserved_units, 5)
        self.assertEqual(snapshot.remaining_units, 0)
        with self.assertRaises(QuotaExceeded):
            self.manager.reserve("provider-a", "geocode", reservation_id="r2")

        settled = self.manager.settle("r1")
        self.assertEqual(settled.consumed_units, 5)
        self.assertEqual(settled.reserved_units, 0)
        self.assertEqual(settled.remaining_units, 0)

    def test_expired_reservation_can_be_released_after_confirmed_no_usage(self):
        self.manager.reserve("provider-a", "geocode", units=5, reservation_id="r1")
        self.clock.advance(10)
        snapshot = self.manager.release("r1")
        self.assertEqual(snapshot.reserved_units, 0)
        self.assertEqual(snapshot.remaining_units, 5)

    def test_expired_reservation_can_be_settled_after_window_boundary(self):
        self.manager.reserve("provider-a", "geocode", units=2, reservation_id="r1")
        self.clock.advance(61)
        historical = self.manager.settle("r1", actual_units=1)
        self.assertEqual(historical.window_id, 0)
        self.assertEqual(historical.consumed_units, 1)
        self.assertEqual(historical.reserved_units, 0)

        current = self.manager.snapshot("provider-a", "geocode")
        self.assertEqual(current.window_id, 1)
        self.assertEqual(current.remaining_units, 5)

    def test_reservation_identifier_is_idempotent_while_active(self):
        first = self.manager.reserve("provider-a", "geocode", units=2, reservation_id="same")
        second = self.manager.reserve("provider-a", "geocode", units=2, reservation_id="same")
        self.assertEqual(first, second)
        self.assertEqual(self.manager.snapshot("provider-a", "geocode").reserved_units, 2)

    def test_reservation_identifier_cannot_be_reused_for_other_request(self):
        self.manager.reserve("provider-a", "geocode", units=2, reservation_id="same")
        with self.assertRaises(QuotaReservationConflict):
            self.manager.reserve("provider-a", "geocode", units=1, reservation_id="same")

    def test_terminal_reservation_identifier_cannot_be_replayed(self):
        self.manager.reserve("provider-a", "geocode", units=2, reservation_id="same")
        self.manager.release("same")
        with self.assertRaises(QuotaReservationConflict):
            self.manager.reserve("provider-a", "geocode", units=2, reservation_id="same")

    def test_policies_are_isolated_by_provider_and_operation(self):
        other = QuotaManager({
            ("provider-a", "geocode"): QuotaPolicy(max_units=1),
            ("provider-b", "geocode"): QuotaPolicy(max_units=3),
            ("provider-a", "route"): QuotaPolicy(max_units=2),
        }, clock=self.clock.now)
        other.reserve("provider-a", "geocode", reservation_id="a")
        other.reserve("provider-b", "geocode", units=3, reservation_id="b")
        other.reserve("provider-a", "route", units=2, reservation_id="c")
        self.assertEqual(other.snapshot("provider-b", "geocode").remaining_units, 0)

    def test_missing_policy_fails_closed(self):
        with self.assertRaises(QuotaPolicyMissing):
            self.manager.reserve("provider-b", "route", reservation_id="r1")

    def test_window_resets_consumption(self):
        self.manager.reserve("provider-a", "geocode", units=5, reservation_id="r1")
        self.manager.settle("r1")
        self.clock.advance(60)
        self.assertEqual(self.manager.snapshot("provider-a", "geocode").remaining_units, 5)

    def test_reservation_cannot_outlive_window(self):
        self.clock.advance(55)
        reservation = self.manager.reserve("provider-a", "geocode", reservation_id="r1")
        self.assertEqual(reservation.expires_at, 60)

    def test_reservation_capacity_fails_closed(self):
        bounded = QuotaManager(
            {("provider-a", "geocode"): QuotaPolicy(max_units=5)},
            clock=self.clock.now, max_reservations=1,
        )
        bounded.reserve("provider-a", "geocode", reservation_id="r1")
        with self.assertRaises(QuotaExceeded):
            bounded.reserve("provider-a", "geocode", reservation_id="r2")

    def test_parallel_reservations_never_exceed_limit(self):
        manager = QuotaManager(
            {("provider-a", "geocode"): QuotaPolicy(max_units=10)},
            clock=self.clock.now,
        )
        barrier = threading.Barrier(20)
        successes = []
        failures = []

        def reserve(index):
            barrier.wait()
            try:
                manager.reserve("provider-a", "geocode", reservation_id=f"r{index}")
                successes.append(index)
            except QuotaExceeded:
                failures.append(index)

        workers = [threading.Thread(target=reserve, args=(i,)) for i in range(20)]
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join(2)
        self.assertTrue(all(not worker.is_alive() for worker in workers))
        self.assertEqual(len(successes), 10)
        self.assertEqual(len(failures), 10)
        self.assertEqual(manager.snapshot("provider-a", "geocode").reserved_units, 10)

    def test_invalid_policy_and_arguments_are_rejected(self):
        for kwargs in (
            {"max_units": 0}, {"window_seconds": 0},
            {"reservation_ttl_seconds": float("inf")},
        ):
            config = {"max_units": 1}
            config.update(kwargs)
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                QuotaPolicy(**config)
        for units in (0, -1, True, 1.5):
            with self.subTest(units=units), self.assertRaises(ValueError):
                self.manager.reserve("provider-a", "geocode", units=units, reservation_id="x")

    def test_settle_and_release_are_not_interchangeable(self):
        self.manager.reserve("provider-a", "geocode", reservation_id="r1")
        self.manager.settle("r1")
        with self.assertRaises(QuotaReservationConflict):
            self.manager.release("r1")


if __name__ == "__main__":
    unittest.main()
