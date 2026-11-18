"""Bounded retries with explicit operation-level retry safety."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
import math
import random
import time
from typing import Callable, Mapping

from .adapters import DispatchResult


class RetrySafety(str, Enum):
    """How an operation protects side effects when a request is repeated."""

    NEVER = "never"
    IDEMPOTENT = "idempotent"
    IDEMPOTENCY_KEY_REQUIRED = "idempotency_key_required"


@dataclass(frozen=True)
class OperationRetryPolicy:
    """Per-operation declaration; conservative by default."""

    safety: RetrySafety = RetrySafety.NEVER
    idempotency_key: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.safety, RetrySafety):
            raise ValueError("safety must be a RetrySafety value")
        if self.idempotency_key is not None:
            if not isinstance(self.idempotency_key, str) or not self.idempotency_key.strip():
                raise ValueError("idempotency_key must be a non-empty string")
        if self.safety is RetrySafety.IDEMPOTENT and self.idempotency_key is not None:
            raise ValueError("idempotent operations must not supply an idempotency_key")
        if self.safety is RetrySafety.IDEMPOTENCY_KEY_REQUIRED and self.idempotency_key is None:
            raise ValueError("idempotency_key is required by this operation policy")
        if self.safety is not RetrySafety.IDEMPOTENCY_KEY_REQUIRED and self.idempotency_key is not None:
            raise ValueError("idempotency_key is only valid when required by the operation")


@dataclass(frozen=True)
class ExecutionContext:
    """Immutable context passed to every attempt; key remains stable across retries."""

    retry_safety: RetrySafety
    idempotency_key: str | None
    deadline_monotonic: float


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
    """Apply bounded retries only when the operation contract permits repetition.

    The callback receives the same immutable ExecutionContext on every attempt.
    For idempotency-key operations it MUST forward context.idempotency_key unchanged
    to the provider's idempotency mechanism. This class cannot prove remote support.
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
        execute: Callable[[ExecutionContext], DispatchResult],
        *,
        deadline_seconds: float,
        operation_policy: OperationRetryPolicy | None = None,
    ) -> ResilienceResult:
        if not math.isfinite(deadline_seconds) or deadline_seconds <= 0:
            raise ValueError("deadline_seconds must be finite and > 0")
        operation = operation_policy or OperationRetryPolicy()
        started = self._clock()
        deadline = started + deadline_seconds
        context = ExecutionContext(
            retry_safety=operation.safety,
            idempotency_key=operation.idempotency_key,
            deadline_monotonic=deadline,
        )
        attempts = 0
        reasons: list[str] = []
        last_result: DispatchResult | None = None

        while attempts < self.policy.max_attempts:
            remaining = deadline - self._clock()
            if remaining <= 0:
                return self._deadline_result(attempts, started, reasons)

            attempts += 1
            try:
                result = execute(context)
            except Exception:
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
                operation.safety is not RetrySafety.NEVER
                and result.retryable
                and result.outcome in self.policy.retryable_outcomes
                and attempts < self.policy.max_attempts
            )
            if not can_retry:
                return ResilienceResult(
                    dispatch=self._with_metadata(result, attempts, elapsed, reasons, operation),
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

        if last_result is None:
            return self._deadline_result(attempts, started, reasons)
        elapsed = max(0.0, self._clock() - started)
        return ResilienceResult(
            dispatch=self._with_metadata(last_result, attempts, elapsed, reasons, operation),
            attempts=attempts,
            elapsed_seconds=elapsed,
            retry_reasons=tuple(reasons),
        )

    @staticmethod
    def _with_metadata(
        result: DispatchResult,
        attempts: int,
        elapsed: float,
        reasons: list[str],
        operation: OperationRetryPolicy,
    ) -> DispatchResult:
        metadata = dict(result.metadata)
        metadata.update({
            "attempt_count": attempts,
            "elapsed_seconds": round(elapsed, 6),
            "retry_reasons": list(reasons),
            "retry_safety": operation.safety.value,
            "idempotency_key_used": operation.safety is RetrySafety.IDEMPOTENCY_KEY_REQUIRED,
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
