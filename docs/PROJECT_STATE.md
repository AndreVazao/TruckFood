# TruckFood — Project State

**Version:** 3.3.0  
**Status:** Active — Discovery / Foundation  
**Last Update:** 2026-11-12  
**Repository:** `AndreVazao/TruckFood`  
**Default Branch:** `main`

## 1. Current Mission

TruckFood is being designed as a platform for professional truck drivers to make better journey decisions.

The core problem is broader than finding restaurants: drivers need opportunities to avoid unsuitable roads and access points, find places where they can stop, park, eat and rest, and then continue their journey.

Core sequence:

**Chegar → Parar → Comer → Descansar → Continuar**

## 2. Product Direction

The initial product direction is a **Truck Intelligence layer** around existing mapping/routing capabilities.

TruckFood should combine:

- driver origin/destination;
- vehicle context;
- mapping/routing provider information;
- known restrictions;
- TruckFood rules;
- trusted locations and services;
- community observations;
- confidence and freshness of information.

TruckFood is not initially intended to replace mature navigation engines.

## 3. Discovery Documentation Completed

The discovery baseline now includes:

- `docs/VISION.md`
- `docs/REQUIREMENTS.md`
- `docs/USER_PERSONAS.md`
- `docs/USER_JOURNEYS.md`
- `docs/VEHICLE_PROFILE.md`
- `docs/LOCATION_MODEL.md`
- `docs/RESTRICTIONS_AND_TRUST.md`
- `docs/DATA_STRATEGY.md`
- `docs/MVP.md`
- `docs/ROADMAP.md`
- `docs/PROVIDER_RESEARCH.md`
- `docs/LICENSING.md`
- `docs/SOURCE_REGISTRY.md`
- `docs/DISCOVERY_FINDINGS.md`
- `docs/PORTUGAL_DATA_SOURCES.md`
- `docs/PROVIDER_COSTS.md`
- `docs/VEHICLE_PROFILE_ADR-0003.md`
- `docs/adr/ADR-0001-product-direction.md`
- `docs/adr/ADR-0002-provider-abstraction.md`
- `docs/adr/ADR-0004-location-poi-domain-model.md`
- `docs/adr/ADR-0005-initial-domain-persistence-model.md`
- `docs/adr/ADR-0006-provenance-trust-confidence-model.md`
- `docs/adr/ADR-0007-restriction-effective-time-model.md`
- `docs/adr/ADR-0008-system-architecture-module-boundaries.md`
- `docs/adr/ADR-0009-api-boundaries-error-contracts.md`
- `docs/adr/ADR-0010-offline-map-packages-vehicle-modes.md`
- `docs/adr/ADR-0011-security-privacy-authorization-rls.md`
- `docs/adr/ADR-0012-geospatial-storage-query-strategy.md`
- `docs/adr/ADR-0013-provider-adapter-contracts-capability-model.md`
- `docs/adr/ADR-0014-mvp-api-cross-platform-vehicle-experience.md`
- `docs/adr/ADR-0015-fleet-organizations-driver-groups-live-location.md`
- `docs/adr/ADR-0016-organization-membership-fleet-assignments.md`
- `docs/adr/ADR-0017-authorization-model-permission-matrix.md`
- `docs/adr/ADR-0018-database-logical-physical-model.md`
- `docs/specifications/DATABASE_SCHEMA_V1.md`
- `docs/specifications/API_CONTRACT_V1.md`
- `docs/specifications/openapi-v1.yaml`
- `docs/specifications/PROVIDER_CONTRACTS_V1.md`
- `docs/specifications/provider-contract-v1.schema.json`
- `docs/specifications/examples/provider-capability.fixture.json`
- `docs/specifications/examples/provider-result.fixture.json`
- `docs/specifications/PROVIDER_RUNTIME_V1.md`
- `src/truckfood_providers/__init__.py`
- `src/truckfood_providers/registry.py`
- `tests/test_provider_registry.py`
- `docs/specifications/PROVIDER_REGISTRY_V1.md`
- `docs/specifications/provider-registry-v1.schema.json`
- `docs/specifications/examples/registry.fixture.json`
- `docs/adr/ADR-0019-provider-registry-deterministic-selection.md`
- `.github/workflows/openapi-contract-validation.yml`

