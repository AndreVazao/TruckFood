# ADR-0008 — System Architecture & Module Boundaries

**Status:** Proposed — Discovery / Foundation  
**Date:** 2026-10-14  
**Decision:** TruckFood should begin with a modular, layered architecture with explicit domain, application, integration and delivery boundaries. The MVP should be a modular monolith, not a distributed microservice system.

## 1. Context

TruckFood is a professional truck-driver journey intelligence platform. Its core sequence is:

**Chegar → Parar → Comer → Descansar → Continuar**

The discovery baseline has established a TruckFood-owned domain model, provider abstraction, vehicle context, Location/POI, restrictions, temporal validity, provenance and explainable uncertainty.

The architecture must preserve these decisions without introducing operational complexity that the initial team and MVP cannot justify.

## 2. Decision

The initial architecture will use a **modular monolith** with explicit internal boundaries.

The first implementation should avoid independently deployed microservices, distributed transactions, message brokers and orchestration infrastructure unless a demonstrated requirement justifies them.

Deployment units may initially be few, while domain modules remain logically separated and independently testable.

## 3. Logical Layers

### 3.1 Delivery / Presentation

Responsibilities:
- mobile driver experience;
- web experience and administration;
- present domain results and uncertainty clearly;
- collect user actions and observations.

Rules:
- UI components must not contain provider-specific routing or data rules.
- The UI must not independently decide that a road or location is safe for a vehicle.
- Client-side validation improves usability but is not a security boundary.

### 3.2 Application

Responsibilities:
- coordinate use cases;
- authenticate and authorize operations through trusted server-side mechanisms;
- validate commands and inputs;
- coordinate domain logic and persistence;
- enforce request limits and idempotency where needed;
- produce auditable outcomes.

Example use cases:
- create/update driver vehicle profile;
- search locations and capabilities;
- submit a community observation;
- inspect a location's evidence and freshness;
- evaluate a known restriction against a vehicle/time context;
- manage moderation and source validation.

Application use cases must not depend directly on a specific map/routing vendor SDK.

### 3.3 Domain

Responsibilities:
- canonical TruckFood entities and value concepts;
- domain invariants and state transitions;
- vehicle context;
- Location and capabilities/services;
- restrictions, access rules and suitability;
- evidence, provenance, trust and temporal semantics.

Rules:
- domain types are owned by TruckFood;
- provider request/response objects must not leak into domain entities;
- unknown, conflicting, expired and insufficient-data states must remain representable;
- the domain must not treat absence of evidence as proof of safety.

### 3.4 Persistence

Responsibilities:
- persist canonical domain records;
- preserve evidence history and relevant timestamps;
- enforce database constraints and access policies;
- support spatial queries through an implementation selected by a later ADR;
- keep provider snapshots and external references distinct from canonical entities.

PostgreSQL/Supabase is the current candidate foundation, but exact schema, PostGIS use, indexes and Row Level Security policies require separate decisions and validation.

### 3.5 Integration / Provider Adapters

Responsibilities:
- integrate map, geocoding, routing, restriction and POI providers;
- translate provider-specific responses into explicit adapter outputs;
- expose provider capabilities, coverage limits and failures;
- enforce licensing, caching and request-budget constraints;
- keep external identifiers as references, never canonical TruckFood identity.

Each adapter must document supported operations, required inputs, coverage limitations, timeout/error behaviour, quotas, pricing assumptions and data-use restrictions.

### 3.6 Background / Operational Work

Responsibilities when justified:
- refresh eligible provider data;
- expire or flag stale evidence for review;
- process moderation queues;
- run bounded imports and reconciliation;
- generate operational diagnostics.

Background work must be introduced only for a demonstrated need. The MVP should prefer simple, observable jobs over a complex event-driven platform.

## 4. Initial Domain Modules

The first logical modules are:

1. **Identity & Access** — user identity, roles and authorization boundaries.
2. **Driver & Vehicle** — driver preferences and versioned vehicle profiles.
3. **Locations & Services** — canonical Location identity, capabilities, entrances and service relationships.
4. **Restrictions & Access** — scoped restrictions, access rules, directionality and effective time.
5. **Evidence & Trust** — source records, observations, provenance, freshness, conflicts and explainable presentation state.
6. **Discovery & Search** — search/filter use cases and provider coordination.
7. **Journey Intelligence** — future composition of route, vehicle, restrictions, locations and assessments; do not imply guaranteed safe routing before validation.
8. **Community & Moderation** — submissions, reviews, reports, validation and non-destructive lifecycle.
9. **Administration & Operations** — source management, moderation, diagnostics, quotas and audit visibility.

Modules are logical boundaries, not a commitment to nine separate deployable services. The first MVP may implement only a subset, with clear interfaces around future domains.

## 5. Dependency Rules

Allowed direction:

**Presentation → Application → Domain**

Application may call persistence and integration ports defined by TruckFood. Persistence and provider adapters implement those ports.

