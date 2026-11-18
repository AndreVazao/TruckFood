import unittest

from truckfood_providers.adapters import DispatchResult
from truckfood_providers.resilience import (
    OperationRetryPolicy, ResilienceExecutor, RetryPolicy, RetrySafety,
)


class FakeClock:
    def __init__(self):
        self.value = 0.0
        self.sleeps = []

    def now(self):
        return self.value

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.value += seconds

    def advance(self, seconds):
        self.value += seconds


def result(outcome="success", *, retryable=False, error_code=None):
    return DispatchResult(
        outcome=outcome, retryable=retryable, error_code=error_code,
        metadata={"adapter_id": "fixture.adapter"},
    )


class ResilienceExecutorTests(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.executor = ResilienceExecutor(
            RetryPolicy(max_attempts=3, base_delay_seconds=0.2, max_delay_seconds=0.5),
            clock=self.clock.now,
            sleeper=self.clock.sleep,
            random_value=lambda: 1.0,
        )

    def test_success_runs_once(self):
        calls = []
        outcome = self.executor.execute(
            lambda _ctx: calls.append(1) or result(), deadline_seconds=5,
            operation_policy=OperationRetryPolicy(RetrySafety.IDEMPOTENT),
        )
        self.assertEqual(outcome.dispatch.outcome, "success")
        self.assertEqual(outcome.attempts, 1)
        self.assertEqual(len(calls), 1)

    def test_retryable_transient_result_retries_for_idempotent_operation(self):
        calls = []
        sequence = iter([
            result("unavailable", retryable=True, error_code="upstream_503"),
            result("rate_limited", retryable=True, error_code="provider_429"),
            result("success"),
        ])
        outcome = self.executor.execute(
            lambda _ctx: calls.append(1) or next(sequence), deadline_seconds=5,
            operation_policy=OperationRetryPolicy(RetrySafety.IDEMPOTENT),
        )
        self.assertEqual(outcome.dispatch.outcome, "success")
        self.assertEqual(outcome.attempts, 3)
        self.assertEqual(len(calls), 3)
        self.assertEqual(self.clock.sleeps, [0.2, 0.4])
        self.assertEqual(outcome.retry_reasons, ("upstream_503", "provider_429"))

    def test_default_policy_never_retries_even_if_adapter_marks_retryable(self):
        calls = []
        outcome = self.executor.execute(
            lambda _ctx: calls.append(1) or result("unavailable", retryable=True),
            deadline_seconds=5,
        )
        self.assertEqual(outcome.attempts, 1)
        self.assertEqual(len(calls), 1)
        self.assertEqual(outcome.dispatch.metadata["retry_safety"], "never")

    def test_non_retryable_outcome_is_never_retried(self):
        calls = []
        outcome = self.executor.execute(
            lambda _ctx: calls.append(1) or result("invalid", retryable=True, error_code="bad_input"),
            deadline_seconds=5,
            operation_policy=OperationRetryPolicy(RetrySafety.IDEMPOTENT),
        )
        self.assertEqual(outcome.attempts, 1)
        self.assertEqual(len(calls), 1)

    def test_conflict_is_never_retried(self):
        calls = []
        outcome = self.executor.execute(
            lambda _ctx: calls.append(1) or result("conflict", retryable=True, error_code="conflict"),
            deadline_seconds=5,
            operation_policy=OperationRetryPolicy(RetrySafety.IDEMPOTENT),
        )
        self.assertEqual(outcome.attempts, 1)

    def test_attempt_ceiling_includes_initial_attempt(self):
        calls = []
        outcome = self.executor.execute(
            lambda _ctx: calls.append(1) or result("unavailable", retryable=True),
            deadline_seconds=5,
            operation_policy=OperationRetryPolicy(RetrySafety.IDEMPOTENT),
        )
        self.assertEqual(outcome.attempts, 3)
        self.assertEqual(len(calls), 3)

    def test_idempotency_key_is_required_before_callback(self):
        called = []
        with self.assertRaises(ValueError):
            self.executor.execute(
                lambda _ctx: called.append(True) or result("success"),
                deadline_seconds=5,
                operation_policy=OperationRetryPolicy(RetrySafety.IDEMPOTENCY_KEY_REQUIRED),
            )
        self.assertEqual(called, [])

    def test_same_idempotency_key_is_provided_to_every_attempt(self):
        seen = []
        policy = OperationRetryPolicy(
            RetrySafety.IDEMPOTENCY_KEY_REQUIRED, idempotency_key="order-123-attempt-group"
        )
        sequence = iter([
            result("unavailable", retryable=True, error_code="temporary"),
            result("success"),
        ])
        outcome = self.executor.execute(
            lambda ctx: seen.append(ctx.idempotency_key) or next(sequence),
            deadline_seconds=5, operation_policy=policy,
        )
        self.assertEqual(outcome.attempts, 2)
        self.assertEqual(seen, ["order-123-attempt-group", "order-123-attempt-group"])
        self.assertTrue(outcome.dispatch.metadata["idempotency_key_used"])

    def test_operation_policy_rejects_inconsistent_key_configuration(self):
        for kwargs in (
            {"safety": RetrySafety.IDEMPOTENT, "idempotency_key": "key"},
            {"safety": RetrySafety.NEVER, "idempotency_key": "key"},
            {"safety": RetrySafety.IDEMPOTENCY_KEY_REQUIRED},
            {"safety": "idempotent"},
            {"safety": RetrySafety.IDEMPOTENCY_KEY_REQUIRED, "idempotency_key": "  "},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                OperationRetryPolicy(**kwargs)

    def test_deadline_prevents_first_attempt(self):
        clock_values = iter((0.0, 2.0, 2.0))
        executor = ResilienceExecutor(
            RetryPolicy(max_attempts=3, base_delay_seconds=0.2, max_delay_seconds=0.5),
            clock=lambda: next(clock_values),
            sleeper=lambda _seconds: self.fail("must not sleep"),
            random_value=lambda: 1.0,
        )
        outcome = executor.execute(
            lambda _ctx: self.fail("must not execute"), deadline_seconds=1,
            operation_policy=OperationRetryPolicy(RetrySafety.IDEMPOTENT),
        )
        self.assertTrue(outcome.deadline_exceeded)
        self.assertEqual(outcome.attempts, 0)

    def test_deadline_clips_retry_before_sleep(self):
        calls = []
        outcome = self.executor.execute(
            lambda _ctx: calls.append(1) or result("unavailable", retryable=True),
            deadline_seconds=0.1,
            operation_policy=OperationRetryPolicy(RetrySafety.IDEMPOTENT),
        )
        self.assertTrue(outcome.deadline_exceeded)
        self.assertEqual(outcome.attempts, 1)
        self.assertEqual(len(calls), 1)
        self.assertEqual(self.clock.sleeps, [])

    def test_callback_returning_after_deadline_is_discarded(self):
        def slow_call(_ctx):
            self.clock.advance(2)
            return result()
        outcome = self.executor.execute(
            slow_call, deadline_seconds=1,
            operation_policy=OperationRetryPolicy(RetrySafety.IDEMPOTENT),
        )
        self.assertTrue(outcome.deadline_exceeded)
        self.assertFalse(outcome.dispatch.metadata["cancellation_guaranteed"])

    def test_unexpected_callback_exception_is_sanitized_and_not_retried(self):
        def fail(_ctx):
            raise RuntimeError("private response and secret")
        outcome = self.executor.execute(
            fail, deadline_seconds=5,
            operation_policy=OperationRetryPolicy(RetrySafety.IDEMPOTENT),
        )
        self.assertEqual(outcome.dispatch.error_code, "resilience_execution_failed")
        self.assertEqual(outcome.attempts, 1)
        self.assertNotIn("private response", str(outcome.dispatch))

    def test_invalid_deadline_rejected(self):
        for value in (0, -1, float("inf"), float("nan")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.executor.execute(lambda _ctx: result(), deadline_seconds=value)

    def test_retry_policy_rejects_unsafe_configuration(self):
        for kwargs in (
            {"max_attempts": 4}, {"max_attempts": 0},
            {"base_delay_seconds": -1},
            {"max_delay_seconds": 0.1, "base_delay_seconds": 0.2},
            {"retryable_outcomes": frozenset({"conflict"})},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                RetryPolicy(**kwargs)


if __name__ == "__main__":
    unittest.main()
