# ADR-0009 — API Boundaries & Error Contracts

**Status:** Proposed — Discovery / Foundation  
**Date:** 2026-10-14  
**Decision:** TruckFood should expose use-case-oriented API contracts that are independent of provider-specific schemas, validate all inputs at trusted boundaries, and distinguish unavailable, unknown, partial, conflicting and empty results.

## 1. Context

ADR-0008 proposes a modular monolith with explicit application, domain, persistence and integration boundaries. TruckFood must support mobile and web clients, community submissions, location discovery and future journey intelligence without leaking database or provider implementation details.

TruckFood handles information that may influence professional driving decisions. An API response must therefore communicate uncertainty and data freshness rather than collapsing every failure or missing record into an empty result.

## 2. Decision

API contracts will be designed around TruckFood use cases and canonical domain concepts.

The API boundary must:
- validate and normalize input;
- authenticate and authorize protected operations;
- call application use cases rather than directly exposing database tables;
- return stable TruckFood-owned response shapes;
- preserve provenance, freshness and uncertainty when relevant;
- use consistent error categories;
- apply pagination, request limits and bounded provider usage;
- avoid exposing provider credentials, raw vendor objects or internal stack traces.

The exact transport and endpoint paths remain open. HTTP/JSON is the initial candidate for client-facing APIs, but this ADR does not freeze a framework or API specification format.

## 3. Contract Families

Initial API families should map to the product's use cases:

1. **Identity & Driver Context** — current user context and permitted profile operations.
2. **Vehicle Profiles** — create, inspect and update versioned vehicle profiles.
3. **Locations & Services** — search and retrieve canonical locations, capabilities, access information and service relationships.
4. **Evidence & Community** — submit observations, reviews, corrections and reports.
5. **Restrictions & Assessments** — retrieve known restrictions and explainable evaluation outcomes when implemented.
6. **Administration & Moderation** — privileged review, source management and audit operations.
7. **Operational Status** — limited health/readiness information that does not reveal secrets or private data.

Journey planning and route intelligence remain future capabilities until provider, licensing, data-quality and safety prerequisites are validated.

## 4. Request and Response Rules

- Use stable TruckFood IDs for canonical entities.
- External provider IDs are references, not primary public identity.
- Validate identifiers, enums, numeric ranges, units, lengths and payload sizes.
- Units must be explicit for vehicle dimensions, weight and restriction values.
- Unknown optional vehicle attributes must remain unknown; do not silently fill them with defaults that affect suitability.
- Use consistent timestamps and clearly document timezone semantics.
- Responses must distinguish absent optional fields from explicit null values where that distinction matters.
- Search responses should support bounded pagination and deterministic ordering where feasible.
- Do not return unrestricted raw database rows as a public contract.
- Do not expose internal database column names as a permanent API promise.

## 5. Result Semantics

An empty search result means only that no matching result was returned for the stated query and coverage; it does not mean a road or location is safe, unrestricted or nonexistent.

Where relevant, responses must distinguish:
- complete result;
- partial result;
- provider unavailable;
- unknown;
- insufficient data;
- conflicting evidence;
- stale/expired evidence;
- unauthorized or forbidden operation;
- invalid request.

If a provider fails, the API must not disguise that failure as a successful empty result.

For restriction or suitability outputs, include enough explanatory context to identify the applicable vehicle context, time context, evidence state and important limitations. Do not claim guaranteed safety.

## 6. Error Contract

Use a stable error envelope containing, at minimum:
- machine-readable error code;
- safe human-readable message;
- request/correlation identifier when available;
- field-level validation details where appropriate;
- retryability or retry guidance when meaningful.

HTTP status codes should match the failure category. Exact code names and schema will be defined in the API specification.

Do not expose stack traces, SQL errors, secrets, provider credentials or internal infrastructure details to clients. Detailed diagnostics belong in protected server logs.

## 7. Authentication and Authorization

- Public discovery operations must expose only intentionally public fields.
- Driver profile, vehicle, journey and personal data require authorization.
- Every protected operation must verify ownership or the relevant role server-side.
- Administrative endpoints must require explicit privileged roles and audit sensitive actions.
- Database RLS, where used, is a second enforcement layer, not a reason to omit application authorization.
- Never trust user ID, role or ownership values supplied by the client without server-side verification.
- Service-role credentials must never be shipped to browser or mobile clients.

Detailed policies remain for a dedicated security/RLS decision.

## 8. Provider Boundary

Provider adapter responses must be mapped into internal application/domain result types before becoming public API responses.

Public API contracts must not depend on:
- vendor-specific enum names;
- vendor JSON nesting;
- provider credentials or request identifiers;
- a vendor's temporary response shape.

Where useful, the API may expose a carefully designed source attribution, coverage caveat, freshness timestamp or provider-derived confidence label. Such fields must be normalized and documented.

## 9. Rate Limits, Pagination and Cost Controls

- Apply bounded page sizes and request payload sizes.
- Rate-limit public and authenticated operations according to abuse and cost risk.
- Set timeouts and bounded retries for provider-backed requests.
- Avoid triggering expensive external calls for every UI interaction where caching or request consolidation is permitted.
- Respect each provider's licensing, caching and storage terms.
- Record usage metrics without collecting unnecessary personal data.
- Do not promise unlimited availability or cost-free operation.

Exact quotas, cache policies and pricing thresholds are follow-up decisions.

## 10. Versioning and Compatibility

- Treat public request/response schemas as versioned contracts.
- Prefer additive changes when possible.
- Document breaking changes and migration expectations.
- Do not rename or reinterpret a field silently when clients may depend on it.
- Maintain contract tests for validation, errors, authorization and key response semantics.
- Internal module interfaces may evolve more freely, but changes must remain covered by tests.

The initial versioning mechanism is not frozen here.

## 11. MVP Scope

The first API slice should support only validated MVP use cases:
- driver and basic vehicle profile operations;
- location search and location details;
- selected capabilities/services;
- provenance/freshness display for important facts;
- community observation/review submission with moderation state;
- administrative moderation behind protected authorization.

Restriction evaluation and route intelligence should be exposed only after their semantics and evidence limitations are implemented and tested.

## 12. Non-Goals

This ADR does not freeze:
- exact URL paths;
- OpenAPI file format;
- REST versus alternative transport for internal calls;
- framework or deployment runtime;
- exact error-code strings;
- JWT/session provider configuration;
- final RLS policies;
- provider-specific response schemas;
- route-planning API;
- final cache durations or rate-limit numbers.

## 13. Consequences

### Positive
- Keeps clients independent of persistence and provider details.
- Makes failures and uncertainty explicit.
- Improves authorization and cost-control consistency.
- Enables contract tests without live providers.
- Allows internal modules to evolve without accidental public API changes.

### Trade-offs
- Requires explicit mapping and validation at boundaries.
- Stable contracts need documentation and version discipline.
- Partial results and uncertainty require more thoughtful UI handling.
- Exact security, versioning and transport decisions remain to be completed.

## 14. Follow-up Decisions

1. Define security/privacy requirements and Supabase RLS.
2. Decide spatial storage/query strategy.
3. Define provider adapter contracts.
4. Specify the first MVP API schemas and error codes.
5. Define rate limits, cache policy and operating budget.
6. Validate the contracts against actual mobile/web user journeys.
