"""TruckFood provider runtime (stdlib-only foundation)."""
from .adapters import (
    AdapterDispatcher,
    AdapterRegistrationError,
    AdapterResult,
    DispatchResult,
    ProviderAdapter,
)
from .resilience import ResilienceExecutor, ResilienceResult, RetryPolicy\nfrom .registry import (
    RegistryError,
    SelectionRequest,
    SelectionDecision,
    load_registry,
    select_provider,
)

__all__ = [
    "AdapterDispatcher",
    "AdapterRegistrationError",
    "AdapterResult",
    "DispatchResult",
    "ProviderAdapter",\n    "ResilienceExecutor",\n    "ResilienceResult",\n    "RetryPolicy",
    "RegistryError",
    "SelectionRequest",
    "SelectionDecision",
    "load_registry",
    "select_provider",
]
