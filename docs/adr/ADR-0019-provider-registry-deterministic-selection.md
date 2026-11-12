# ADR-0019 — Provider Registry and Deterministic Selection

- **Status:** Proposed
- **Date:** 2026-11-12
- **Decision owners:** TruckFood project
- **Depends on:** ADR-0002, ADR-0006, ADR-0009, ADR-0013

## Context

Provider capability declarations describe what an adapter claims to support, but the application also needs a controlled record of adapter identity, version, environment, lifecycle, rights-review governance, operational health and immutable declaration reference. Duplicating capability details in a registry would create conflicting sources of truth.

## Decision

Adopt a registry manifest that stores operational metadata and references a separately versioned capability declaration by immutable reference and SHA-256 digest. The declaration remains authoritative for operations, coverage, vehicle parameters, freshness, costs, attribution and data rights. Registry metadata must not duplicate these capability fields.

Selection is eligibility-first and deterministic: reject candidates that fail environment, lifecycle, declaration integrity/schema, operation, geography, vehicle-parameter, data-rights, freshness or budget requirements; then order eligible candidates by configured priority and stable registry ID. Unknown or expired rights and unknown safety-critical vehicle capabilities fail closed. A generic car route must never silently replace a required truck-capable route.

Secrets remain outside the manifest. Only server-side configuration key names may be listed. Registry revisions and selection decisions must be auditable.

## Consequences

- Provider selection becomes explainable and reproducible.
- Capability declarations remain independently versioned and testable.
- Registry state cannot override legal rights or manufacture provider capabilities.
- Runtime registry storage, selector, health checks and adapter activation remain implementation work.
- The initial JSON fixture is synthetic; it does not approve or integrate a real provider.

## Validation

The registry manifest has a separate JSON Schema and synthetic fixture. CI validates it independently from provider capability/result fixtures and OpenAPI. Passing schema validation proves structural conformance only, not provider truth, licensing or runtime behaviour.
