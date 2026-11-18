"""Thread-safe, process-local circuit breaker for trusted provider operations."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import math
import threading
import time
from typing import Callable

from .adapters import DispatchResult


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass(frozen=True)
class CircuitBreakerPolicy:
    """Conservative breaker settings; failures are consecutive per provider operation."""

    failure_threshold: int = 3
    recovery_timeout_seconds: float = 30.0
    half_open_max_calls: int = 1
    qualifying_outcomes: frozenset[str] = frozenset({"unavailable"})
    max_circuits: int = 1024

    def __post_init__(self) -> None:
        if self.failure_threshold < 1:
            raise ValueError("failure_threshold must be >= 1")
        if not math.isfinite(self.recovery_timeout_seconds) or self.recovery_timeout_seconds <= 0:
            raise ValueError("recovery_timeout_seconds must be finite and > 0")
        if self.half_open_max_calls < 1:
            raise ValueError("half_open_max_calls must be >= 1")
        if self.max_circuits < 1:
            raise ValueError("max_circuits must be >= 1")
        if not self.qualifying_outcomes or not self.qualifying_outcomes <= {"unavailable"}:
            raise ValueError("qualifying_outcomes may contain only unavailable")


@dataclass
class _Circuit:
    state: CircuitState = CircuitState.CLOSED
    consecutive_failures: int = 0
    opened_until: float = 0.0
    half_open_in_flight: int = 0
    generation: int = 0
    last_access: float = 0.0


@dataclass(frozen=True)
class CircuitSnapshot:
    provider_id: str
    operation: str
    state: CircuitState
    consecutive_failures: int
    retry_after_seconds: float
    half_open_in_flight: int


class CircuitBreaker:
    """Guard provider calls by (provider_id, operation).

    This implementation is process-local. It is suitable for deterministic tests
    and single-process deployments only; multi-worker production enforcement needs
    a shared atomic state store.
    """

    def __init__(
        self,
        policy: CircuitBreakerPolicy | None = None,
        *,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.policy = policy or CircuitBreakerPolicy()
        self._clock = clock
        self._lock = threading.RLock()
        self._circuits: dict[tuple[str, str], _Circuit] = {}

    def execute(
        self,
        provider_id: str,
        operation: str,
        callback: Callable[[], DispatchResult],
    ) -> DispatchResult:
        if not isinstance(provider_id, str) or not provider_id.strip():
            raise ValueError("provider_id must be a non-empty string")
        if not isinstance(operation, str) or not operation.strip():
            raise ValueError("operation must be a non-empty string")
        if not callable(callback):
            raise ValueError("callback must be callable")

        key = (provider_id, operation)
        now = self._clock()
        with self._lock:
            circuit = self._get_or_create(key, now)
            if circuit is None:
                return DispatchResult(
                    outcome="unavailable",
                    error_code="circuit_capacity_exceeded",
                    retryable=False,
                    metadata={"provider_invoked": False},
                )
            circuit.last_access = now
            if circuit.state is CircuitState.OPEN:
                if now < circuit.opened_until:
                    return self._rejected(circuit, now)
                circuit.state = CircuitState.HALF_OPEN
                circuit.half_open_in_flight = 0
                circuit.generation += 1

            is_probe = circuit.state is CircuitState.HALF_OPEN
            if is_probe and circuit.half_open_in_flight >= self.policy.half_open_max_calls:
                return self._rejected(circuit, now)

            if is_probe:
                circuit.half_open_in_flight += 1
            generation = circuit.generation

        try:
            result = callback()
        except Exception:
            result = DispatchResult(
                outcome="unavailable",
                error_code="circuit_execution_failed",
                retryable=False,
            )
        if not isinstance(result, DispatchResult):
            result = DispatchResult(
                outcome="invalid",
                error_code="invalid_dispatch_result",
                retryable=False,
            )

        completed_at = self._clock()
        with self._lock:
            current = self._circuits[key]
            # A result from an older closed/open generation must not overwrite a
            # newer state transition made by another concurrent request.
            if generation == current.generation:
                if is_probe:
                    current.half_open_in_flight = max(0, current.half_open_in_flight - 1)
                    if result.outcome == "unavailable":
                        self._open(current, completed_at)
                    else:
                        current.state = CircuitState.CLOSED
                        current.consecutive_failures = 0
                        current.opened_until = 0.0
                        current.generation += 1
                elif current.state is CircuitState.CLOSED:
                    if result.outcome in self.policy.qualifying_outcomes:
                        current.consecutive_failures += 1
                        if current.consecutive_failures >= self.policy.failure_threshold:
                            self._open(current, completed_at)
                    elif result.outcome in {"success", "empty", "partial"}:
                        current.consecutive_failures = 0

        metadata = dict(result.metadata)
        metadata.update({
            "circuit_provider_id": provider_id,
            "circuit_operation": operation,
            "circuit_probe": is_probe,
        })
        from dataclasses import replace
        return replace(result, metadata=metadata)

    def snapshot(self, provider_id: str, operation: str) -> CircuitSnapshot:
        key = (provider_id, operation)
        now = self._clock()
        with self._lock:
            circuit = self._get_or_create(key, now)
            if circuit is None:
                raise RuntimeError("Circuit state capacity exhausted; no closed entry can be evicted")
            circuit.last_access = now
            if circuit.state is CircuitState.OPEN and now >= circuit.opened_until:
                circuit.state = CircuitState.HALF_OPEN
                circuit.half_open_in_flight = 0
                circuit.generation += 1
            return CircuitSnapshot(
                provider_id=provider_id,
                operation=operation,
                state=circuit.state,
                consecutive_failures=circuit.consecutive_failures,
                retry_after_seconds=max(0.0, circuit.opened_until - now)
                if circuit.state is CircuitState.OPEN else 0.0,
                half_open_in_flight=circuit.half_open_in_flight,
            )


    def _get_or_create(self, key: tuple[str, str], now: float) -> _Circuit | None:
        circuit = self._circuits.get(key)
        if circuit is not None:
            return circuit
        if len(self._circuits) >= self.policy.max_circuits:
            evictable = [
                (item.last_access, existing_key)
                for existing_key, item in self._circuits.items()
                if item.state is CircuitState.CLOSED and item.half_open_in_flight == 0
            ]
            if not evictable:
                return None
            _, oldest_key = min(evictable)
            del self._circuits[oldest_key]
        circuit = _Circuit(last_access=now)
        self._circuits[key] = circuit
        return circuit

    def _open(self, circuit: _Circuit, now: float) -> None:
        circuit.state = CircuitState.OPEN
        circuit.opened_until = now + self.policy.recovery_timeout_seconds
        circuit.half_open_in_flight = 0
        circuit.generation += 1

    @staticmethod
    def _rejected(circuit: _Circuit, now: float) -> DispatchResult:
        return DispatchResult(
            outcome="unavailable",
            error_code="circuit_open",
            retryable=False,
            metadata={
                "circuit_state": circuit.state.value,
                "circuit_retry_after_seconds": round(max(0.0, circuit.opened_until - now), 6),
                "provider_invoked": False,
            },
        )
