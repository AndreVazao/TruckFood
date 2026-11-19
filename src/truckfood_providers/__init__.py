"""TruckFood provider runtime (stdlib-only foundation)."""
from .adapters import (
    AdapterDispatcher,
    AdapterRegistrationError,
    AdapterResult,
    DispatchResult,
    ProviderAdapter,
)
from .circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerPolicy,
    CircuitSnapshot,
    CircuitState,
)
from .quota import (
    QuotaError,
    QuotaExceeded,
    QuotaManager,
    QuotaPolicy,
    QuotaPolicyMissing,
    QuotaReservation,
    QuotaReservationConflict,
    QuotaReservationNotFound,
    QuotaSnapshot,
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
    "CircuitBreaker",
    "CircuitBreakerPolicy",
    "CircuitSnapshot",
    "CircuitState",
    "DispatchResult",
    "ExecutionContext",
    "OperationRetryPolicy",
    "ProviderAdapter",
    "QuotaError",
    "QuotaExceeded",
    "QuotaManager",
    "QuotaPolicy",
    "QuotaPolicyMissing",
    "QuotaReservation",
    "QuotaReservationConflict",
    "QuotaReservationNotFound",
    "QuotaSnapshot",
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
