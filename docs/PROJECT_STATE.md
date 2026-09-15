# TruckFood — Project State

**Version:** 1.0.0  
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

## 3. Repository Status

The repository started empty and now contains the initial project foundation and governance documentation.

### Confirmed files

- `README.md`
- `LICENSE`
- `PROJECT_CONSTITUTION.md`
- `PRODUCT_MANIFESTO.md`
- `docs/PROJECT_STATE.md`

## 4. Initial Technology Direction

The original technical direction remains:

- Mobile: React Native + Expo
- Web: Next.js + Vercel
- Backend/data: Supabase / PostgreSQL / Auth / Storage
- Maps: provider abstraction supporting OpenStreetMap/Mapbox/Google Maps or other suitable providers
- Source control: GitHub

These choices are provisional until the architecture and discovery phases validate them.

## 5. Product Domains Under Consideration

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

## 6. Critical Product Risks

1. Incorrect or stale road restriction information.
2. Presenting inferred route suitability as guaranteed safety.
3. Insufficient coverage of truck parking and services.
4. Licensing restrictions around map, traffic and road data.
5. Vendor lock-in.
6. Uncontrolled scope expansion.
7. Building UI before the data and domain model are stable.

## 7. Architecture Governance

The project will use:

- Architecture Decision Records (`docs/adr/`)
- Request for Comments (`docs/rfc/`)
- Domain specifications (`docs/specifications/`)
- Versioned diagrams (`docs/diagrams/`)
- This project-state document as the operational memory of the repository.

## 8. Development Rule

Each major phase must close with documentation, implementation where applicable, validation/tests, known limitations and a project-state update before the next major phase begins.

## 9. Current Phase

### Phase -1 — Discovery & Product Foundation

**Status:** In progress.

Current objectives:

- freeze the core mission;
- define the problem precisely;
- identify primary users and journeys;
- define product boundaries;
- identify data sources and licensing constraints;
- define the first domain model;
- define architecture principles;
- define MVP scope;
- define success criteria;
- only then begin implementation.

## 10. Immediate Next Steps

1. Document product vision and requirements.
2. Define driver personas and critical journeys.
3. Define the first truck/vehicle profile.
4. Define the Location/POI model.
5. Define restrictions and provenance model.
6. Define MVP boundaries.
7. Create first ADRs.
8. Define high-level architecture and system boundaries.
9. Define initial database model.
10. Validate the architecture before coding the application.

## 11. North Star Direction

The long-term product metric should focus on useful, trusted journey information rather than downloads alone.

Candidate North Star:

**Number of active, trusted locations and journey facts that are useful to professional drivers.**

The exact metric will be validated during product discovery.

## 12. Important Historical Decision

TruckFood has explicitly evolved from a restaurant discovery concept into a broader professional-driver journey platform. Restaurant discovery remains important, but the central problem is helping trucks **arrive, stop, eat, rest and continue** with better information.

This change must remain visible in future architecture and product decisions.
