# Provider Quota Manager v1

## Status

Implemented as a process-local, in-memory reservation ledger in proposed PR #7. It is a deterministic foundation and contract example, not production multi-worker quota enforcement.

## Scope and policy

Policies are explicitly configured by the exact pair `(provider_id, operation)`. Each policy defines a maximum number of caller-defined cost units in a fixed monotonic-time window, plus a reservation TTL. There is no implicit/default allowance: a missing policy denies the reservation.

The unit is intentionally provider-neutral. One unit may represent one request, one billable lookup, or another explicitly documented cost unit; the application must not assume different providers or operations have equivalent unit economics.

## Reservation lifecycle

1. Before a potentially billable provider call, the caller supplies a stable, non-empty reservation ID and atomically reserves the maximum expected units.
2. The manager counts both consumed and outstanding reserved units against the window limit. If the limit or internal reservation capacity cannot be confirmed, it raises a quota error and the provider call must not run.
3. After the operation, the caller settles the reservation with actual units (never greater than reserved) or releases it when no usage occurred.
4. The configured TTL marks a reservation as stale; it does **not** release its reserved units. The provider call may still be running or may already have incurred usage when the TTL elapses.
5. A stale reservation remains charged to its original quota window, including after that window boundary, until an explicit settlement or release reconciles it. Settlement records actual units (defaulting conservatively to the full reserved amount); release is an explicit assertion by the caller that no billable usage occurred.
6. An active repeated reservation with the same ID and same scope/units returns the original reservation. Reusing an ID for different parameters or replaying a terminal reservation is rejected.

All admission, settlement and release transitions are protected by one process-local lock. The manager bounds retained reservation records and fails closed when its capacity is exhausted.

## Integration requirements

- Reserve before dispatch; do not call the provider after `QuotaExceeded` or `QuotaPolicyMissing`.
- On a confirmed no-usage failure, release. Release is the caller's explicit confirmation that no billable usage occurred.
- When the provider may have performed billable work despite a timeout/error, settle conservatively; do not automatically release uncertain usage.
- TTL expiry is not proof that a provider operation stopped. Stale reservations continue consuming reserved capacity until explicitly settled or released. Unreconciled reservations are retained across window boundaries and consume bounded in-memory record capacity; capacity exhaustion fails closed.
- Settle actual units only when they are known and within the reservation. If actual usage exceeds the reservation, the manager refuses settlement; the caller must not silently undercount or issue another provider call.
- The caller owns reservation-ID generation and persistence. Reservation IDs are not provider idempotency keys and must not be substituted for them.
- This v1 manager does not infer prices, currencies, monetary budgets, provider billing rules, or rate-limit semantics.

## Production boundary

This implementation is thread-safe only within one Python process. Separate workers and restarts have independent counters, so it must not be represented as production quota enforcement in a multi-worker deployment. Production requires a shared transactional/atomic backend (for example, a database transaction or atomic Redis script) with durable reservation state, lease/fencing semantics that cannot release live work, tenant/provider/operation scoping, idempotent settlement, reconciliation and concurrency tests. That backend is deliberately not implemented here.

No provider credentials, paid calls, purchases, billing integrations, live provider calls, deployment changes or external side effects are included.
