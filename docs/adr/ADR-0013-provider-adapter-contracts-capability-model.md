# ADR-0013 — Provider Adapter Contracts and Capability Model

- **Status:** Proposed
- **Date:** 2026-10-30
- **Decision owners:** TruckFood project
- **Scope:** Map display, geocoding, routing, restrictions, POI/business data, external source ingestion and TruckFood-owned data
- **Depends on:** ADR-0002 (provider abstraction), ADR-0006 (provenance/trust), ADR-0008 (architecture boundaries), ADR-0009 (API boundaries), ADR-0010 (offline packages), ADR-0012 (geospatial strategy)

## 1. Context

TruckFood may combine open geographic data, commercial APIs, official datasets and its own community/curated records. These sources differ in capabilities, coverage, pricing, quotas, data quality, update frequency, failure behaviour and rights to cache, store, transform or redistribute results.

A generic lowest-common-denominator interface would hide important differences. Direct vendor integration throughout the domain would create lock-in and contaminate canonical models with external schemas. TruckFood therefore needs stable internal contracts plus explicit, inspectable provider capabilities and limitations.

## 2. Decision

Adopt **TruckFood-owned provider ports and adapters**, with one adapter per external integration and capability family. Application use cases depend on TruckFood contracts, never directly on vendor SDKs, response objects or identifiers.

The contracts must be capability-oriented rather than assuming every provider supports every operation. Providers declare supported operations, constraints, geographic coverage, freshness characteristics and data-use permissions. Unsupported capability must be explicit; adapters must not fabricate equivalent behaviour.

This ADR defines the contract design direction. It does not select, approve or activate any provider.

## 3. Integration boundaries

Keep the following capability families independently replaceable:

1. **Map display** — map styles, tiles or rendered map resources, attribution and display constraints.
2. **Geocoding** — forward and reverse geocoding, result precision and candidate ranking.
3. **Routing** — route calculation, alternatives, route geometry where permitted, travel estimates and supported vehicle parameters.
4. **Restriction/data** — road restrictions, closures, access conditions and source datasets.
5. **POI/business** — candidate places, business attributes, service categories and external references.
6. **TruckFood-owned data** — curated Locations, capabilities, access assessments, observations, trust and moderation.

A single vendor may implement multiple adapters, but the domain must not assume that its map, geocoding, routing and POI products share identical coverage, contracts or licensing.

## 4. Contract principles

Every provider contract must:

- use TruckFood-owned request, response, identifier and error types;
- expose only operations the adapter can genuinely support;
- validate and normalize external payloads at the integration boundary;
- preserve source identifiers as external references, never as canonical TruckFood IDs;
- return provenance metadata and source timestamps where available;
- distinguish missing, unknown, unsupported, partial, stale, conflicting and failed results;
- declare relevant geographic and vehicle-parameter coverage;
- declare data-use permissions before any result is persisted, cached or placed in an offline package;
- support bounded requests, timeouts, cancellation where practical and predictable resource use;
- avoid leaking credentials or raw sensitive request data into logs;
- be testable without live provider credentials through deterministic fixtures and contract tests.

Adapters must not silently convert unsupported vehicle restrictions into supported ones or claim a route is truck-safe merely because a provider returned a route.

## 5. Capability declaration

Each adapter should expose a versioned capability description with, at minimum:

| Capability area | Required declaration |
|---|---|
| Operations | Supported operations and explicit unsupported operations |
| Geography | Countries/regions, known gaps and coverage granularity |
| Vehicle support | Vehicle types and parameters actually accepted (height, width, length, gross weight, axle loads, trailer/configuration, ADR/hazmat and conditional rules) |
| Time dependence | Whether closures, time windows, conditional access and departure-time effects are supported |
| Output | Geometry, precision, alternatives, metadata and known omissions |
| Freshness | Provider update characteristics, source timestamp availability and refresh guidance |
| Limits | Quotas, rate limits, maximum bounds/radius/waypoints/payload and relevant request constraints |
| Reliability | Timeout expectations, known failure modes and service availability information where contractually supplied |
| Data rights | Display, transient processing, caching, persistent storage, transformation, derived data, redistribution and offline use |
| Attribution | Required notices, placement and licence references |
| Cost | Pricing unit, free-tier assumptions, metering dimensions and configured budget controls |
| Adapter version | Contract version, adapter version and provider API/product version |

