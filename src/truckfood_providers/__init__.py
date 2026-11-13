"""TruckFood provider registry runtime (stdlib-only foundation)."""
from .registry import (
    RegistryError,
    SelectionRequest,
    SelectionDecision,
    load_registry,
    select_provider,
)

__all__ = [
    "RegistryError",
    "SelectionRequest",
    "SelectionDecision",
    "load_registry",
    "select_provider",
]
