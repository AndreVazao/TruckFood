# TruckFood — Project State

**Version:** 2.4.0  
**Status:** Active — Discovery / Foundation  
**Last Update:** 2026-10-30  
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

The product, provider/data, vehicle-model, Location/POI, persistence, provenance/trust, restriction/time, proposed system architecture, API boundaries, offline/vehicle-mode direction, security/privacy direction, preferred geospatial storage/query direction, provider adapter/capability contracts, cross-platform/vehicle-selection requirements and future fleet-management/live-location requirements are documented. ADR-0008 proposes a modular-monolith direction, ADR-0009 records API contract principles, ADR-0010 records staged offline package and vehicle-mode requirements, ADR-0011 proposes least-privilege authorization and RLS requirements, ADR-0012 proposes PostgreSQL/PostGIS subject to hosting/licensing/query validation, ADR-0013 defines TruckFood-owned provider contracts and capability declarations, and ADR-0014 defines cross-platform experience and explicit multi-profile vehicle selection. Physical spatial schema, concrete provider selection, exact client support matrix, fleet privacy/legal policy, tenancy implementation and live integrations remain open before implementation.

The next work is architecture/API/security and deeper commercial/licensing validation, not application coding.

## 12. Immediate Next Steps

1. Define versioned language-neutral provider contract schemas, outcome states and stable error categories.
2. Define fleet organization, membership, group, assignment, fleet-vehicle and subscription entitlement domain contracts.
3. Specify privacy-reviewed location-sharing session lifecycle, driver notice, permissions, off-duty cessation, retention and audit requirements.
4. Define fleet dashboard API scopes and source/freshness semantics for driver-phone GPS versus vehicle tracker telemetry.
5. Validate Portuguese/EU employment privacy obligations, lawful basis, controller/processor roles and any required impact assessment before any fleet pilot.
6. Define the provider registry/configuration and capability declaration format.
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
29. Only then freeze the first database migration and begin implementation.

## 13. North Star Direction

The long-term product metric should focus on useful, trusted journey information rather than downloads alone.

Candidate North Star:

**Number of active, trusted locations and journey facts that are useful to professional drivers.**

The exact metric will be validated during product discovery.

## 14. Historical Decision

TruckFood has explicitly evolved from the original restaurant-discovery concept into a broader professional-driver journey platform. Restaurant discovery remains important, but the central problem is helping trucks **arrive, stop, eat, rest and continue** with better information.

This change must remain visible in future architecture and product decisions.