Unknown capability must be represented as unknown, not false and not true. Capabilities may be region-specific and operation-specific. A global provider label such as "truck supported" is insufficient.

## 6. Core operation contracts

Exact programming-language types and endpoint paths are implementation decisions. The following operations define the minimum semantic contract.

### 6.1 Geocoding

Input: address/place text, optional geographic bias, language and bounded result limit.

Output: zero or more candidates containing normalized display label, coordinates, precision class, confidence where available, provider reference and provenance.

The contract must distinguish no match from provider failure and must not imply that a geocoded point is an approved truck entrance.

### 6.2 Routing

Input: origin, destination, optional waypoints, departure time, selected vehicle profile and routing preferences.

Output: route candidates with permitted geometry/reference, distance/time estimates, applied vehicle parameters, warnings, omitted/unsupported constraints, provider coverage context and provenance.

A successful route response is not a TruckFood safety certification. If the provider cannot apply a required vehicle parameter, the response must disclose that limitation. If critical vehicle data is missing, the application must not silently substitute a default that changes restriction evaluation.

### 6.3 Restriction/data retrieval

Input: bounded geographic area, route/corridor or external reference, vehicle context when supported, effective time and data-family filters.

Output: normalized restriction candidates with geometry/scope, rule attributes, direction, validity/effective periods, source reference, source timestamps, licence/use metadata and confidence/provenance.

Provider observations remain evidence until validated and evaluated through TruckFood's trust and restriction domain.

### 6.4 POI/business discovery

Input: bounded geographic area or proximity search, capability/service filters, language and result limit.

Output: candidate places with external reference, normalized attributes, source location precision, category mapping and provenance.

POI candidates must pass identity resolution/deduplication before becoming or enriching canonical TruckFood Locations. Provider records must not overwrite trusted TruckFood facts automatically.

### 6.5 Map display

The adapter declares how map resources are obtained and displayed, required attribution, allowed storage/offline behaviour, style/version constraints and geographic coverage. Map rendering resources are not interchangeable with routing or restriction data.

## 7. Canonical result envelope

Application-facing adapter results should carry a consistent envelope conceptually containing:

- operation and contract version;
- provider and adapter identity/version;
- outcome state: success, partial, empty, unsupported, unavailable, rate_limited or invalid_response;
- normalized result payload, when present;
- source/provenance references and relevant timestamps;
- coverage/limitations metadata;
- data-use permission classification;
- retry guidance where meaningful;
- correlation/request identifier safe for logs.

The exact serialized schema will be defined with the MVP API contracts. Do not collapse empty, unsupported, unavailable and partial into the same empty array.

## 8. Errors, resilience and cost controls

Adapters must map provider-specific failures into stable TruckFood error categories while preserving safe diagnostic detail.

At minimum distinguish invalid request, authentication/configuration failure, permission/licensing denial, quota/rate limit, timeout, network/provider unavailable, provider server error, invalid provider response and unsupported operation.

Use bounded timeouts, bounded retries only for suitable transient/idempotent operations, and backoff respecting provider retry guidance. Avoid retry storms. Circuit breaking, caching and background refresh may be introduced where measured need justifies them; they must not conceal stale data or violate licence terms.

Every billable operation should be measurable by provider, capability, operation, region and product use case without logging secrets or unnecessary precise personal coordinates. Budgets and rate limits must be enforceable centrally.

## 9. Data rights and lifecycle

Permission must be assessed separately for:

