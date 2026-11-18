"""TruckFood provider runtime (stdlib-only foundation)."""
from .adapters import (
    AdapterDispatcher,
    AdapterRegistrationError,
    AdapterResult,
    DispatchResult,
    ProviderAdapter,
)
from .registry import (
    RegistryError,
    SelectionDecision,
    SelectionRequest,
    load_registry,
    select_provider,
)
from .resilience import (
    ExecutionContext,
    OperationRetryPolicy,
    ResilienceExecutor,
    ResilienceResult,
    RetryPolicy,
    RetrySafety,
)

__all__ = [
    "AdapterDispatcher",
    "AdapterRegistrationError",
    "AdapterResult",
    "DispatchResult",
    "ExecutionContext",
    "OperationRetryPolicy",
    "ProviderAdapter",
    "RegistryError",
    "ResilienceExecutor",
    "ResilienceResult",
    "RetryPolicy",
    "RetrySafety",
    "SelectionDecision",
    "SelectionRequest",
    "load_registry",
    "select_provider",
]
