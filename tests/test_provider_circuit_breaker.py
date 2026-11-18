import threading
import unittest

from truckfood_providers.adapters import DispatchResult
from truckfood_providers.circuit_breaker import (
    CircuitBreaker, CircuitBreakerPolicy, CircuitState,
)


class FakeClock:
    def __init__(self):
        self.value = 0.0

    def now(self):
        return self.value

    def advance(self, seconds):
        self.value += seconds


def dispatch(outcome="success", error_code=None):
    return DispatchResult(outcome=outcome, error_code=error_code)


class CircuitBreakerTests(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.breaker = CircuitBreaker(
            CircuitBreakerPolicy(failure_threshold=2, recovery_timeout_seconds=10),
            clock=self.clock.now,
        )

    def test_starts_closed(self):
        snap = self.breaker.snapshot("provider-a", "geocode")
        self.assertEqual(snap.state, CircuitState.CLOSED)
        self.assertEqual(snap.consecutive_failures, 0)

    def test_opens_after_consecutive_unavailable_results(self):
        self.breaker.execute("provider-a", "route", lambda: dispatch("unavailable", "upstream_down"))
        self.breaker.execute("provider-a", "route", lambda: dispatch("unavailable", "upstream_down"))
        snap = self.breaker.snapshot("provider-a", "route")
        self.assertEqual(snap.state, CircuitState.OPEN)
        self.assertEqual(snap.consecutive_failures, 2)
        self.assertEqual(snap.retry_after_seconds, 10)

    def test_open_circuit_rejects_without_invoking_provider(self):
        self.breaker.execute("provider-a", "route", lambda: dispatch("unavailable", "down"))
        self.breaker.execute("provider-a", "route", lambda: dispatch("unavailable", "down"))
        called = []
        result = self.breaker.execute(
            "provider-a", "route", lambda: called.append(True) or dispatch()
        )
        self.assertEqual(result.error_code, "circuit_open")
        self.assertFalse(result.retryable)
        self.assertFalse(result.metadata["provider_invoked"])
        self.assertEqual(called, [])

    def test_success_resets_consecutive_failure_count(self):
        self.breaker.execute("provider-a", "route", lambda: dispatch("unavailable", "down"))
        self.breaker.execute("provider-a", "route", lambda: dispatch("success"))
        snap = self.breaker.snapshot("provider-a", "route")
        self.assertEqual(snap.state, CircuitState.CLOSED)
        self.assertEqual(snap.consecutive_failures, 0)

    def test_non_health_outcomes_do_not_count_as_provider_failure(self):
        for outcome, code in (
            ("rate_limited", "quota"), ("invalid", "bad_input"),
            ("unsupported", "not_supported"), ("conflict", "conflict"),
        ):
            self.breaker.execute("provider-a", "route", lambda o=outcome, c=code: dispatch(o, c))
        self.assertEqual(
            self.breaker.snapshot("provider-a", "route").consecutive_failures, 0
        )

    def test_breakers_are_isolated_by_provider_and_operation(self):
        self.breaker.execute("provider-a", "route", lambda: dispatch("unavailable", "down"))
        self.breaker.execute("provider-a", "route", lambda: dispatch("unavailable", "down"))
        self.assertEqual(self.breaker.snapshot("provider-a", "route").state, CircuitState.OPEN)
        self.assertEqual(self.breaker.snapshot("provider-b", "route").state, CircuitState.CLOSED)
        self.assertEqual(self.breaker.snapshot("provider-a", "geocode").state, CircuitState.CLOSED)

    def test_half_open_probe_closes_circuit_on_success(self):
        self.breaker.execute("provider-a", "route", lambda: dispatch("unavailable", "down"))
        self.breaker.execute("provider-a", "route", lambda: dispatch("unavailable", "down"))
        self.clock.advance(10)
        result = self.breaker.execute("provider-a", "route", lambda: dispatch("success"))
        self.assertTrue(result.metadata["circuit_probe"])
        self.assertEqual(self.breaker.snapshot("provider-a", "route").state, CircuitState.CLOSED)

    def test_half_open_probe_reopens_circuit_on_unavailable(self):
        self.breaker.execute("provider-a", "route", lambda: dispatch("unavailable", "down"))
        self.breaker.execute("provider-a", "route", lambda: dispatch("unavailable", "down"))
        self.clock.advance(10)
        self.breaker.execute("provider-a", "route", lambda: dispatch("unavailable", "still_down"))
        snap = self.breaker.snapshot("provider-a", "route")
        self.assertEqual(snap.state, CircuitState.OPEN)
        self.assertEqual(snap.retry_after_seconds, 10)

    def test_half_open_probe_limit_rejects_concurrent_extra_probe(self):
        entered = threading.Event()
        release = threading.Event()
        results = []

        self.breaker.execute("provider-a", "route", lambda: dispatch("unavailable", "down"))
        self.breaker.execute("provider-a", "route", lambda: dispatch("unavailable", "down"))
        self.clock.advance(10)

        def probe():
            entered.set()
            release.wait(2)
            return dispatch("success")

        worker = threading.Thread(
            target=lambda: results.append(self.breaker.execute("provider-a", "route", probe))
        )
        worker.start()
        self.assertTrue(entered.wait(2))
        second_called = []
        second = self.breaker.execute(
            "provider-a", "route", lambda: second_called.append(True) or dispatch("success")
        )
        self.assertEqual(second.error_code, "circuit_open")
        self.assertEqual(second_called, [])
        release.set()
        worker.join(2)
        self.assertFalse(worker.is_alive())
        self.assertEqual(len(results), 1)
        self.assertEqual(self.breaker.snapshot("provider-a", "route").state, CircuitState.CLOSED)

    def test_late_completion_from_old_generation_cannot_close_open_circuit(self):
        entered = threading.Event()
        release = threading.Event()

        def slow_failure():
            entered.set()
            release.wait(2)
            return dispatch("unavailable", "late_failure")

        worker = threading.Thread(
            target=lambda: self.breaker.execute("provider-a", "route", slow_failure)
        )
        worker.start()
        self.assertTrue(entered.wait(2))
        self.breaker.execute("provider-a", "route", lambda: dispatch("unavailable", "down"))
        self.breaker.execute("provider-a", "route", lambda: dispatch("unavailable", "down"))
        self.assertEqual(self.breaker.snapshot("provider-a", "route").state, CircuitState.OPEN)
        release.set()
        worker.join(2)
        self.assertFalse(worker.is_alive())
        self.assertEqual(self.breaker.snapshot("provider-a", "route").state, CircuitState.OPEN)

    def test_invalid_configuration_rejected(self):
        for kwargs in (
            {"failure_threshold": 0},
            {"recovery_timeout_seconds": 0},
            {"recovery_timeout_seconds": float("inf")},
            {"half_open_max_calls": 0},
            {"qualifying_outcomes": frozenset({"rate_limited"})},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                CircuitBreakerPolicy(**kwargs)

    def test_invalid_call_arguments_rejected(self):
        for provider, operation in (("", "route"), ("provider-a", ""), (" ", "route")):
            with self.subTest(provider=provider, operation=operation), self.assertRaises(ValueError):
                self.breaker.execute(provider, operation, lambda: dispatch())


if __name__ == "__main__":
    unittest.main()
