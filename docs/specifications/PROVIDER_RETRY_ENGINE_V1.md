# Provider Retry Engine v1

## Status

Implemented as a bounded orchestration wrapper around the trusted synchronous dispatcher. This is an initial development/runtime increment, not a complete production timeout or resilience system.

## API

- `RetryPolicy` limits total attempts to 1–3 (including the initial call).
- Only explicitly retryable `unavailable` and `rate_limited` results can be retried.
- Invalid, conflict, unsupported and other outcomes are never retried, even if an adapter sets its retryable flag.
- Exponential backoff uses full jitter, with configurable base and maximum delay.
- The total execution budget is checked before every attempt, after every synchronous call and before sleeping.
- A deterministic clock, sleeper and random source can be injected for offline tests.
- Result metadata reports attempt count, elapsed time and safe retry reason codes.

## Deadline limitation — important

The current adapter interface is synchronous and has no cancellation/context parameter. Python cannot safely terminate an arbitrary blocked thread. Therefore this version enforces a cooperative total budget and discards results that arrive after the deadline, but it **does not interrupt a blocked adapter call** and does not claim transport-level timeout enforcement.

Every network adapter must configure connect/read/total timeouts in its own underlying HTTP client, bounded by the remaining request budget. A later contract increment should pass a typed execution context/deadline to adapters and test transport cancellation semantics.

## Deliberate non-goals

No circuit breaker, shared quota ledger, billing meter, automatic provider failover, live provider, credentials or network client is included. Retries remain limited to adapter results explicitly marked retryable and to the allowlisted transient outcomes. Non-idempotent operations must not set retryable until operation-level idempotency is modeled and enforced.
