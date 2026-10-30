# ADR-0012 — Geospatial Storage and Query Strategy

- **Status:** Proposed
- **Date:** 2026-10-30
- **Decision owners:** TruckFood project
- **Scope:** Locations, entrances, services, road restrictions, route references, spatial search and offline data
- **Depends on:** ADR-0004, ADR-0005, ADR-0008, ADR-0010 and ADR-0011

## 1. Context

TruckFood is a geographic journey-intelligence product. Its domain includes physical Locations, service capabilities, vehicle-specific entrances/access, road restrictions, route segments and coverage areas. These are not all simple latitude/longitude points: facts may apply to points, lines, areas, road segments, directions or entrances.

The system needs nearby search, route-corridor discovery, restriction intersection, service-area coverage and map viewport queries. It must preserve provider abstraction, provenance, licensing, privacy and spatial uncertainty.

## 2. Decision direction

Adopt **PostgreSQL with PostGIS as the preferred geospatial persistence direction**, subject to confirming the selected hosting plan, extension availability, version, operational cost, backup/restore behaviour and deployment constraints before implementation.

PostGIS is preferred because spatial and ordinary relational data can be queried together, spatial indexes and common geometry operations are available, and a separate spatial database service is not justified at this stage.

This is a proposed direction. It does not mean PostGIS is enabled or that a database schema exists. If the selected managed platform cannot support required PostGIS capabilities on acceptable terms, reassess before implementation.

## 3. Canonical coordinate reference

- Use WGS 84 / EPSG:4326 as the canonical interchange reference for geographic positions exchanged with APIs and common map providers.
- Explicitly define coordinate order at every boundary: longitude (X), latitude (Y) for PostGIS geometry construction and GeoJSON coordinates.
- Validate latitude/longitude ranges; reject malformed, non-finite or out-of-range values.
- Record geocoding source, result precision and confidence. Do not imply rooftop precision when the source only supports street-, locality- or area-level precision.
- Preserve source precision and uncertainty metadata.
- Any projected/local coordinate system used for specialised calculations must be explicit, documented and transformed at a controlled boundary. Never mix coordinate reference systems silently.

## 4. Spatial representation by domain concept

Use the simplest geometry that accurately represents the real-world fact. This is conceptual mapping, not a frozen SQL schema.

| Domain concept | Preferred representation | Notes |
|---|---|---|
| Location/site | Point, optionally supported by a site-boundary polygon | A discovery anchor is not the exact entrance |
| Entrance/access point | Separate Point | Distinct from site centre or public map pin |
| Parking/service area | Polygon when reliable boundary data exists; otherwise point plus explicit uncertainty | Never invent boundaries from a pin |
| Road/route segment | LineString or provider-independent network reference | Store only when rights and product need justify it |
| Restriction | Point, line or polygon matching its actual scope | Also retain direction, applicability, effective time and provenance |
| Coverage/offline region | Polygon or bounded region definition | Include source, version and coverage limitations |
| Journey origin/destination | Point or appropriately coarse reference | Private user data |
| Route result | Provider reference and/or permitted normalized geometry | Subject to licensing and retention rights |

A Location may have several entrances and services. A site point is not interchangeable with a truck entrance. Access suitability must be evaluated against the relevant entrance/service and vehicle context, not merely the site's centroid.

## 5. Geometry and geography semantics

Use PostGIS types deliberately:

- The geography type is a strong default for global earth-surface distance and radius calculations where metre-based distance semantics are required.
- The geometry type is appropriate for topology, intersection, containment, line/polygon processing and workflows using a defined projected coordinate system.
- EPSG:4326 geometry is suitable for canonical geographic storage and interoperable GeoJSON, but its distance/area calculations use angular units. Degrees must never be treated as metres.
- Transform to a suitable projected CRS for calculations requiring local planar accuracy; document the CRS and operating region.
- Do not select a type merely because a provider returns it. The persistence adapter owns conversion and validation.

The exact geometry/geography choice per entity remains open until query prototypes are measured.

## 6. Required spatial queries

Introduce these use cases progressively:

1. Nearby published Locations with bounded radius and stable pagination.
2. Nearby Location filtering by capability/service and publication state.
3. Truck parking and service discovery along a route corridor.
4. Restrictions intersecting or relevant to a route/segment, respecting direction and effective time.
5. Point-in-area checks where the boundary is trustworthy.
6. Entrance/access-point discovery associated with a Location.
7. Map viewport queries using bounded bounding boxes and server-side result limits.
8. Coverage checks that can report missing/incomplete geographic or data-family coverage.

Spatial proximity alone does not establish reachability, vehicle suitability, opening or availability. These remain separate domain evaluations.

## 7. Indexing and query performance

- Use appropriate PostGIS spatial indexes, normally GiST, on spatial columns used in filters or joins.
- Use index-aware predicates and bounding-box prefilters where appropriate; validate query plans with representative data.
- Combine spatial filters with capability, publication, country, freshness and access-state filters.
- Bound radius, result count, viewport size and query cost at the API boundary.
- Use deterministic ordering and cursor/keyset pagination where practical.
- Avoid speculative indexes on every geometry. Measure query plans and write overhead first.
- Record representative query plans and performance thresholds before scaling or adding caching.

Exact indexes, partitioning and materialized views remain implementation decisions.

