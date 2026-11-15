"""Bounded, deterministic retry orchestration for trusted provider dispatch.

This module enforces attempt budgets and cooperative deadlines around a synchronous
callable. It cannot interrupt a blocked adapter call; transport-level deadlines must
be enforced by each adapter's underlying client.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
import math
import random
import time
from typing import Callable, Mapping

from .adapters import DispatchResult


@dataclass(frozen=True)
class RetryPolicy:
    """Conservative retry limits. max_attempts includes the initial attempt."""

    max_attempts: int = 3
    base_delay_seconds: float = 0.25
    max_delay_seconds: float = 2.0
    retryable_outcomes: frozenset[str] = frozenset({"unavailable", "rate_limited"})

    def __post_init__(self) -> None:
        if not 1 <= self.max_attempts <= 3:
            raise ValueError("max_attempts must be between 1 and 3")
        if not math.isfinite(self.base_delay_seconds) or self.base_delay_seconds < 0:
            raise ValueError("base_delay_seconds must be finite and non-negative")
        if not math.isfinite(self.max_delay_seconds) or self.max_delay_seconds < 0:
            raise ValueError("max_delay_seconds must be finite and non-negative")
        if self.max_delay_seconds < self.base_delay_seconds:
            raise ValueError("max_delay_seconds must be >= base_delay_seconds")
        if not self.retryable_outcomes <= {"unavailable", "rate_limited"}:
            raise ValueError("retryable_outcomes contains a non-transient outcome")


@dataclass(frozen=True)
class ResilienceResult:
    """Result plus safe orchestration metadata."""

    dispatch: DispatchResult
    attempts: int
    elapsed_seconds: float
    deadline_exceeded: bool = False
    retry_reasons: tuple[str, ...] = ()


class ResilienceExecutor:
    """Apply bounded retries and a cooperative total execution budget.

    The execute callback is normally AdapterDispatcher.dispatch. A synchronous
    callback that blocks cannot be forcibly cancelled by this class. If it returns
    after the deadline, the result is discarded and a timeout outcome is returned.
    """

    def __init__(
        self,
        policy: RetryPolicy | None = None,
        *,
        clock: Callable[[], float] = time.monotonic,
        sleeper: Callable[[float], None] = time.sleep,
        random_value: Callable[[], float] = random.random,
    ) -> None:
        self.policy = policy or RetryPolicy()
        self._clock = clock
        self._sleep = sleeper
        self._random = random_value

    def execute(
        self,
        execute: Callable[[], DispatchResult],
        *,
        deadline_seconds: float,
    ) -> ResilienceResult:
        if not math.isfinite(deadline_seconds) or deadline_seconds <= 0:
            raise ValueError("deadline_seconds must be finite and > 0")

        started = self._clock()
        deadline = started + deadline_seconds
        attempts = 0
        reasons: list[str] = []
        last_result: DispatchResult | None = None

        while attempts < self.policy.max_attempts:
            remaining = deadline - self._clock()
            if remaining <= 0:
                return self._deadline_result(attempts, started, reasons)

            attempts += 1
            try:
                result = execute()
            except Exception:
                # The dispatcher normally normalizes adapter exceptions. This guard
                # prevents an unexpected callback exception from leaking details.
                result = DispatchResult(
                    outcome="unavailable",
                    error_code="resilience_execution_failed",
                    retryable=False,
                )

            elapsed = max(0.0, self._clock() - started)
            if self._clock() >= deadline:
                return self._deadline_result(attempts, started, reasons)

            if not isinstance(result, DispatchResult):
                result = DispatchResult(
                    outcome="invalid",
                    error_code="invalid_dispatch_result",
                    retryable=False,
                )
            last_result = result

            can_retry = (
                result.retryable
                and result.outcome in self.policy.retryable_outcomes
                and attempts < self.policy.max_attempts
            )
            if not can_retry:
                return ResilienceResult(
                    dispatch=self._with_metadata(result, attempts, elapsed, reasons),
                    attempts=attempts,
                    elapsed_seconds=elapsed,
                    retry_reasons=tuple(reasons),
                )

            reasons.append(result.error_code or result.outcome)
            ceiling = min(
                self.policy.max_delay_seconds,
                self.policy.base_delay_seconds * (2 ** (attempts - 1)),
            )
            sample = self._random()
            if not 0.0 <= sample <= 1.0:
                raise ValueError("random_value must return a value in [0, 1]")
            delay = ceiling * sample
            remaining = deadline - self._clock()
            if delay >= remaining:
                return self._deadline_result(attempts, started, reasons)
            if delay > 0:
                self._sleep(delay)

        # The loop can only exhaust after a non-retryable result or the attempt cap.
        if last_result is None:
            return self._deadline_result(attempts, started, reasons)
        elapsed = max(0.0, self._clock() - started)
        return ResilienceResult(
            dispatch=self._with_metadata(last_result, attempts, elapsed, reasons),
            attempts=attempts,
            elapsed_seconds=elapsed,
            retry_reasons=tuple(reasons),
        )

    @staticmethod
    def _with_metadata(
        result: DispatchResult, attempts: int, elapsed: float, reasons: list[str]
    ) -> DispatchResult:
        metadata = dict(result.metadata)
        metadata.update({
            "attempt_count": attempts,
            "elapsed_seconds": round(elapsed, 6),
            "retry_reasons": list(reasons),
        })
        return replace(result, metadata=metadata)

    def _deadline_result(
        self, attempts: int, started: float, reasons: list[str]
    ) -> ResilienceResult:
        elapsed = max(0.0, self._clock() - started)
        result = DispatchResult(
            outcome="unavailable",
            error_code="execution_deadline_exceeded",
            retryable=False,
            metadata={
                "attempt_count": attempts,
                "elapsed_seconds": round(elapsed, 6),
                "retry_reasons": list(reasons),
                "deadline_exceeded": True,
                "cancellation_guaranteed": False,
            },
        )
        return ResilienceResult(
            dispatch=result,
            attempts=attempts,
            elapsed_seconds=elapsed,
            deadline_exceeded=True,
            retry_reasons=tuple(reasons),
        )
