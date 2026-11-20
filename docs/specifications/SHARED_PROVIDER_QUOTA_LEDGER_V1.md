# Shared Provider Quota Ledger — Contract v1

- **Status:** Architecture contract proposal; no backend selected or implemented
- **Date:** 2026-11-20
- **Related:** `PROVIDER_QUOTA_MANAGER_V1.md`, ADR-0008, ADR-0018, PRs #7 and #8

## 1. Purpose

Define the correctness contract required before replacing the process-local `QuotaManager` with a durable ledger shared by multiple application workers and recoverable after process restarts.

This document is deliberately storage-neutral. PostgreSQL is a candidate because the wider TruckFood architecture already proposes PostgreSQL/PostGIS, but neither PostgreSQL nor Supabase is approved or provisioned. Redis, a database extension, a hosted service or a second datastore must not be introduced until operational, cost, backup/restore, security and local-development requirements are assessed.

**This is a contract, not an implementation.** No database, Redis instance, migration, schema, credentials, network integration or deployment is created by this proposal.

## 2. Non-negotiable invariants

1. **Atomic admission:** checking the limit and creating the reservation are one indivisible operation for a quota bucket. No two workers may both spend the same remaining capacity.
2. **Durable reservation:** once reserve reports success, the reservation and its quota impact survive worker/process restart and are visible to every worker using the same ledger.
3. **Fail closed:** if the ledger cannot establish the authoritative result of reserve, the provider operation must not be invoked.
4. **No expiry-based release:** TTL/lease expiry is not proof that provider work stopped or incurred no charge. Expiry may mark work stale or eligible for reconciliation, but cannot free quota by itself.
5. **Idempotent identity:** the caller-supplied reservation ID is unique within a documented ledger namespace. Repeating an identical request returns the same logical reservation; reusing the ID with different immutable inputs is a conflict.
6. **Idempotent terminal transitions:** repeated settlement/release with the same terminal payload returns the established result; a different terminal payload conflicts and cannot rewrite history.
7. **Historical attribution:** usage and reservations remain associated with the original policy and quota window even when settlement happens later.
8. **No hidden overrun:** if confirmed actual usage exceeds reserved units, the ledger records the actual amount and an explicit overrun/debt condition atomically. It must not silently clamp usage or discard the provider's confirmed consumption.
9. **Tenant and policy isolation:** quota identity must include the configured enforcement scope. The scope (global provider, organization/tenant, account, credential, or another level) is an explicit policy decision, never inferred from a caller-controlled label.
10. **Auditable transitions:** reserve, settlement, release, stale marking and administrative reconciliation carry timestamps, actor/correlation identity and version information sufficient to explain every capacity change.

## 3. Proposed logical contract

The application depends on a domain port, not a concrete database SDK:

- `reserve(request) -> ReservationResult`
- `settle(reservation_id, settlement) -> ReservationResult`
- `release(reservation_id, release_evidence) -> ReservationResult`
- `get_reservation(reservation_id) -> ReservationResult`
- `get_bucket_snapshot(quota_key, window_id) -> QuotaSnapshot`
- `list_reconciliation_candidates(criteria) -> bounded page` (privileged worker/admin path only)

The concrete types and Python protocol are deferred to an implementation PR after storage selection. The logical request must carry:

- stable reservation ID;
- explicit quota key/scope and policy version;
- provider ID and operation;
- reserved units and unit definition;
- correlation/request ID;
- creation time assigned by the authoritative ledger;
- optional owner/worker identity for observability, not as proof that work has stopped.

A reservation record must preserve immutable request identity, original window, reserved units, confirmed consumed units, status, creation/update timestamps, terminal payload fingerprint and monotonically increasing record version. Provider idempotency keys remain a separate concept.

## 4. State machine

The durable state model must distinguish at least:

| State | Meaning | Capacity treatment |
|---|---|---|
| `reserved` | Admission succeeded; provider work may start or be running | Reserved units count |
| `stale` | Expected completion/lease time elapsed; outcome remains uncertain | Reserved units still count |
| `settled` | Confirmed actual usage recorded | Actual units count as consumed |
| `released` | Caller supplied explicit evidence that no billable usage occurred | Reserved units are returned |
| `overrun` | Confirmed usage exceeded reserved amount | Actual usage and overrun debt count; new admission is constrained |

Allowed transitions:

- `reserved -> stale` may be performed by expiry/reconciliation workers and does not change quota usage.
- `reserved -> settled` and `stale -> settled` record actual usage atomically.
- `reserved -> released` and `stale -> released` require an explicit caller/reconciler assertion supported by operation evidence that no billable usage occurred.
- `reserved -> overrun` or `stale -> overrun` records confirmed usage greater than the reservation.
- Terminal states cannot be changed by a later stale worker or replay.
- A repeated identical terminal command is idempotent; a conflicting terminal command returns a conflict.

A lease may identify the current reconciliation owner and a monotonically increasing fencing token may reject writes from an obsolete owner. **Fencing protects ledger writes; it cannot cancel an external provider request.** A lease expiring therefore never authorizes release. The system must establish the provider operation's outcome before releasing capacity.

## 5. Atomic quota-window semantics

The first implementation may support fixed windows only. Its exact boundary semantics must be specified and tested:

