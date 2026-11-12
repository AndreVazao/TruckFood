# TruckFood Provider Registry v1

- **Status:** Proposed specification; no runtime registry is implemented.
- **Version:** 1.0.0
- **Related:** ADR-0002, ADR-0006, ADR-0009, ADR-0013; provider capability contract v1.

## 1. Purpose

The registry is the controlled catalogue of provider adapters that the application may consider for a specific operation. It connects adapter identity and deployment lifecycle to a separately versioned capability declaration. It is not a directory of API keys and does not itself prove that a provider is licensed, reachable, accurate or suitable for a journey.

## 2. Separation of concerns

The registry entry owns operational identity and governance:

- stable `registry_entry_id`, `provider_id` and `adapter_id`;
- adapter and provider product versions;
- environment and lifecycle state;
- reference to the capability declaration and its SHA-256 digest;
- configuration key names (never secret values);
- rights-review reference/state and review dates;
- operational health state and last check;
- activation and retirement metadata.

The capability declaration remains the source of truth for operations, geography, vehicle parameters, freshness, cost, attribution and data rights. Do not copy those fields into the registry entry: duplication would allow contradictory declarations.

## 3. Identity and immutable revisions

An adapter identity is stable across releases; each adapter release is versioned. A registry revision must pin the exact capability declaration using both a repository-relative or approved immutable reference and a SHA-256 digest of the exact UTF-8 bytes. A changed declaration requires a new digest and registry revision. Consumers must reject a digest mismatch.

The registry entry must not use mutable branch names as the sole integrity reference in production. A commit or immutable artifact reference is preferred. The illustrative fixture uses repository paths and clearly remains non-production.

## 4. Environments and lifecycle

Environments: `fixture`, `development`, `staging`, `production`.

Lifecycle states: `draft`, `under_review`, `approved`, `enabled`, `suspended`, `retired`.

Only `enabled` entries in the requested environment are candidates for runtime selection. `approved` is not the same as `enabled`. Fixture entries are never eligible for production.

Suspension must take effect without deleting history. Retirement prevents new selection but preserves references needed to explain historical journeys and prior decisions.

## 5. Rights governance

The registry records a governance decision and points to supporting terms/licence review. The capability declaration specifies the operation-level data rights. Both must be acceptable for the intended use.

Fail closed when rights are unknown, blocked, expired, overdue for review or conditional without its conditions being satisfied. Do not infer that permission to display includes caching, storage, transformation, redistribution or offline use. A registry status cannot override provider contract terms.

## 6. Operational health

Health states: `unknown`, `healthy`, `degraded`, `unavailable`, `disabled`. Health is time-stamped and environment-specific. A missing or stale health observation is not healthy. Health may influence availability selection but cannot increase declared capability or data trust.

Health checks must be bounded, budget-aware and avoid sending real driver coordinates unless strictly required and approved. Health checks must not expose credentials or sensitive response payloads.

## 7. Selection policy

Selection is performed per use case and operation, not by provider brand. The selector must:

1. load an enabled entry for the requested environment;
2. verify immutable declaration reference and digest;
3. validate the declaration against the provider contract schema;
4. require the requested capability family and operation;
5. require adequate geographic coverage for the requested region;
6. verify every safety-critical vehicle parameter required by the use case;
7. evaluate data rights for the exact intended processing/use;
8. apply freshness, quota, budget and operational-health constraints;
9. rank only the remaining eligible candidates using an explicit deterministic policy;
10. return the selected adapter together with limitations, provenance and the reason for selection.

If no adapter meets mandatory requirements, return a typed unsupported/unavailable/insufficient-capability outcome. Never silently downgrade to a car route, invent vehicle support, ignore regional gaps or treat unknown as supported. A degraded alternative may be offered only when the caller explicitly permits it and the limitation is made visible.

## 8. Deterministic precedence

The initial policy is eligibility-first, then configured priority (lower integer wins), then stable `registry_entry_id` lexical order. Priority cannot override capability, rights, safety, environment or budget gates. No random selection or implicit provider-brand preference.

## 9. Secrets and configuration

The registry may list environment variable or secret-manager key names, but never values, tokens, passwords, private URLs containing credentials or raw provider payloads. Secret resolution belongs to the server-side runtime. Client applications must never receive provider secrets.

## 10. Audit and change control

Record registry revision, selector policy version, requested operation/region/vehicle requirements, selected entry, rejected-candidate reason codes, declaration digest and decision timestamp. Redact personal coordinates and secrets. Changes to rights, capability, adapter version, activation or priority require review and an auditable revision.

## 11. Conformance tests

At minimum test: digest mismatch; missing declaration; invalid schema; fixture-to-production rejection; disabled/suspended/retired entry; unknown/expired rights; review overdue; unsupported operation; inadequate geography; missing vehicle height/weight/axle/trailer/ADR support; stale health; quota/budget exhaustion; deterministic tie-break; safe fallback; no car-route downgrade; and secret-value rejection.

## 12. Non-goals and implementation status

This specification does not implement a registry service, database table, runtime selector, provider adapters, credentials, health probes or provider approval. The example manifest is synthetic and exists only to validate structure. No real provider is approved or production-enabled by this document.