### 5.19 Provider registry and deterministic selection

ADR-0019 and the Provider Registry v1 specification define a registry manifest that references a separately versioned capability declaration by immutable reference and SHA-256 digest. Registry metadata covers adapter identity/version, environment, lifecycle, rights-review governance, operational health and configuration key names only; capability details remain authoritative in the declaration. Selection is eligibility-first and deterministic, with fail-closed handling for unknown/expired rights and unknown safety-critical vehicle support. No silent downgrade from truck routing to car routing is permitted. A synthetic fixture, JSON Schema and independent CI validation step have been added. This is documentation and structural validation only: there is no runtime registry, selector, health probe, live adapter or approved production provider.

### 5.20 Initial provider registry runtime (feature branch)

The feature branch `feat/provider-runtime-v1` introduces the first executable provider-runtime slice in `src/truckfood_providers`. It loads registry manifests, confines capability declaration paths to an explicit repository root, verifies SHA-256 pins and provider/adapter version identity, then applies deterministic eligibility-first selection. The selector fails closed on non-enabled lifecycle/environment, unapproved or overdue rights review, unknown/stale/unavailable health, unsupported operation/family/geography, missing required vehicle parameters and data rights not explicitly allowed. Eligible candidates are ordered by ascending priority and stable registry ID. It performs no network calls, dynamic imports, secret retrieval or adapter invocation.

Fifteen standard-library unit tests cover selection, digest/path/identity integrity, rights, vehicle capability, geography, health, lifecycle, environment, no-fallback behaviour and deterministic ordering. The CI workflow now runs these tests after schema validation. The sample registry fixture remains intentionally ineligible and synthetic.

This is an initial runtime foundation, not a production provider platform. Full runtime JSON Schema validation, regional geometry, conditional-rights evaluation, configurable health thresholds, quota/cost enforcement, trusted adapter registration/invocation and real provider integration remain outstanding. The branch requires a successful GitHub Actions run and review before merge. No provider is approved for production.

## 4. Repository Foundation

Confirmed foundation documents include:

- `README.md`
- `LICENSE`
- `PROJECT_CONSTITUTION.md`
- `PRODUCT_MANIFESTO.md`
- `docs/PROJECT_STATE.md`
- `docs/PRINCIPLES.md`
- `docs/HISTORY.md`

## 5. Product Decisions Now Established

### 5.1 Primary user

The professional truck driver is the highest-priority persona.

### 5.2 Central geographic entity

The central entity is **Location / POI**, not Restaurant.

ADR-0004 formalises Location as the stable TruckFood geographic entity. A Location can expose multiple capabilities/services such as parking, food, fuel, showers, toilets, accommodation, workshop or other driver services.

### 5.3 Vehicle context

Vehicle characteristics are a first-class concern because physical and access suitability depends on the vehicle.

ADR-0003 defines the minimum viable vehicle context: dimensions, gross weight, axle context, configuration, conditional ADR attributes and selected operational attributes.

### 5.4 Location suitability

Location existence, location capability and vehicle suitability are separate concepts. A restaurant may exist and offer parking while still being unsuitable for a particular truck because of access, dimensions, restrictions or temporal conditions.

### 5.5 Trust

Critical information must preserve provenance, freshness and confidence. Official, provider, community and inferred information must remain distinguishable.

### 5.6 Safety boundary

The absence of a known restriction must never be interpreted as proof that no restriction exists.

TruckFood must not claim universally safe or legally compliant truck routing until data quality, coverage, licensing and validation justify that capability.

### 5.7 MVP boundary

The MVP focuses on useful discovery of locations, truck-relevant parking, food, community information and basic driver/vehicle context, while preparing the architecture for future restriction intelligence.

### 5.8 Provider abstraction

