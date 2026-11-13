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
    "ProviderAdapter",
    "RegistryError",
    "SelectionRequest",
    "SelectionDecision",
    "load_registry",
    "select_provider",
]
