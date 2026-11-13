"""Trusted in-process provider adapter registration and dispatch.

Registry manifests are untrusted data: they never control imports or code loading.
Only adapter instances explicitly registered by application code can execute.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol

from .registry import SelectionDecision


NORMALIZED_OUTCOMES = frozenset({
    "success", "empty", "partial", "unsupported", "unavailable",
    "rate_limited", "invalid", "conflict",
})


@dataclass(frozen=True)
class AdapterResult:
    """Provider-independent result returned by a trusted adapter."""
    outcome: str
    data: Any = None
    error_code: str | None = None
    retryable: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.outcome not in NORMALIZED_OUTCOMES:
            raise ValueError(f"Unsupported normalized outcome: {self.outcome}")
        if self.outcome in {"unsupported", "unavailable", "rate_limited", "invalid", "conflict"}:
            if not self.error_code:
                raise ValueError(f"{self.outcome} requires a stable error_code")
        if self.outcome in {"success", "empty", "partial"} and self.error_code is not None:
            raise ValueError(f"{self.outcome} must not carry an error_code")


class ProviderAdapter(Protocol):
    """Minimal synchronous adapter port; implementations are trusted app code."""
    def execute(self, operation: str, payload: Mapping[str, Any]) -> AdapterResult:
        ...


@dataclass(frozen=True)
class RegisteredAdapter:
    adapter_id: str
    adapter_version: str
    operations: frozenset[str]
    instance: ProviderAdapter


@dataclass(frozen=True)
class DispatchResult:
    outcome: str
    data: Any = None
    error_code: str | None = None
    retryable: bool = False
    adapter_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


class AdapterRegistrationError(ValueError):
    """Raised when trusted application code registers an invalid adapter."""


class AdapterDispatcher:
    """Dispatch only to an explicitly registered adapter matching a selection.

    No dynamic import, network access, retry, failover, timeout, quota accounting
    or circuit-breaker management is performed here.
    """
    def __init__(self) -> None:
        self._adapters: dict[tuple[str, str], RegisteredAdapter] = {}

    def register(
        self, *, adapter_id: str, adapter_version: str,
        operations: set[str] | frozenset[str], instance: ProviderAdapter,
    ) -> None:
        if not adapter_id or not adapter_version:
            raise AdapterRegistrationError("adapter_id and adapter_version are required")
        normalized_operations = frozenset(operations)
        if not normalized_operations or any(not item for item in normalized_operations):
            raise AdapterRegistrationError("At least one non-empty operation is required")
        if not callable(getattr(instance, "execute", None)):
            raise AdapterRegistrationError("Adapter instance must implement execute()")
        key = (adapter_id, adapter_version)
        if key in self._adapters:
            raise AdapterRegistrationError("Adapter identity/version is already registered")
        self._adapters[key] = RegisteredAdapter(
            adapter_id, adapter_version, normalized_operations, instance
        )

    def dispatch(
        self, decision: SelectionDecision, *, operation: str,
        payload: Mapping[str, Any],
    ) -> DispatchResult:
        if not decision.selected or decision.selected_entry is None:
            return DispatchResult(
                outcome="unavailable", error_code="provider_not_selected",
                metadata={"selection_reason": decision.reason},
            )

        entry = decision.selected_entry
        adapter_id = entry.get("adapter_id")
        adapter_version = entry.get("adapter_version")
        declaration = decision.capability_declaration or {}
        declared = any(
            item.get("operation") == operation and item.get("support_state") == "supported"
            for item in declaration.get("operations", [])
        )
        if not declared:
            return DispatchResult(
                outcome="unsupported",
                error_code="operation_not_declared_by_selected_provider",
                adapter_id=adapter_id,
            )

        registered = self._adapters.get((adapter_id, adapter_version))
        if registered is None:
            return DispatchResult(
                outcome="unavailable", error_code="trusted_adapter_not_registered",
                adapter_id=adapter_id,
            )
        if operation not in registered.operations:
            return DispatchResult(
                outcome="unsupported", error_code="operation_not_implemented_by_adapter",
                adapter_id=adapter_id,
            )

        try:
            result = registered.instance.execute(operation, payload)
        except Exception:
            # Never expose provider exception text, credentials or raw response bodies.
            return DispatchResult(
                outcome="unavailable", error_code="adapter_execution_failed",
                retryable=False, adapter_id=adapter_id,
            )

        if not isinstance(result, AdapterResult):
            return DispatchResult(
                outcome="invalid", error_code="adapter_returned_invalid_result",
                adapter_id=adapter_id,
            )
        return DispatchResult(
            outcome=result.outcome, data=result.data, error_code=result.error_code,
            retryable=result.retryable, adapter_id=adapter_id,
            metadata=dict(result.metadata),
        )