External maps, routing, geocoding, restriction and POI services will be isolated behind provider adapters. Provider-specific objects must not become the TruckFood domain model.

### 5.9 Domain / persistence boundary

ADR-0005 establishes the first canonical domain model before database implementation.

The model separates:

- identity and user context;
- vehicle and journey context;
- Location and capabilities/services;
- access rules, restrictions and suitability assessments;
- observations, reviews, provenance and external references;
- provider snapshots outside the canonical domain.

TruckFood-owned canonical IDs are used for core entities. External provider IDs remain references and must not become primary identity.

Time-varying facts must preserve their relevant observation, receipt, validation and effective periods rather than silently rewriting historical evidence.

The initial model is deliberately implementation-neutral: exact SQL tables, PostGIS strategy, indexes, RLS, API contracts and provider schemas remain follow-up decisions.

### 5.10 Architecture direction

ADR-0008 proposes a modular monolith with explicit Presentation, Application, Domain, Persistence, Integration/Provider Adapter and optional Background Work boundaries. Domain logic remains independent of UI frameworks, Supabase SDKs and vendor-specific types. The first implementation should avoid microservices and unnecessary infrastructure. Security/RLS, spatial storage and provider contracts remain separate decisions.

### 5.11 API boundary direction

ADR-0009 proposes use-case-oriented, TruckFood-owned API contracts. The API must validate input, authorize protected operations, return stable response shapes, and distinguish empty results from partial results, provider failures, unknown data, conflicts and stale evidence. Exact endpoints, transport details, error codes, versioning and rate limits remain open.

### 5.12 Offline maps and vehicle modes

ADR-0010 records the product direction for user-managed offline area packages and an explicit travel-mode choice: car, truck or special/oversized load. Offline capabilities must be separated into map viewing, saved-place search, known restrictions, local route calculation and truck-aware evaluation. Each package must show coverage, data families, source attribution and last update. Lack of connectivity means no live traffic or guaranteed awareness of new/temporary restrictions. Full offline truck routing remains conditional on provider licensing, local data quality and validation.

### 5.13 Security, privacy and authorization

ADR-0011 proposes a least-privilege, deny-by-default model across APIs, persistence, community content, administration and offline storage. Public location discovery must expose only intentionally public fields; private profiles, vehicle data and journeys must be owner-scoped. User submissions remain untrusted until appropriately reviewed. If Supabase is selected, RLS must be designed per operation and tested against anonymous access, cross-user access, ownership changes and privilege escalation. Privileged secrets must remain server-side. Offline caches and sync must respect account boundaries and must not trust cached permissions. These are documented requirements, not yet implemented security controls.

### 5.14 Geospatial storage and queries

ADR-0012 proposes PostgreSQL/PostGIS as the preferred spatial persistence direction, conditional on confirming managed-hosting support, version, cost, backup/restore and deployment constraints. EPSG:4326 is the canonical interchange reference, with explicit longitude/latitude ordering and preservation of source precision/uncertainty. Location sites, entrances, parking/service areas, roads, restrictions and coverage regions require distinct spatial representations; a site pin is not a truck entrance. Nearby, corridor, restriction-intersection, viewport and coverage queries are required progressively. Spatial proximity does not establish vehicle access or safety. Geometry storage, provider licensing, ODbL obligations, RLS and offline package rights must be validated before migrations. PostGIS is a proposed direction, not an enabled extension or implemented feature.

### 5.15 Provider adapters and capability contracts

ADR-0013 proposes TruckFood-owned provider ports and adapters for map display, geocoding, routing, restriction/data, POI/business and TruckFood-owned data. Application/domain contracts must not expose vendor SDK types or identifiers as canonical entities. Each adapter must declare supported operations, geographic coverage, actual vehicle parameters, time-dependent support, output/freshness limitations, quotas, costs, attribution and separate rights for display, transient processing, caching, persistent storage, transformation, redistribution and offline use. Unsupported, empty, partial, stale, rate-limited and unavailable outcomes must remain distinguishable. Fallback is permitted only when the alternative meets the required capability and rights; a generic car route must never silently replace a required truck route. Deterministic fixture-based contract tests must work without paid credentials. These are architecture requirements; no provider adapter or live integration is claimed implemented.