- displaying a result to a user;
- transient processing in memory;
- short-lived caching;
- persistent storage;
- transformation or enrichment;
- use in analytics or derived datasets;
- redistribution to other users;
- inclusion in downloadable offline packages.

The adapter capability/rights declaration must not be treated as legal advice or as a substitute for current contract review. Unknown or unapproved rights mean the result cannot be persisted, redistributed or included offline until resolved.

Store the applicable licence/terms reference, review date and decision with provider configuration/source registry. Expiry, deletion and refresh obligations must be enforceable.

OSM/ODbL obligations and commercial provider-specific restrictions must be evaluated independently. Combining sources does not automatically remove their individual obligations.

## 10. Provider selection and fallback

Provider selection is a product/operations policy, not a domain concern. The application layer may select an adapter based on operation, geography, required vehicle capability, cost budget, licensing and availability.

Fallback is allowed only when the alternative supports the required operation and constraints. The system must disclose reduced capability, coverage or freshness. A generic car route must never silently replace a truck route when truck restrictions are required.

Multiple sources may enrich or corroborate a fact, but conflicting evidence must be preserved under ADR-0006 and evaluated by TruckFood trust rules. Do not use majority vote as a substitute for source authority or legal validation.

## 11. Testing and conformance

Every adapter must pass:

1. contract tests for supported and unsupported operations;
2. schema/normalization tests using representative fixtures;
3. malformed, missing and unexpected-field handling;
4. provenance and timestamp preservation;
5. vehicle parameter mapping and explicit unsupported-parameter tests;
6. regional coverage and known-gap reporting;
7. error mapping, timeout and rate-limit behaviour;
8. cost-metering and safe logging checks;
9. licensing/cache/storage/offline permission tests;
10. deterministic tests that run without network access or paid credentials.

Live-provider smoke tests may supplement these checks but must be optional, budget-limited and never the only evidence of correctness.

## 12. Initial implementation sequence

1. Define language-neutral contract schemas and error/outcome enums.
2. Build a provider registry and capability declaration format.
3. Implement fake/in-memory adapters and contract tests before live integrations.
4. Select one initial map-display option and one geocoding option only after licence and cost review.
5. Evaluate routing candidates separately for Portugal truck-parameter coverage; do not assume the map provider is the routing provider.
6. Integrate TruckFood-owned POI/location records independently of external business search.
7. Add official restriction-data ingestion only when source access, update process and reuse rights are documented.
8. Add provider selection/fallback and budget enforcement after observability and capability checks exist.

## 13. Consequences

### Positive
- Protects the canonical domain from vendor lock-in.
- Allows providers to be mixed by capability, region and cost.
- Makes limitations, data rights and coverage visible rather than implicit.
- Enables deterministic tests without paid API access.
- Supports gradual adoption of open, commercial and official sources.

### Trade-offs
- Requires careful contract design and adapter conformance.
- Capability metadata and licensing decisions need ongoing maintenance.
- A provider-neutral contract cannot erase meaningful differences between providers.
- Fallback may be unavailable when no alternative meets safety, licensing or geographic requirements.

## 14. Open questions

- Choose the initial contract serialization and schema-versioning format.
- Define the provider registry/configuration storage model.
- Set measurable Portugal-first coverage requirements for truck routing and POI discovery.
- Decide which capabilities must be mandatory for each MVP use case.
- Complete current commercial and legal review for candidate providers.
- Define provider health/cost dashboards and operational alert thresholds.
- Define source-specific refresh and expiry schedules.
- Determine whether any provider permits the required persistent geometry and offline package use.

## 15. Implementation gate

Do not embed a live provider SDK in domain or presentation code, select a production provider, or persist external results until the TruckFood-owned contract, capability declaration, rights classification, cost controls and conformance tests are reviewed. This ADR defines direction and requirements; it does not claim any adapter, provider account, API integration or test suite has been implemented.
