# Provider Circuit Breaker v1

## Status

Implemented as a process-local, in-memory execution guard in the proposed PR #6. This is not a distributed or production multi-worker breaker.

## Isolation and policy

State is keyed by the exact pair `(provider_id, operation)`. The default policy opens after three consecutive `unavailable` outcomes, waits 30 seconds, and permits one half-open probe. All thresholds and the monotonic clock are injectable/configurable for deterministic tests.

Only `unavailable` counts as a provider-health failure. Successful `success`, `empty`, or `partial` results reset the consecutive-failure counter. `invalid`, `unsupported`, `conflict` and `rate_limited` do not count as provider-health failures; they are application, capability, conflict or quota outcomes, not evidence that the provider is unreachable.

## State machine

- `closed`: callback may execute; consecutive qualifying failures are counted.
- `open`: callback is not invoked; a normalized `unavailable/circuit_open` result is returned with retry-after metadata.
- `half_open`: after the recovery interval, only the configured number of probes may run concurrently. A successful or non-health probe response closes the breaker; `unavailable` reopens it.

A generation counter prevents late results from earlier in-flight calls from overwriting a newer open/half-open transition. State transitions and probe admission are protected by a process-local lock. State cardinality is capped (default 1,024 entries); when full, the least-recently-used closed entry may be evicted. Open/half-open entries are never evicted to make room. If no closed entry is available, a new call fails closed with `circuit_capacity_exceeded` and does not invoke the provider.

## Boundaries

- The breaker does not select or authorize an alternative provider and does not implement failover.
- An open circuit is not proof that another provider is compatible with the original geography, vehicle, operation or data rights.
- This implementation is process-local. Multiple workers/processes can make independent decisions; production shared enforcement requires a shared atomic store and bounded state lifecycle.
- No credentials, paid calls, provider integrations, quota/billing, persistent state or deployment changes are included.
