"""Atomic process-local quota reservations for provider operations."""
from __future__ import annotations

from dataclasses import dataclass
import math
import threading
import time
from typing import Callable, Mapping


class QuotaError(RuntimeError):
    """Base class for fail-closed quota errors."""


class QuotaPolicyMissing(QuotaError):
    """No explicit quota policy exists for the requested provider operation."""


class QuotaExceeded(QuotaError):
    """The requested reservation would exceed the configured window budget."""

    def __init__(self, message: str, *, retry_after_seconds: float) -> None:
        super().__init__(message)
        self.retry_after_seconds = max(0.0, retry_after_seconds)


class QuotaReservationConflict(QuotaError):
    """A reservation identifier was reused with incompatible or terminal state."""


class QuotaReservationNotFound(QuotaError):
    """The reservation identifier is unknown or no longer retained."""


@dataclass(frozen=True)
class QuotaPolicy:
    """Maximum units in a fixed window; units are caller-defined cost units."""

    max_units: int
    window_seconds: float = 60.0
    reservation_ttl_seconds: float = 30.0

    def __post_init__(self) -> None:
        if isinstance(self.max_units, bool) or not isinstance(self.max_units, int) or self.max_units < 1:
            raise ValueError("max_units must be a positive integer")
        if not math.isfinite(self.window_seconds) or self.window_seconds <= 0:
            raise ValueError("window_seconds must be finite and > 0")
        if not math.isfinite(self.reservation_ttl_seconds) or self.reservation_ttl_seconds <= 0:
            raise ValueError("reservation_ttl_seconds must be finite and > 0")


@dataclass(frozen=True)
class QuotaReservation:
    reservation_id: str
    provider_id: str
    operation: str
    units: int
    window_id: int
    expires_at: float


@dataclass(frozen=True)
class QuotaSnapshot:
    provider_id: str
    operation: str
    window_id: int
    consumed_units: int
    reserved_units: int
    remaining_units: int
    reset_in_seconds: float


@dataclass
class _Window:
    consumed: int = 0
    reserved: int = 0


@dataclass
class _ReservationRecord:
    reservation: QuotaReservation
    state: str = "reserved"