## 8. Accuracy, provenance and safety

Every critical spatial fact must retain provenance and relevant timestamps under the existing trust and effective-time decisions.

The model/API must distinguish source-reported geometry from normalized geometry; official/surveyed positions from provider-geocoded or community-reported positions; exact points from approximate points/areas; and current, stale, conflicting or unknown spatial evidence.

Do not silently snap, simplify, merge or move geometry in ways that change operational meaning. Derived geometry must be traceable to its inputs and method.

A restriction geometry does not by itself define legal applicability. Vehicle class, direction, time, exceptions, source authority and effective dates remain separate rule data.

**Absence of a spatial record is not evidence that a road or access is unrestricted.** Query results must preserve unknown and incomplete-coverage states.

## 9. Provider and licensing boundary

- Provider geometry enters through the relevant provider adapter.
- Provider geometry types and identifiers must not become canonical domain contracts.
- Store raw provider payloads or full geometries only when the applicable licence and contract permit it.
- Distinguish transient processing from persistent caching, redistribution, offline packaging and derived-database use. Permission for one does not imply permission for the others.
- Keep source attribution and licence obligations attached to the relevant dataset/package.
- OSM-derived data must be handled under ODbL obligations, including attribution and applicable share-alike considerations. Legal/licensing review is required before distributing derived databases or offline packages.
- Where persistent storage is not permitted, retain only allowed references or derived results, and apply expiry/deletion requirements.

No provider or dataset is approved for unrestricted storage or redistribution by this ADR.

## 10. Privacy and access control

Spatial data can expose sensitive routines and personal movements.

- Separate public Location geometry from private user journey/origin/destination geometry.
- Apply ADR-0011 authorization and RLS requirements to private spatial rows and any views/functions that expose them.
- Do not include private coordinates in public search, analytics, error messages or ordinary logs.
- Use minimised/coarsened analytics data when exact coordinates are unnecessary.
- Define retention and deletion for journey geometry before production.
- Spatial indexes, views, RPCs and map endpoints must not bypass ownership rules.

## 11. API and GeoJSON boundary

Expose provider-independent geographic values. GeoJSON is a suitable interchange format for supported geometry responses when coordinate order, CRS assumptions, precision and geometry limits are explicit.

Validate geometry type, coordinate ranges, vertex counts and payload size. Reject unsupported or invalid geometry rather than silently coercing it. Avoid returning unnecessary high-resolution geometry to mobile clients. Keep database-specific spatial expressions inside persistence/query adapters.

API responses must distinguish no matching records from unavailable spatial data, incomplete coverage and provider failure, consistent with ADR-0009.

## 12. Offline and mobile implications

Offline packages may contain permitted map geometry, published Location/service records, known restrictions and coverage metadata, subject to ADR-0010 and source rights.

- Package manifests identify geographic bounds, included data families, source attribution, versions and last update.
- Simplify or tile offline geometry only where transformation preserves intended use and does not imply greater accuracy.
- State local spatial search capability separately from online PostGIS query capability.
- Offline results expose age, coverage and known limitations.
- Private journeys and vehicle-specific evaluations follow ADR-0011 local-device protections and sync rules.
- Offline packages must not imply awareness of new temporary restrictions or live traffic after disconnection.

## 13. Validation before implementation

Before the first migration, validate:

1. PostGIS availability/version on the selected managed database and hosting plan.
2. Backup, restore, migration and local-development parity for spatial columns/indexes.
3. Expected storage, query volume and hosting cost for Portugal-first coverage.
4. Provider and OSM licensing for storage, transformation, caching and offline distribution.
5. Representative query plans for nearby search, corridor search and restriction intersection.
6. RLS behaviour for private spatial records, views and RPCs.
7. Import validation, geometry repair policy and quarantine of invalid source geometries.
8. Data migration and schema-version strategy for offline packages.

## 14. Consequences

### Positive
- Keeps spatial data alongside canonical relational TruckFood entities.
- Supports points, entrances, lines, polygons and spatial relationships without a separate service at the outset.
- Provides a path to nearby and corridor-based discovery.
- Preserves provider abstraction and licensing controls.
- Makes spatial accuracy, provenance, privacy and coverage explicit concerns.

### Trade-offs
- PostGIS adds operational and schema expertise requirements.
- Spatial indexes and complex queries require measurement and careful design.
- Poor-quality or overly detailed geometry increases cost without necessarily improving driver outcomes.
- Provider licensing may prevent storage or offline reuse of some geometries.
- A site's representative point is insufficient for entrance-level truck access decisions.

## 15. Open questions

- Confirm the exact managed PostgreSQL/Supabase plan and supported PostGIS version.
- Choose geometry, geography or both per entity after query prototypes.
- Define the physical Location/entrance/site-boundary relationship.
- Define road-network representation and whether TruckFood stores road geometry or only permitted references.
- Select route-corridor query strategy and acceptable approximation/false-positive behaviour.
- Define precision classes and geometry quality validation rules.
- Define retention/licensing per provider and dataset.
- Establish measurable query performance and cost budgets.

## 16. Implementation gate

Do not create the production spatial migration until hosting capability, licensing rights, canonical geometry mapping, privacy/RLS design and representative query prototypes have been validated. This ADR records the preferred direction; it does not claim PostGIS is enabled or spatial functionality implemented.
