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
from .resilience import ResilienceExecutor, ResilienceResult, RetryPolicy

__all__ = [
    "AdapterDispatcher",
    "AdapterRegistrationError",
    "AdapterResult",
    "DispatchResult",
    "ProviderAdapter",
    "RegistryError",
    "ResilienceExecutor",
    "ResilienceResult",
    "RetryPolicy",
    "SelectionDecision",
    "SelectionRequest",
    "load_registry",
    "select_provider",
]
