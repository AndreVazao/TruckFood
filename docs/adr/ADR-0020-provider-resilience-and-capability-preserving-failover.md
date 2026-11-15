# ADR-0020 — Provider Resilience and Capability-Preserving Failover

- **Status:** Proposed
- **Date:** 2026-11-15
- **Decision owners:** TruckFood project
- **Depends on:** ADR-0013, ADR-0019, Provider Registry Runtime v1, Provider Adapter Dispatch v1

## Context

Provider adapters can be slow, unavailable, rate-limited or costly. Resilience controls are necessary before real external providers are connected. Naive retries can amplify outages and charges; naive fallback can silently remove truck restrictions, geographic coverage or data-use guarantees.

The current registry and dispatcher provide deterministic selection and trusted in-process invocation, but do not implement timeouts, retries, circuit breakers, quotas, billing or failover.

## Decision

Adopt a centralized, operation-aware resilience policy after registry selection and trusted adapter dispatch. The policy must preserve the original request's hard capability, vehicle, geographic, rights and budget constraints.

### Required controls

1. **Deadlines:** adapter transport clients enforce connection/read/total timeouts bounded by an overall monotonic deadline. A synchronous wrapper timeout must not be described as cancellation of a blocked thread.
2. **Retries:** finite, opt-in, idempotency-aware retries with bounded exponential backoff and jitter; honor valid provider retry guidance and the overall deadline.
3. **Circuit breaker:** closed/open/half-open state machine with bounded probes and only transient provider failures contributing to health state.
4. **Quotas and budgets:** centralized preflight and atomic usage reservations; production enforcement must be shared across workers and restarts.
5. **Failover:** fresh provider selection against the original request; alternatives must independently satisfy every hard requirement and be approved, healthy, rights-cleared and within budget.
6. **Observability:** safe, structured decision metadata without secrets, raw response bodies or unnecessary precise location data.

### Safety rule

A generic route is not a substitute for a truck route. No failover may relax required height, width, length, gross weight, axle load, trailer, ADR/hazmat, access or time-dependent constraints. If no compatible alternative exists, fail closed with a normalized outcome.

### Consequences

- Avoids retry storms and uncontrolled provider spend.
- Makes degraded capability visible and explicit.
- Requires operation metadata, shared quota state and adapter transport cooperation.
- Some outages will produce an unavailable result rather than a lower-capability fallback; this is intentional.

### Implementation status

This ADR is proposed only. The accompanying Provider Resilience Policy v1 is a design gate. Runtime code, tests, persistent quota accounting and provider integrations remain future work. PR #3 must be reviewed independently; no merge to main is implied.