The domain must not depend on:
- React Native or Next.js;
- Supabase client/server SDKs;
- a particular map, routing or geocoding vendor;
- HTTP request/response objects;
- environment-specific deployment details.

Provider adapters may depend on vendor SDKs, but vendor types must be translated at the boundary.

No circular module dependencies should be introduced. Cross-module operations should use explicit application interfaces rather than reach into another module's internal tables or implementation.

## 6. Initial Deployment Shape

The initial target is deliberately simple:

- **Mobile client:** React Native with Expo, subject to later implementation validation.
- **Web/admin client:** Next.js, subject to later implementation validation.
- **Backend and data services:** Supabase/PostgreSQL is the current candidate; security policies and server-side responsibilities must be designed before production data is exposed.
- **External integrations:** provider adapters behind server-side boundaries wherever credentials, licensing, quotas or trust rules require control.
- **Repository and delivery:** GitHub with documented, reviewable changes and reproducible validation.

This is a proposed direction, not proof that any application code or production deployment already exists.

## 7. Security and Trust Boundaries

- Treat every client input and community submission as untrusted.
- Enforce authorization server-side and in database policies where applicable.
- Never ship privileged database/service credentials in mobile or browser clients.
- Keep provider secrets server-side.
- Apply least privilege to users, administrators, jobs and integrations.
- Record security-relevant administrative and moderation actions.
- Validate file uploads, image metadata, content size and access permissions before storing or serving user content.
- Rate-limit public search, submission and provider-backed operations to control abuse and cost.
- Do not expose private driver, vehicle or journey data through public Location APIs.
- Do not present unverified or incomplete restriction data as a guarantee of legal or physical access.

Exact policies belong in a dedicated security/RLS design.

## 8. Failure and Degradation Behaviour

The architecture must make provider failures visible and bounded.

- A provider timeout must not silently become an empty result that implies no restriction exists.
- Cached data must retain its source and observation/freshness metadata.
- Provider unavailability must not erase TruckFood-owned records.
- Partial results must be identified as partial when that affects user decisions.
- Retries must be bounded and respect provider quotas.
- External provider data must not overwrite community or official evidence without explicit reconciliation rules.
- Search or discovery may degrade gracefully; safety-critical unknowns must remain unknown.

## 9. Observability and Operations

The system should record enough operational information to diagnose failures without unnecessarily collecting personal data.

Initial needs:
- structured error categories;
- request correlation identifiers;
- provider latency, timeout and quota/error metrics;
- background-job status and retry count where jobs exist;
- audit records for privileged changes;
- health checks that distinguish application health from provider availability;
- documented backup/restore and data-retention decisions before production.

Logs must avoid secrets, authentication tokens and unnecessary sensitive journey details.

## 10. Testing Strategy

Architecture validation should include:
- domain unit tests for restriction, time and suitability semantics;
- application tests for authorization and use-case outcomes;
- adapter contract tests using controlled fixtures;
- persistence integration tests for constraints and access policies;
- API tests for validation, pagination, rate limits and error contracts;
- regression tests for conflicts, expired evidence and provider outages.

Tests must not depend on live commercial provider calls by default. Live integration checks, if introduced, must be explicitly bounded and budgeted.

## 11. MVP Scope Boundary

The MVP should implement only the minimum end-to-end slice that can be validated with drivers:
- driver identity and a basic vehicle profile;
- canonical locations and selected capabilities;
- location search/discovery;
- provenance and freshness for important claims;
- community observation/review submission with moderation safeguards;
- clear unknown/insufficient-data presentation.

Advanced autonomous truck routing, complex restriction evaluation, real-time fleet telemetry, microservices, AI-based safety claims and large-scale event infrastructure are not MVP prerequisites.

## 12. Consequences

### Positive
- Keeps initial operation and development manageable.
- Preserves clear boundaries for later extraction if real scaling needs appear.
- Protects the canonical domain from vendor lock-in.
- Makes security, failure behaviour and uncertainty explicit.
- Supports testing without constant live provider access.

### Trade-offs
- A modular monolith requires discipline to maintain boundaries.
- Some modules may later need extraction or separate scaling.
- Security, RLS, spatial queries and provider contracts still need dedicated decisions.
- The proposed stack remains subject to validation; this ADR does not authorize production implementation by itself.

## 13. Non-Goals

This ADR does not freeze:
- exact repository folder structure;
- exact framework versions;
- SQL tables or migrations;
- API endpoint paths or payload schemas;
- final Supabase RLS policies;
- PostGIS/index strategy;
- specific map or routing provider;
- queue/job technology;
- production deployment topology;
- autonomous or guaranteed-safe truck routing.

## 14. Follow-up Decisions

1. Define API boundaries and error contracts.
2. Define security, privacy, authorization and Supabase RLS.
3. Decide spatial storage and query strategy.
4. Define provider adapter contracts and capability declarations.
5. Define MVP migration and rollout plan.
6. Define data-family freshness and review policies.
7. Validate architecture against real driver journeys and operational constraints.