### 5.16 Cross-platform experience and vehicle selection

ADR-0014 establishes responsive Android phone, Android tablet and PC/web experiences using shared domain and API contracts. The design must adapt to different Android versions, manufacturers, screen sizes, memory/performance levels, input methods and connectivity; exact minimum OS/browser support must be evidence-based and tested before being promised. Vehicle selection is a critical journey input, not a generic mode toggle: drivers may maintain multiple profiles (for example Jeep/4x4, van, rigid truck, tractor with semi-trailer, multi-trailer combination and special/oversized load) and explicitly select the correct profile per journey. Profiles must represent complete vehicle/combination dimensions, gross mass, axle configuration and loads, trailers, applicable ADR attributes and permit context. Unknown, missing, unconfirmed and not-applicable values remain distinct; missing safety-critical values must never be replaced by defaults. Vehicle-sensitive evaluations must disclose which attributes were actually applied and preserve the profile version/snapshot used for historical journeys. These are design requirements, not implemented compatibility or vehicle-evaluation features.

### 5.17 Future fleet management and driver-phone live location

ADR-0015 prepares a future B2B multi-tenant fleet capability: business organizations, subscription entitlements, fleet groups, role-scoped administrators/dispatchers, driver memberships, assignments, company fleet vehicles and a PC/web management dashboard. Drivers may use the ordinary TruckFood app on their own Android phones to share phone GPS during an explicitly disclosed, purpose-bound and time-limited work/assignment session, subject to approved privacy/legal policy. The dashboard must identify this source as driver-phone location, show last-update/freshness/accuracy and distinguish it from genuine vehicle-mounted tracker telemetry. Phone position is not proof that the truck is physically at that point, nor that the driver is with or away from the vehicle. No automated accusation, discipline or abandonment conclusion may be based on proximity, stale coordinates, missing updates or permission/device failures. Tenant, group, assignment and role isolation, visible session controls, off-duty cessation, revocable device sessions, minimal retention, audit trails and GDPR/employment-law review are release gates. The capability is future architecture only: no subscriptions, GPS tracking, background service or fleet dashboard is implemented.

### 5.18 Organization, membership, groups, fleet assets and assignments

ADR-0016 proposes a complete multi-tenant fleet domain. User Account and personal Driver Profile remain independent of organizations; one user may hold explicit memberships in multiple organizations. Organization Membership, invitation, scoped role grants, group membership and operational Assignment are distinct relationships with separate lifecycles. Groups belong to one tenant and cannot grant access without active organization membership. Candidate roles are owner, fleet_admin, dispatcher, safety_manager, driver and viewer, but a final server-enforced permission matrix remains open.

ADR-0016 also separates a reusable, versioned technical Vehicle Profile from an organization-owned Fleet Vehicle asset and from a time-bounded driver/vehicle/group/task Assignment. Assignment overlap/exclusivity is policy-driven rather than assumed universally; history is auditable and journey records preserve the exact profile snapshot used. Subscription, Plan, Entitlement and Usage are separate from authorization: payment status alone does not grant resource access. Offboarding and organization closure revoke access and active sharing, preserve required history and do not delete a user's personal account. Location sharing remains purpose-bound, visible, time-limited and assignment-aware under ADR-0015. This is proposed domain architecture only; none of these fleet capabilities are implemented.

### 5.19 Authorization model and permission matrix

ADR-0017 proposes a permission-based, deny-by-default authorization model that extends ADR-0011 and ADR-0016. It defines stable permission namespaces for organization administration, memberships, groups, fleet vehicles, vehicle profiles, assignments, location sessions/history, compliance, audit and subscription entitlements. Authorization combines authenticated subject, active organization membership, explicit permission, resource scope (self, assigned, group, organization, public or exceptional platform), resource lifecycle and contextual conditions. Roles are permission bundles, not trusted client claims.