- Persisted windows use an authoritative UTC time source, not process-local monotonic clocks.
- The window start/end and policy version are stored with each reservation.
- Admission atomically reads the bucket, validates policy and remaining capacity, creates the reservation and increments outstanding reserved units.
- Settlement atomically subtracts the reservation's reserved units and adds confirmed actual units to the same historical bucket.
- Release atomically subtracts reserved units only after the explicit no-usage assertion is accepted.
- Overrun settlement records actual units even if they exceed the reserved amount and marks the bucket/ledger as overrun; it must not permit the overrun to disappear at the next request.
- A reservation settled after its original window closes is still charged to that original window.
- A later policy change does not rewrite reservations admitted under an earlier policy version.
- Reads used for dashboards may be eventually consistent only if clearly labelled; admission decisions must always use the authoritative atomic path.

The policy owner must decide whether the quota scope is global per provider/operation or partitioned by tenant/account/credential. That decision must match the provider's actual quota and billing rules; the ledger must not guess.

## 6. Crash and uncertain-outcome handling

The provider call and the ledger cannot generally participate in one distributed transaction. The implementation must therefore model uncertainty rather than promise exactly-once external execution.

Required sequence:

1. Persist the reservation before dispatch.
2. Dispatch using a separate provider idempotency key where the provider supports it.
3. Persist confirmed outcome/usage through idempotent settlement.
4. If the worker crashes or times out after dispatch, keep the reservation charged and mark it stale for reconciliation.
5. Reconciliation queries durable operation records or provider-supported status/idempotency mechanisms where available. If the outcome cannot be established, retain the reservation and escalate; do not guess that usage was zero.
6. Release only after evidence establishes no billable operation occurred.
7. If provider status cannot be queried and no reliable outcome exists, keep the reservation held until a reviewed manual/contractual reconciliation decision.

The ledger provides at-most-one accepted reservation identity and idempotent state transitions. It does **not** guarantee exactly-once provider execution.

## 7. Concurrency, isolation and storage requirements

Any selected backend must demonstrate:

- atomic compare/check-and-reserve under concurrent workers;
- unique reservation identity enforced by storage, not only application locks;
- transactionally consistent bucket and reservation updates;
- durable commit acknowledgement before dispatch;
- safe retry after client timeout when commit outcome is unknown;
- serializable semantics or an equivalent proven atomic primitive for each quota key/window;
- bounded pagination and indexes for reconciliation;
- retention/archival rules that do not delete unsettled reservations or historical accounting;
- tenant isolation and least-privilege access;
- backup/restore and recovery-point/recovery-time expectations;
- observability without logging secrets or sensitive provider payloads.

A process-local lock, in-memory cache or read-then-write sequence is not sufficient for multi-worker admission. A cache may accelerate reads but must never become the authority for quota admission.

## 8. Minimum verification matrix

The implementation PR must add deterministic tests for:

1. Two or more workers concurrently reserving the final available units: total accepted units never exceed the limit.
2. Same reservation ID and same immutable request retried concurrently: one logical reservation.
3. Same reservation ID with different provider, operation, scope, policy version or units: conflict.
4. Worker crash immediately after durable reserve and before provider dispatch.
5. Worker crash after provider dispatch but before settlement.
6. Client timeout with unknown transaction commit outcome, followed by safe retry.
7. Stale/expired lease cannot release capacity.
8. Obsolete fencing token cannot settle or release a newer generation.
9. Late settlement charges the original window and policy version.
10. Duplicate identical settlement returns the same terminal result.
11. Conflicting settlement/release after terminal state is rejected.
12. Confirmed usage above reserved units records overrun without undercounting.
13. Confirmed no-usage release requires explicit evidence and is idempotent.
14. Database restart/reconnect preserves reservations and snapshots.
15. Backup/restore retains unresolved reservations and accounting consistency.
16. Tenant/scope isolation prevents one principal from reading or reconciling another scope.
17. Ledger unavailable or ambiguous reserve result prevents provider invocation.
18. Reconciliation pagination is bounded and does not skip/duplicate records under concurrent updates.
19. Policy changes do not mutate historical reservations.
20. Window-boundary and authoritative-clock behaviour is deterministic.

Tests must use an isolated ephemeral backend or a deterministic test implementation with the same atomicity contract. Thread-only tests against the existing in-memory manager do not prove multi-process correctness.

## 9. Rollout and migration gates

1. Inventory the actual application runtime, dependency policy, deployment target and existing persistence choices.
2. Confirm quota ownership/scope and provider-specific unit semantics.
3. Compare candidate backends against atomicity, durability, operational cost, backups, local development and security.
4. Choose one backend explicitly; do not add two systems for speculative future needs.
5. Specify schema/transactions and migration/rollback strategy.
6. Implement the storage adapter behind the domain port, retaining the in-memory manager for unit tests only.
7. Run multi-process concurrency, crash/recovery and fault-injection tests against the selected backend.
8. Prove that uncertain provider outcomes remain charged and that overrun is visible.
9. Review authorization, tenant boundaries, audit and operational monitoring.
10. Only then consider enabling the durable ledger in a non-production environment.

## 10. Explicit non-goals

This contract does not select PostgreSQL, Supabase or Redis; create SQL; add dependencies; configure secrets; call providers; implement billing; set production quotas; deploy infrastructure; or claim multi-worker enforcement. Those actions require separate evidence and review.

## 11. Open decisions

- Which provider quota scopes are truly global versus account/credential/tenant-specific?
- Which providers expose reliable operation-status or idempotency mechanisms?
- What retention period and archival policy apply to settled accounting records?
- What manual reconciliation authority and evidence are acceptable for permanently ambiguous outcomes?
- Which hosting/database option meets backup, recovery, privacy, cost and local-development constraints?
- What overrun policy should block future requests, and who may clear a reviewed overrun?

These decisions must be resolved before production implementation. The safest default for unknown answers is to deny new provider work and retain uncertain reservations.
