# Provider Execution Orchestration Contract v1

- **Status:** Proposed implementation contract
- **Scope:** In-process orchestration of an already selected provider and a trusted registered adapter.
- **Related:** ADR-0020, PROVIDER_RUNTIME_V1.md, PROVIDER_ADAPTER_DISPATCH_V1.md, SHARED_PROVIDER_QUOTA_LEDGER_V1.md.

## 1. Purpose and non-goals

The runtime currently exposes registry selection, trusted adapter dispatch, bounded retries, a circuit breaker and a process-local quota manager as separate components. No central application boundary currently coordinates their admission and lifecycle rules.

This contract defines the minimum safe sequence for a future `ProviderExecutionCoordinator`. It does not claim that such a coordinator exists, and it does not approve a real provider, credential, backend, deployment or paid call.

## 2. Required input

A coordinator request must carry:
- a successful, immutable `SelectionDecision` produced for the original request;
- the exact operation and a mapping payload;
- a positive total deadline budget;
- explicit operation retry-safety policy (default `never`);
- explicit quota units and a caller-stable reservation ID when quota is configured;
- an adapter dispatcher, circuit breaker, retry executor and quota manager supplied by trusted application composition.

The coordinator must not accept provider identity, adapter identity or capability declarations independently of the selected decision. It must not load code from a manifest.

## 3. Admission and execution order

The implementation must preserve this order:

1. Validate request shape, successful selection, operation and payload before any state reservation or provider invocation.
2. Read provider/adapter identity only from the selected entry and verify it is structurally valid.
3. Reserve quota before any possible provider call. Missing policy, exhausted quota, reservation conflict or quota-store error denies execution.
4. Enter circuit-breaker admission for the selected provider and operation. An open circuit or exhausted half-open probe capacity must not invoke the adapter.
5. Execute the trusted dispatcher through the bounded retry executor, passing the same immutable execution context and idempotency key to every attempt.
6. Settle quota only when the outcome is sufficiently known to account for usage. A confirmed no-usage outcome may release only through an explicit reconciliation path.
7. Return a normalized result with safe orchestration metadata; never expose credentials, raw exception text or raw provider response bodies.

The exact integration between breaker admission and retries must be implemented deliberately: each provider attempt must be visible to breaker health accounting, while the total retry budget/deadline remains bounded. The implementation must not accidentally wrap the whole retry loop as one health sample if that hides repeated provider failures.

## 4. Uncertain outcomes and quota lifecycle

A timeout, deadline expiry, process interruption, transport exception or lost response does not prove that the provider did not execute the operation or incur usage.

- Never automatically release quota on an uncertain result.
- Preserve the reservation as outstanding/stale until explicit reconciliation.
- Do not interpret local cancellation or a discarded late result as remote cancellation.
- If actual usage exceeds reserved units, report an explicit overrun/authorization requirement; do not silently clamp usage.
- Reservation expiry is a stale marker only.

The current quota manager is process-local and in-memory. This coordinator contract does not make it durable, shared across workers or safe across restarts. Production multi-worker enforcement remains blocked on a separately approved shared ledger implementation.

## 5. Retry and idempotency

- Retry only `unavailable` or `rate_limited` outcomes explicitly marked retryable by the trusted adapter and allowed by the operation policy.
- `never` remains the default. Side-effecting operations must not retry without reviewed provider-specific idempotency semantics.
- A key-required operation must supply a non-empty key before the first attempt; every attempt must receive the identical key.
- Invalid, unsupported, conflict and other non-allowlisted outcomes are never retried.
- Maximum attempts remain bounded by the configured retry policy (currently at most three, including the first attempt).
- Deadlines are cooperative at the orchestration layer. Adapter transport clients must enforce connect/read/total timeouts.

## 6. Capability-preserving selection and failover

This v1 coordinator executes only the selected provider. It does not implement automatic failover.

Any later failover increment must re-run registry selection against the original request and independently satisfy the same operation, vehicle parameters, geography, rights, freshness and safety requirements. It must not reuse a prior adapter selection or weaken a constraint to obtain a result. No eligible alternative means fail closed.

## 7. Result contract

The coordinator must preserve normalized dispatch outcomes:
`success`, `empty`, `partial`, `unsupported`, `unavailable`, `rate_limited`, `invalid`, and `conflict`.

Safe metadata may include provider/adapter IDs, attempt count, elapsed time, circuit state, quota reservation state and whether provider invocation was attempted. It must not include secrets, raw payloads, precise location beyond the minimum required, raw provider bodies or exception messages.

## 8. Minimum deterministic verification matrix

1. Invalid selection is rejected before quota reservation and adapter invocation.
2. Invalid operation/payload is rejected before any side effect.
3. Missing quota policy denies invocation.
4. Quota exhaustion denies invocation.
5. Quota reservation is acquired before the first adapter call.
6. Open circuit denies invocation without consuming a provider attempt.
7. Half-open concurrency remains bounded.
8. Default retry safety performs exactly one attempt.
9. Idempotent retry preserves deadline and attempt ceiling.
10. Key-required retry propagates one unchanged key.
11. Invalid, unsupported and conflict results are not retried.
12. Adapter exception is sanitized and treated as uncertain usage.
13. Deadline expiry does not claim cancellation.
14. Uncertain result does not release quota.
15. Explicit confirmed-no-usage reconciliation may release a stale reservation.
16. Known usage settles the reservation.
17. Usage overrun is surfaced, not discarded.
18. Retry attempts are individually reflected in breaker health state.
19. Metadata contains no raw payload, provider response or exception text.
20. Missing/inconsistent dependencies fail closed before provider invocation.

All tests must use synthetic adapters, injected clocks and deterministic callbacks. No network, credentials, live provider, billing or deployment is permitted in this increment.

## 9. Implementation gates

Implement the coordinator in a small follow-up PR with deterministic tests. Keep shared/durable quota storage, provider-specific idempotency verification, real adapters, failover and production deployment out of scope until separately evidenced and approved.