A conservative initial role matrix is documented for owner, fleet_admin, dispatcher, safety_manager, driver and viewer. It deliberately denies ordinary access to historical location by default; live location requires a valid, visible, purpose-bound session and matching scope. Sensitive fields, reads, exports and support access require minimization and audit. Revocation, offline caches, background jobs, object storage, webhooks and exports must observe the same tenant boundaries. ADR-0017 also defines a 20-case minimum security test matrix and implementation gates. The matrix remains proposed pending product and privacy/legal review; no RLS, authorization guard, audit pipeline or security test is claimed implemented.


### 5.20 Logical and physical database model

ADR-0018 translates the established domain into proposed relational table families for identity/personal driver context, organizations/memberships/groups, vehicle profiles and immutable versions, fleet assets/assignments, journeys/routes/snapshots, locations/services/entrances/access, restrictions and temporal applicability, evidence/provenance/community, location-sharing sessions/telemetry, plans/entitlements/usage and audit/operational records. It defines canonical UUID identity, tenant-aware composite foreign keys, temporal conventions, candidate constraints/indexes, retention/deletion principles, migration sequencing and validation gates.

The design prefers PostgreSQL with PostGIS conditional on hosting/version/cost, licensing, backup/restore and query validation. It explicitly separates technical vehicle profiles from fleet assets and historical journey snapshots; separates location capability from access and suitability; and requires tenant isolation across indirect child records. Sensitive phone-location samples require a valid visible purpose-bound session and restricted retention/access. These are proposed database decisions only: no SQL schema, migration, Supabase configuration, PostGIS extension, RLS policy, trigger or persistence implementation has been applied.


### 5.21 First database schema specification

`docs/specifications/DATABASE_SCHEMA_V1.md` narrows ADR-0018 into a proposed first-release persistence contract. It specifies candidate columns, types, constraints and indexes for user profiles, personal vehicle profiles and immutable versions, location/service/capability records, geometry/provenance, external references, observations, optional reviews and optional journey snapshots. It distinguishes included foundations from deferred fleet, subscription, live-location, full restriction-engine and offline-package domains.

The specification defines metric canonical units, UTC timestamps, explicit unknown/not-applicable semantics, immutable vehicle versions and journey snapshots, public/private data boundaries, owner isolation and migration gates. Reviews and journey history remain explicit scope decisions; PostGIS and Supabase remain conditional. It is a specification only: no SQL, migration, database instance, RLS policy, seed data or application persistence has been created or deployed.


### 5.22 API contract v1

`docs/specifications/API_CONTRACT_V1.md` defines the proposed TruckFood-owned HTTP API v1 shared by Android phone/tablet and PC/web clients. It establishes versioning, authentication context, common response/error envelopes, stable error codes, pagination, idempotency, concurrency, endpoint catalogue, representative payloads, domain states, validation/security/observability requirements and a 25-case minimum contract test suite.

The proposed MVP surface covers current-user profile, personal vehicle profiles and immutable versions, published location/service discovery, community observations and optional reviews/journey history. Fleet, subscription and live-location namespaces are explicitly deferred. Provider failures, partial results, stale/conflicting evidence and unknown vehicle/access attributes remain distinguishable. This is a contract specification only: no routes, controllers, OpenAPI file, middleware, database queries, provider adapters or deployed service have been implemented.

### 5.23 OpenAPI 3.1 contract specification

`docs/specifications/openapi-v1.yaml` translates the proposed API contract into an OpenAPI 3.1 document. It describes the initial system, driver, personal vehicle-profile/version, published location/service/evidence-summary, community observation/report and conditional review/journey operations; bearer authentication; shared success/error envelopes; pagination, idempotency and concurrency headers; and reusable domain schemas.

