# TruckFood — Project State

**Version:** 1.6.0  
**Status:** Active — Discovery / Foundation  
**Last Update:** 2026-09-15  
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

The product, provider/data, vehicle-model, Location/POI and initial domain/persistence discovery baseline is now documented. The minimum viable vehicle context and Location domain direction have been accepted through ADRs. ADR-0005 now establishes the canonical entity boundaries and provider-data separation before database implementation.

The next work is architecture/API/security and deeper commercial/licensing validation, not application coding.

## 12. Immediate Next Steps

1. Define provenance/trust data structures and explainable confidence.
2. Define restriction and effective-time representation.
3. Define system architecture and module boundaries.
4. Define provider adapter contracts.
5. Define API boundaries.
6. Define security/privacy requirements and Supabase RLS strategy.
7. Define spatial storage/query strategy and validate PostGIS direction.
8. Validate Portuguese official and concessionaire data sources in more depth.
9. Research European expansion and cross-border restriction sources.
10. Obtain/compare current commercial pricing and contractual terms for HERE and TomTom truck routing.
11. Compare OSM infrastructure/hosting approaches with commercial map hosting.
12. Define an initial operating-cost budget and request limits.
13. Validate the domain model against real driver journeys, parking and access cases.
14. Only then freeze the first database migration and begin implementation.

## 13. North Star Direction

The long-term product metric should focus on useful, trusted journey information rather than downloads alone.

Candidate North Star:

**Number of active, trusted locations and journey facts that are useful to professional drivers.**

The exact metric will be validated during product discovery.

## 14. Historical Decision

TruckFood has explicitly evolved from the original restaurant-discovery concept into a broader professional-driver journey platform. Restaurant discovery remains important, but the central problem is helping trucks **arrive, stop, eat, rest and continue** with better information.

This change must remain visible in future architecture and product decisions.
