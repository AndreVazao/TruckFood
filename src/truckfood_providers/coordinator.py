"""Central coordination for provider selection, quota, breaker and retries."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .adapters import AdapterDispatcher, DispatchResult
from .circuit_breaker import CircuitBreaker
from .quota import QuotaManager
from .registry import SelectionDecision
from .resilience import OperationRetryPolicy, ResilienceExecutor


@dataclass(frozen=True)
class CoordinatorResult:
    dispatch: DispatchResult
    attempts: int
    quota_reservation_id: str | None
    quota_state: str
    provider_invocation_attempted: bool


class ProviderExecutionCoordinator:
    """Fail-closed in-process coordinator; quota/breaker remain local components.

    Quota reservations are settled conservatively at the reserved amount whenever
    adapter invocation may have occurred. A result cannot prove zero provider use.
    """

    def __init__(
        self,
        *,
        dispatcher: AdapterDispatcher,
        resilience: ResilienceExecutor,
        circuit_breaker: CircuitBreaker,
        quota_manager: QuotaManager | None = None,
    ) -> None:
        self.dispatcher = dispatcher
        self.resilience = resilience
        self.circuit_breaker = circuit_breaker
        self.quota_manager = quota_manager

    def execute(
        self,
        decision: SelectionDecision,
        *,
        operation: str,
        payload: Mapping[str, Any],
        deadline_seconds: float,
        retry_policy: OperationRetryPolicy | None = None,
        quota_units: int = 1,
        reservation_id: str | None = None,
    ) -> CoordinatorResult:
        selected = getattr(decision, "selected_entry", None)
        if not getattr(decision, "selected", False) or not isinstance(selected, Mapping):
            return self._invalid("provider_selection_invalid")
        provider_id = selected.get("provider_id")
        if not isinstance(provider_id, str) or not provider_id.strip():
            return self._invalid("selected_provider_identity_invalid")
        if not isinstance(operation, str) or not operation.strip() or not isinstance(payload, Mapping):
            return self._invalid("execution_request_invalid")

        reservation = None
        if self.quota_manager is not None:
            if not isinstance(reservation_id, str) or not reservation_id.strip():
                return self._invalid("quota_reservation_id_required")
            try:
                reservation = self.quota_manager.reserve(
                    provider_id, operation, units=quota_units, reservation_id=reservation_id
                )
            except Exception:
                return CoordinatorResult(
                    DispatchResult(outcome="unavailable", error_code="quota_admission_denied",
                                  metadata={"provider_invoked": False}),
                    0, reservation_id, "denied", False,
                )

        invocation_attempted = False

        def attempt(_context: Any) -> DispatchResult:
            nonlocal invocation_attempted

            def call_dispatch() -> DispatchResult:
                nonlocal invocation_attempted
                result = self.dispatcher.dispatch(decision, operation=operation, payload=payload)
                invocation_attempted = invocation_attempted or result.metadata.get("provider_invoked") is True
                return result

            return self.circuit_breaker.execute(provider_id, operation, call_dispatch)

        try:
            result = self.resilience.execute(
                attempt, deadline_seconds=deadline_seconds,
                operation_policy=retry_policy or OperationRetryPolicy(),
            )
            dispatch = result.dispatch
            attempts = result.attempts
        except Exception:
            dispatch = DispatchResult(outcome="invalid", error_code="coordinator_execution_invalid")
            attempts = 0

        quota_state = "not_configured"
        if reservation is not None:
            try:
                if invocation_attempted:
                    # Conservative: uncertain outcomes retain the full reserved amount.
                    self.quota_manager.settle(reservation.reservation_id, actual_units=reservation.units)
                    quota_state = "settled_conservatively"
                else:
                    self.quota_manager.release(reservation.reservation_id)
                    quota_state = "released_confirmed_no_invocation"
            except Exception:
                quota_state = "reconciliation_required"
                metadata = dict(dispatch.metadata)
                metadata["quota_reconciliation_required"] = True
                dispatch = DispatchResult(
                    outcome=dispatch.outcome, data=dispatch.data, error_code=dispatch.error_code,
                    retryable=dispatch.retryable, adapter_id=dispatch.adapter_id, metadata=metadata,
                )

        metadata = dict(dispatch.metadata)
        metadata.update({
            "coordinator_attempts": attempts,
            "provider_invocation_attempted": invocation_attempted,
            "quota_state": quota_state,
        })
        dispatch = DispatchResult(
            outcome=dispatch.outcome, data=dispatch.data, error_code=dispatch.error_code,
            retryable=dispatch.retryable, adapter_id=dispatch.adapter_id, metadata=metadata,
        )
        return CoordinatorResult(dispatch, attempts, reservation.reservation_id if reservation else None,
                                quota_state, invocation_attempted)

    @staticmethod
    def _invalid(code: str) -> CoordinatorResult:
        return CoordinatorResult(
            DispatchResult(outcome="invalid", error_code=code, metadata={"provider_invoked": False}),
            0, None, "not_reserved", False,
        )