The specification intentionally excludes future organization/fleet routes. Review and journey operations are marked conditional and must be enabled only if approved for the release. The illustrative server URL uses the reserved `.invalid` domain and is not a deployment endpoint. The YAML has been committed and re-fetched from GitHub to verify its stored contents, but has not yet been run through an OpenAPI parser/linter or contract-test suite. It remains a documentation artifact: no API implementation, route, middleware, database or deployment exists.

### 5.24 Provider contract v1 and automated validation gate

`docs/specifications/PROVIDER_CONTRACTS_V1.md` defines two TruckFood-owned provider records: versioned capability declarations and normalized operation results. The machine-readable `provider-contract-v1.schema.json` (JSON Schema Draft 2020-12) captures capability families, operation support, geographic coverage, vehicle-parameter support, freshness, separate data-use rights, attribution, cost/reliability metadata, provenance, normalized outcomes and stable provider error categories.

Two deterministic fixture records are included under `docs/specifications/examples/`. They are explicitly synthetic and do not claim real provider coverage, licensing approval or live integration. The contract preserves the distinction between empty, partial, unsupported, unavailable, rate-limited and invalid responses. Unknown capability or data rights must fail closed for safety-sensitive and persistence/offline decisions.

`.github/workflows/openapi-contract-validation.yml` adds a GitHub Actions validation gate: Redocly CLI (pinned) lints the OpenAPI 3.1 document, and Python 3.12 with a pinned JSON Schema validator checks the provider schema and all fixture files. The workflow is configured for relevant pushes, pull requests and manual dispatch. It has been committed but no successful run has yet been confirmed in this project state. It validates specification artifacts only; it does not call providers or implement application adapters.

## 6. Discovery Research Findings

Current web research confirms:

- OpenStreetMap contains useful truck-related restriction structures including height, physical height, width, physical width, length, weight, axle load, HGV access, hazardous-material access and conditional restrictions.
- HERE Routing supports truck routing with vehicle parameters and considers legal, physical, hazardous-material and time-dependent restrictions.
- HERE also documents regional differences in truck restriction coverage, confirming that coverage itself must be part of TruckFood's trust model.
- TomTom also exposes truck vehicle types and vehicle dimensions/restrictions in its routing SDK.
- OpenStreetMap is licensed under ODbL and requires attribution; share-alike implications must be handled deliberately when distributing OSM-derived databases.

### Portugal-specific findings

- IMT is a primary regulatory source for dangerous-goods restrictions and ADR material.
- Infraestruturas de Portugal is a primary candidate for national-road operational information and time-dependent traffic regimes.
- A current 2026 example shows why temporal rules matter: restrictions for heavy goods vehicles on Porto's VCI enter into force on 15 September 2026.
- Portuguese road-network legislation explicitly recognises service areas, rest areas and parking areas.
- Road concessionaires publish useful service-area details, including heavy-vehicle parking and driver facilities at some locations.
- There is no single identified Portuguese nationwide feed that is sufficient for TruckFood's complete parking/food/service database.
- Portugal is therefore a viable first market, but requires a multi-source strategy with explicit provenance and validation.

### Provider-cost findings

- Google Maps Platform uses SKU-based pay-as-you-go pricing; public list prices include free monthly usage for several Routes, Geocoding and Places SKUs, after which usage is charged per 1,000 events.
- Mapbox offers free tiers and usage-based pricing for Directions, Search and Geocoding, with different licensing/data-use implications for temporary versus permanent geocoding.
- HERE and TomTom remain technically strong truck-routing candidates, but exact production cost and contractual terms must be evaluated against the intended commercial plan and volume.
- Cost must be evaluated as total operating cost, not only API request price.

### Vehicle-model findings

Portuguese legislation defines and regulates dimensions, gross weight and axle-weight concepts separately. The research therefore confirms that TruckFood cannot safely reduce the vehicle profile to a single generic "truck size" value.

ADR is treated as a conditional vehicle/journey capability rather than a mandatory field for every driver.

### Location-model findings

