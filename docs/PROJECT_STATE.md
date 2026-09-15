# TruckFood — Project State

**Version:** 1.2.0  
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
- `docs/adr/ADR-0001-product-direction.md`
- `docs/adr/ADR-0002-provider-abstraction.md`

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

A location can provide multiple services such as parking, food, fuel, showers, accommodation or other driver services.

### 5.3 Vehicle context

Vehicle characteristics are a first-class concern because physical and access suitability depends on the vehicle.

The final database schema remains open until an ADR validates the minimum viable vehicle model.

### 5.4 Trust

Critical information must preserve provenance, freshness and confidence. Official, provider, community and inferred information must remain distinguishable.

### 5.5 Safety boundary

The absence of a known restriction must never be interpreted as proof that no restriction exists.

TruckFood must not claim universally safe or legally compliant truck routing until data quality, coverage, licensing and validation justify that capability.

### 5.6 MVP boundary

The MVP focuses on useful discovery of locations, truck-relevant parking, food, community information and basic driver/vehicle context, while preparing the architecture for future restriction intelligence.

### 5.7 Provider abstraction

External maps, routing, geocoding, restriction and POI services will be isolated behind provider adapters. Provider-specific objects must not become the TruckFood domain model.

## 6. Discovery Research Findings

Current web research confirms:

- OpenStreetMap contains useful truck-related restriction structures including height, physical height, width, physical width, length, weight, axle load, HGV access, hazardous-material access and conditional restrictions.
- HERE Routing supports truck routing with vehicle parameters and considers legal, physical, hazardous-material and time-dependent restrictions.
- HERE also documents regional differences in truck restriction coverage, confirming that coverage itself must be part of TruckFood's trust model.
- TomTom also exposes truck vehicle types and vehicle dimensions/restrictions in its routing SDK.
- OpenStreetMap is licensed under ODbL and requires attribution; share-alike implications must be handled deliberately when distributing OSM-derived databases.

These findings support the provider-abstraction architecture but do not yet select a production provider.

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

The first product and provider/data discovery baseline is documented. The next work is country-specific source research and architecture preparation, not application coding.

## 12. Immediate Next Steps

1. Research Portugal road/restriction sources.
2. Research Portugal truck parking sources.
3. Research Portugal restaurant/POI sources.
4. Research European expansion sources.
5. Compare provider pricing and quotas.
6. Compare data storage/caching/commercial rights.
7. Finalise the minimum viable vehicle model through an ADR.
8. Finalise the Location/POI domain model.
9. Define provenance/trust data structures.
10. Define system architecture and provider boundaries.
11. Define initial database model.
12. Define API boundaries.
13. Define security and privacy requirements.
14. Only then begin implementation.

## 13. North Star Direction

The long-term product metric should focus on useful, trusted journey information rather than downloads alone.

Candidate North Star:

**Number of active, trusted locations and journey facts that are useful to professional drivers.**

The exact metric will be validated during product discovery.

## 14. Historical Decision

TruckFood has explicitly evolved from the original restaurant-discovery concept into a broader professional-driver journey platform. Restaurant discovery remains important, but the central problem is helping trucks **arrive, stop, eat, rest and continue** with better information.

This change must remain visible in future architecture and product decisions.