class QuotaManager:
    """Thread-safe quota manager with explicit process-local enforcement.

    Policies are keyed by (provider_id, operation). A reservation must be
    acquired before invoking a potentially billable provider operation, then
    settled with actual units or released. This in-memory manager is not shared
    between processes/workers and is NOT production multi-worker enforcement.
    """

    def __init__(
        self,
        policies: Mapping[tuple[str, str], QuotaPolicy],
        *,
        clock: Callable[[], float] = time.monotonic,
        max_reservations: int = 4096,
    ) -> None:
        if not policies:
            raise ValueError("at least one explicit quota policy is required")
        if isinstance(max_reservations, bool) or not isinstance(max_reservations, int) or max_reservations < 1:
            raise ValueError("max_reservations must be a positive integer")
        normalized: dict[tuple[str, str], QuotaPolicy] = {}
        for key, policy in policies.items():
            if (not isinstance(key, tuple) or len(key) != 2
                    or any(not isinstance(part, str) or not part.strip() for part in key)):
                raise ValueError("policy keys must be non-empty (provider_id, operation) pairs")
            if not isinstance(policy, QuotaPolicy):
                raise ValueError("every policy value must be a QuotaPolicy")
            normalized[key] = policy
        self._policies = normalized
        self._clock = clock
        self._max_reservations = max_reservations
        self._lock = threading.RLock()
        self._windows: dict[tuple[str, str, int], _Window] = {}
        self._reservations: dict[str, _ReservationRecord] = {}

    def reserve(
        self, provider_id: str, operation: str, *, units: int = 1,
        reservation_id: str,
    ) -> QuotaReservation:
        self._validate_scope(provider_id, operation)
        self._validate_units(units)
        if not isinstance(reservation_id, str) or not reservation_id.strip():
            raise ValueError("reservation_id must be a non-empty caller-supplied string")
        policy = self._policy(provider_id, operation)
        now = self._now()
        window_id = math.floor(now / policy.window_seconds)
        window_end = (window_id + 1) * policy.window_seconds
        key = (provider_id, operation, window_id)

        with self._lock:
            self._prune(now)
            existing = self._reservations.get(reservation_id)
            if existing is not None:
                item = existing.reservation
                if (item.provider_id, item.operation, item.units) != (provider_id, operation, units):
                    raise QuotaReservationConflict("reservation_id already belongs to another request")
                if existing.state == "reserved" and item.window_id == window_id:
                    return item
                raise QuotaReservationConflict("reservation_id has already reached a terminal state")

            if len(self._reservations) >= self._max_reservations:
                raise QuotaExceeded(
                    "reservation capacity exhausted; provider call denied",
                    retry_after_seconds=max(0.0, window_end - now),
                )

            usage = self._windows.setdefault(key, _Window())
            if usage.consumed + usage.reserved + units > policy.max_units:
                raise QuotaExceeded(
                    "provider operation quota exhausted; provider call denied",
                    retry_after_seconds=max(0.0, window_end - now),
                )

            reservation = QuotaReservation(
                reservation_id=reservation_id,
                provider_id=provider_id,
                operation=operation,
                units=units,
                window_id=window_id,
                expires_at=min(now + policy.reservation_ttl_seconds, window_end),
            )
            usage.reserved += units
            self._reservations[reservation_id] = _ReservationRecord(reservation)
            return reservation

    def settle(self, reservation_id: str, *, actual_units: int | None = None) -> QuotaSnapshot:
        if not isinstance(reservation_id, str) or not reservation_id.strip():
            raise ValueError("reservation_id must be a non-empty string")
        with self._lock:
            now = self._now()
            self._prune(now)
            record = self._reservations.get(reservation_id)
            if record is None:
                raise QuotaReservationNotFound("reservation not found or expired")
            if record.state != "reserved":
                if record.state == "settled":
                    return self.snapshot(record.reservation.provider_id, record.reservation.operation)
                raise QuotaReservationConflict("only an active reservation can be settled")
            item = record.reservation
            policy = self._policy(item.provider_id, item.operation)
            if actual_units is None:
                actual_units = item.units
            self._validate_units(actual_units)
            if actual_units > item.units:
                raise QuotaExceeded(
                    "actual usage exceeds the reserved amount; additional authorization is required",
                    retry_after_seconds=max(0.0, (item.window_id + 1) * policy.window_seconds - now),
                )
            usage = self._windows[(item.provider_id, item.operation, item.window_id)]
            usage.reserved -= item.units
            usage.consumed += actual_units
            record.state = "settled"
            return self._snapshot(item.provider_id, item.operation, item.window_id, now)

    def release(self, reservation_id: str) -> QuotaSnapshot:
        if not isinstance(reservation_id, str) or not reservation_id.strip():
            raise ValueError("reservation_id must be a non-empty string")
        with self._lock:
            now = self._now()
            self._prune(now)
            record = self._reservations.get(reservation_id)
            if record is None:
                raise QuotaReservationNotFound("reservation not found or expired")
            if record.state == "released":
                item = record.reservation
                return self._snapshot(item.provider_id, item.operation, item.window_id, now)
            if record.state != "reserved":
                raise QuotaReservationConflict("only an active reservation can be released")
            item = record.reservation
            usage = self._windows[(item.provider_id, item.operation, item.window_id)]
            usage.reserved -= item.units
            record.state = "released"
            return self._snapshot(item.provider_id, item.operation, item.window_id, now)

    def snapshot(self, provider_id: str, operation: str) -> QuotaSnapshot:
        self._validate_scope(provider_id, operation)
        policy = self._policy(provider_id, operation)
        now = self._now()
        window_id = math.floor(now / policy.window_seconds)
        with self._lock:
            self._prune(now)
            return self._snapshot(provider_id, operation, window_id, now)

    def _snapshot(self, provider_id: str, operation: str, window_id: int, now: float) -> QuotaSnapshot:
        policy = self._policy(provider_id, operation)
        usage = self._windows.get((provider_id, operation, window_id), _Window())
        return QuotaSnapshot(
            provider_id=provider_id,
            operation=operation,
            window_id=window_id,
            consumed_units=usage.consumed,
            reserved_units=usage.reserved,
            remaining_units=max(0, policy.max_units - usage.consumed - usage.reserved),
            reset_in_seconds=max(0.0, (window_id + 1) * policy.window_seconds - now),
        )

    def _prune(self, now: float) -> None:
        for reservation_id, record in list(self._reservations.items()):
            item = record.reservation
            policy = self._policy(item.provider_id, item.operation)
            window_end = (item.window_id + 1) * policy.window_seconds
            if record.state == "reserved" and now >= item.expires_at:
                usage = self._windows.get((item.provider_id, item.operation, item.window_id))
                if usage is not None:
                    usage.reserved = max(0, usage.reserved - item.units)
                record.state = "expired"
            if record.state != "reserved" and now >= window_end:
                del self._reservations[reservation_id]
        for key in list(self._windows):
            if now >= (key[2] + 1) * self._policy(key[0], key[1]).window_seconds:
                del self._windows[key]

    def _policy(self, provider_id: str, operation: str) -> QuotaPolicy:
        try:
            return self._policies[(provider_id, operation)]
        except KeyError as exc:
            raise QuotaPolicyMissing("no explicit quota policy; provider call denied") from exc

    def _now(self) -> float:
        value = self._clock()
        if not math.isfinite(value):
            raise ValueError("clock must return a finite value")
        return value

    @staticmethod
    def _validate_scope(provider_id: str, operation: str) -> None:
        if not isinstance(provider_id, str) or not provider_id.strip():
            raise ValueError("provider_id must be a non-empty string")
        if not isinstance(operation, str) or not operation.strip():
            raise ValueError("operation must be a non-empty string")

    @staticmethod
    def _validate_units(units: int) -> None:
        if isinstance(units, bool) or not isinstance(units, int) or units < 1:
            raise ValueError("units must be a positive integer")