- A real-world truck-relevant place commonly combines several services; therefore Location must not be a single-category POI enum.
- Location capabilities should be represented independently from access/suitability.
- Access may differ by vehicle, entrance, service and time.
- Parent locations may contain child service records when service-level precision is required.
- Provider identifiers remain references to a TruckFood-owned Location identity.
- Community observations are evidence with timestamps and confidence, not automatic authoritative truth.
- Suitability should support `suitable`, `suitable_with_conditions`, `unsuitable_known`, `unknown`, `temporarily_unavailable` and `insufficient_data` rather than forcing a binary answer.
- OpenStreetMap tagging guidance supports representing restaurants, fuel stations and related facilities separately and includes fields such as opening hours, HGV access and maximum height, reinforcing the separation between Location, capability and access.

## 7. Provider Strategy

Conceptual provider boundaries:

1. Map Provider
2. Geocoding Provider
3. Routing Provider
4. Restriction/Data Provider
5. POI/Business Provider
6. TruckFood-owned/community data

The project must compare Portugal and European coverage, cost, quotas, licensing, caching/storage rights, data quality and failure behaviour before freezing a provider.

## 8. Product Domains Under Consideration

- Identity
- Vehicle
- Journey / Routing
- Restrictions
- Locations / POIs
- Parking
- Food / Restaurants
- Rest
- Community
- Reviews
- Photos
- Search
- Notifications
- Analytics
- Administration
- Trust / Data Provenance

## 9. Critical Product Risks

1. Incorrect or stale road restriction information.
2. Presenting inferred route suitability as guaranteed safety.
3. Insufficient coverage of truck parking and services.
4. Licensing restrictions around map, traffic and road data.
5. Vendor lock-in.
6. Uncontrolled scope expansion.
7. Building UI before the data and domain model are stable.
8. Designing a vehicle model that is either too weak for real-world use or unnecessarily complex for the MVP.
9. Assuming that technically accessible external data is commercially reusable.
10. Treating provider coverage as universal when it is not.
11. Allowing provider request volume to become an uncontrolled operating cost.
12. Treating gross weight as a substitute for axle-specific restrictions.
13. Entity duplication/conflicts when multiple providers describe the same physical location.
14. Allowing time-varying facts to overwrite historical evidence without preserving their provenance and effective period.

## 10. Architecture Governance

The project will use:

- Architecture Decision Records (`docs/adr/`)
- Request for Comments (`docs/rfc/`)
- Domain specifications (`docs/specifications/`)
- Versioned diagrams (`docs/diagrams/`)
- This project-state document as the operational memory of the repository.

## 11. Current Phase

### Phase -1 — Discovery & Product Foundation

**Status:** In progress.

The product, provider/data, vehicle-model, Location/POI, persistence, provenance/trust, restriction/time, proposed system architecture, API boundaries, offline/vehicle-mode direction, security/privacy direction, preferred geospatial storage/query direction, provider adapter/capability contracts, cross-platform/vehicle-selection requirements, future fleet organization/membership/group/asset/assignment domain and proposed authorization permission matrix are documented. ADR-0008 proposes a modular-monolith direction, ADR-0009 records API contract principles, ADR-0010 records staged offline package and vehicle-mode requirements, ADR-0011 proposes least-privilege authorization and RLS requirements, ADR-0012 proposes PostgreSQL/PostGIS subject to hosting/licensing/query validation, ADR-0013 defines TruckFood-owned provider contracts and capability declarations, and ADR-0014 defines cross-platform experience and explicit multi-profile vehicle selection. Physical spatial schema, concrete provider selection, exact client support matrix, fleet privacy/legal policy, tenancy implementation and live integrations remain open before implementation.

The next work is to obtain a successful automated specification-validation run, resolve any lint/schema findings, then continue architecture/API/security and deeper commercial/licensing validation; provider integrations and application coding remain gated.

## 12. Immediate Next Steps

