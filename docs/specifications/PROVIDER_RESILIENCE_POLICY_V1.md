# Provider Resilience Policy v1

- **Status:** Proposed policy / implementation gate
- **Depends on:** ADR-0013, ADR-0019, Provider Registry Runtime v1, Adapter Dispatch v1
- **Scope:** Provider execution resilience after deterministic provider selection and trusted adapter dispatch
- **Runtime status:** Specification only. No resilience controls are implemented by this document.

## 1. Purpose

Protect TruckFood from provider slowness, transient failures, quota exhaustion and cascading outages without weakening truck-safety, capability, geography, data-rights or cost constraints.

Resilience is an application policy around trusted adapters. It must never turn an unavailable or unsupported operation into a fabricated success.

## 2. Non-negotiable invariants

1. A retry may repeat only an operation explicitly classified as retry-safe/idempotent by the TruckFood operation contract and adapter capability declaration.
2. Retry count is finite and includes the initial attempt in the total attempt budget.
3. A retry must respect provider `Retry-After` guidance, the overall request deadline and the remaining operation budget.
4. No retry is permitted for invalid input, authentication/configuration failure, permission/licensing denial, unsupported capability, safety-parameter mismatch, or conflict unless a future operation-specific rule explicitly proves it safe.
5. A timeout is not a cancellation guarantee. The adapter's transport/client must enforce connect, read and total deadlines; the dispatcher must not claim that a timed-out thread has stopped.
6. Circuit breakers reduce calls to unhealthy providers; they do not change provider eligibility or grant permission to use another provider.
7. Quota and budget decisions must be made before a billable attempt. Failed, retried and fallback attempts must be metered according to the provider's actual billing semantics.
8. Failover is a new provider-selection decision against the original request constraints. It is never a blind switch to the next registered adapter.
9. The system must preserve the selected vehicle profile and every required parameter, geography, freshness, rights and data-use constraint across retries and failover.
10. If no alternative meets every hard requirement, return a normalized unavailable/unsupported result. Never downgrade a truck request to a car route silently.

## 3. Execution deadline and timeout model

Each operation receives a monotonic overall deadline and separate adapter transport limits:

- connection establishment timeout;
- response/read timeout;
- total transport timeout;
- overall use-case deadline, including queueing, retries and fallback.

The adapter must enforce its transport-level timeouts in the underlying HTTP/database client. A wrapper around synchronous Python code cannot safely terminate an arbitrary blocked thread; `Future.result(timeout=...)` alone is not proof of cancellation and must not be represented as an effective hard timeout.

The dispatcher should pass a typed execution context containing the deadline and cancellation signal in a future contract revision. Adapters must check the remaining budget before starting work and configure their transport with a timeout no greater than that budget. A timeout maps to a stable `timeout` failure category, with no raw exception or response body exposed.

## 4. Retry policy

Retries are opt-in per operation and failure category.

Recommended initial policy ceiling for the first runtime implementation:

- maximum attempts: 3 total (initial attempt plus at most 2 retries);
- exponential backoff with full jitter;
- configurable base and maximum delay, bounded by the overall deadline;
- honor `Retry-After` when valid, but never sleep beyond the request deadline;
- no retry when the adapter says the operation is not retry-safe;
- no retry when the response may have committed a non-idempotent side effect and no idempotency key is available.

Retryable categories may include selected network failures, timeouts and provider 5xx responses. Rate-limit responses are retryable only when the provider supplies a safe retry time and the quota policy permits another attempt. The policy must not infer retryability from an exception string.

Use injected clock and random/jitter functions in tests so retry schedules are deterministic. Do not sleep in unit tests.

## 5. Circuit breaker

Circuit state is isolated by provider/adapter identity and operation. Region may be included only where health is genuinely region-specific and the state store can bound its cardinality.

States:

- **closed:** requests may proceed; failures are counted within a configured observation window;
- **open:** calls are rejected locally until the recovery time elapses;
- **half-open:** a small, bounded number of probes may execute; success closes the circuit and failure reopens it.

Requirements:

- thresholds and recovery windows are configuration, not hard-coded vendor assumptions;
- only qualifying transient execution failures affect the breaker;
- invalid requests, rights denials, unsupported operations and caller cancellations do not count as provider-health failures;
- concurrent probes must be bounded;
- breaker-open is not evidence that an alternative provider is compatible;
- process-local state is acceptable for deterministic development tests only; production multi-worker state requires a shared, atomic store or a documented per-worker limitation.

## 6. Quotas, budgets and concurrency

A central policy gate must evaluate, before each billable attempt:

- provider and product/API;
- capability and operation;
- user/tenant or product budget scope;
- region where contractually relevant;
- request count, concurrency and spend limits;
- retry/fallback attempt classification;
- current billing window and reset semantics.

The quota ledger must use atomic reservations/consumption to avoid concurrent requests exceeding limits. Define whether a reservation is released after a request fails before reaching the provider, and how uncertain outcomes are reconciled. Do not assume every provider bills only successful responses.

Use configurable per-provider limits plus global safety ceilings. On exhaustion, return `rate_limited` or `budget_exceeded` without attempting a paid call. Never place API keys, raw payloads or precise user coordinates in quota logs.

In-memory counters are not sufficient for production enforcement across multiple workers or restarts.

## 7. Capability-preserving failover

Failover is allowed only when all of the following hold:

1. The original operation has an explicit failover policy and is safe to repeat.
2. The original provider failure is in the configured failover-trigger set.
3. A fresh registry selection identifies an alternative provider.
4. The alternative is independently approved/enabled, healthy enough, within quota/budget and rights-approved.
5. It supports the exact operation, geography and all required vehicle parameters.
6. Its data-use permissions allow the intended processing and display/persistence action.
7. The result can be represented under the same TruckFood contract without inventing missing capabilities.
8. The overall deadline and cost budget permit the additional attempt.

A fallback with lower coverage, freshness, precision or vehicle support is not equivalent. It may be used only when the use case explicitly permits that limitation and the limitation is surfaced to the user. Hard safety constraints are never negotiable.

Do not chain unlimited providers. Set a finite failover-attempt ceiling, defaulting to one alternative in the first implementation, and prevent loops/revisiting the same provider.

## 8. Normalized outcomes and observability

The resilience layer should preserve the adapter's normalized outcome and add safe policy metadata:

- attempts made;
- retry reason codes;
- circuit state/action;
- quota/budget decision;
- failover decision and reason;
- elapsed time and deadline exhaustion;
- provider/adapter identity and version;
- correlation ID.

Never expose credentials, authorization headers, raw provider bodies, exception messages or unnecessary personal/location data. Observability must not become a second store of licensed provider data.

## 9. Deterministic conformance tests

The implementation must test at least:

- no retry for non-idempotent or non-retry-safe operations;
- maximum-attempt ceiling and deadline clipping;
- `Retry-After` handling and malformed values;
- no retry for invalid, unauthorized, unsupported or licensing-denied outcomes;
- circuit closed/open/half-open transitions and concurrent probe ceiling;
- qualifying vs non-qualifying breaker failures;
- atomic quota reservation under concurrency;
- quota exhaustion prevents provider invocation;
- retries and failover are metered correctly;
- failover rejects any alternative missing a required vehicle parameter, geography, operation or right;
- no fallback from truck routing to car routing;
- provider repetition/loop prevention;
- safe diagnostics with no secret or raw response leakage;
- deterministic tests using fake clocks, fake transports and injected jitter.

Tests must run offline without paid credentials. Live-provider smoke tests are optional and budget-capped.

## 10. Delivery sequence

1. Add typed operation policy metadata and execution context without breaking existing adapter contracts.
2. Implement adapter-enforced transport deadlines and deterministic timeout tests.
3. Implement retry orchestration for explicitly retry-safe operations.
4. Add circuit-breaker state machine and concurrency tests.
5. Define quota ledger interfaces and atomic persistence before enabling paid providers.
6. Add failover only after candidate compatibility can be re-evaluated through the registry.
7. Add telemetry and cost reconciliation with privacy/licensing review.
8. Run the full contract and runtime CI suite; obtain review before merge.

## 11. Current implementation boundary

This document does not claim that any item above is implemented. The current adapter dispatcher remains synchronous and has no effective timeout, retry orchestration, circuit breaker, quota enforcement, billing meter or failover. `AdapterResult.retryable` remains informational metadata only. No live provider is connected or approved.