1. Obtain and review a successful run of `.github/workflows/openapi-contract-validation.yml`; fix all OpenAPI lint and provider-fixture/schema findings.
2. Review ADR-0016 and ADR-0017 together; approve the organization domain, role/permission matrix, scope rules and open questions before physical schema design.
3. Specify privacy-reviewed location-sharing session lifecycle, driver notice, permissions, off-duty cessation, retention and audit requirements.
4. Define fleet dashboard API scopes and source/freshness semantics for driver-phone GPS versus vehicle tracker telemetry.
5. Validate Portuguese/EU employment privacy obligations, lawful basis, controller/processor roles and any required impact assessment before any fleet pilot.
6. Define the provider registry/configuration lifecycle, review/expiry policy and capability declaration storage format based on `PROVIDER_CONTRACTS_V1.md`.
7. Specify MVP API request/response schemas, authorization matrix and error catalog.
8. Define client technology options and a realistic Android/OEM/screen/performance and PC/browser support matrix using target-user/device evidence.
9. Prototype responsive UX and vehicle-profile selection flows for phone, tablet and PC.
10. Refine the vehicle model for full combinations, multiple trailers, axle-group loads, load dimensions and jurisdiction-specific permits/ADR attributes.
11. Define vehicle-profile completeness rules, active journey selection and immutable historical profile snapshots.
12. Define cross-platform client capability negotiation, local database migrations and offline package compatibility.
13. Validate PostgreSQL/PostGIS availability, version, hosting cost, backup/restore and local-development parity.
14. Prototype nearby, route-corridor and restriction-intersection queries using representative Portugal-first sample data; compare geometry/geography choices and query plans.
15. Define the physical Location, entrance, service-area and restriction geometry relationships, including precision/quality metadata.
16. Build fake/in-memory provider adapters and deterministic conformance tests before live integrations.
17. Validate the proposed security model against the eventual schema; define RLS policies and executable security tests if Supabase is selected.
18. Evaluate offline-capable map/routing options and licensing, including source-specific caching and redistribution rights.
19. Define measurable Portugal-first geographic and truck-parameter coverage requirements.
20. Define an MVP migration and rollout plan.
21. Define freshness/review policies by data family.
22. Validate Portuguese official and concessionaire data sources in more depth.
23. Research European expansion and cross-border restriction sources.
24. Obtain/compare current commercial pricing and contractual terms for HERE and TomTom truck routing.
25. Compare OSM infrastructure/hosting approaches with commercial map hosting.
26. Define an initial operating-cost budget, quotas and request limits.
27. Validate the architecture/domain model against real driver journeys, parking and access cases.
28. Review privacy notice, retention, export/deletion, secret rotation and incident-response requirements.
29. Review and approve the first-release table scope in `docs/specifications/DATABASE_SCHEMA_V1.md`, especially journeys, reviews and full vehicle-combination support.
30. Review and freeze the API endpoint scope, error catalog, auth requirements and domain enums in `docs/specifications/API_CONTRACT_V1.md`.
31. Validate `docs/specifications/openapi-v1.yaml` with an OpenAPI 3.1 parser/linter; reconcile any schema or semantic differences against `API_CONTRACT_V1.md`.
32. Expand the contract CI gate with deterministic OpenAPI/API semantic tests after the initial linter and JSON Schema validation pass, without activating paid services.
33. Validate identity UUID mapping, PostgreSQL/PostGIS hosting, measurement semantics, geometry/SRID and source licensing.
34. Produce reviewed SQL migrations with rollback/recovery notes only after those gates pass.
35. Run clean-database, integrity, owner-isolation, anonymous-public-read and privilege-escalation tests before non-production deployment.
36. Only then freeze the first database migration and begin implementation.

## 13. North Star Direction

The long-term product metric should focus on useful, trusted journey information rather than downloads alone.

Candidate North Star:

**Number of active, trusted locations and journey facts that are useful to professional drivers.**

The exact metric will be validated during product discovery.

## 14. Historical Decision

TruckFood has explicitly evolved from the original restaurant-discovery concept into a broader professional-driver journey platform. Restaurant discovery remains important, but the central problem is helping trucks **arrive, stop, eat, rest and continue** with better information.

This change must remain visible in future architecture and product decisions.
