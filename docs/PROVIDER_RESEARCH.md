# TruckFood — Provider & Data Research

**Version:** 1.0.0  
**Status:** Discovery research — not an implementation commitment  
**Date:** 2026-09-15

## Executive Finding

The research confirms that the technical foundation for truck-aware routing already exists in commercial routing platforms, while OpenStreetMap provides valuable open geographic and restriction data. TruckFood should therefore **abstract routing/data providers instead of coupling the product domain directly to one vendor**.

## OpenStreetMap

OpenStreetMap can represent truck-relevant restrictions including maximum height, width, length, weight, axle load, HGV access, hazardous-material access and conditional restrictions.

This is particularly valuable for the TruckFood data model because it demonstrates that legal restrictions and physical limitations are different concepts and may need separate representation.

OSM is licensed under ODbL. Attribution is required, and share-alike obligations can apply to distributed OSM data and derivative databases. The exact legal treatment of a combined TruckFood database must be reviewed before production architecture is frozen.

**Potential role:** geographic foundation, enrichment/reference data, restriction signals, community geographic context.

**Not yet approved as:** sole source of truth for safety-critical truck routing.

## HERE Routing

HERE Routing API v8 explicitly supports truck routing and vehicle parameters such as current weight, gross weight, height and weight per axle. It can consider legal, physical, hazardous-material and time-dependent restrictions.

HERE also documents country/region coverage differences for truck restriction data. This is critical: a truck route may exist in an area where truck-specific restriction coverage is incomplete.

**Potential role:** commercial truck routing engine and restriction-aware route calculation.

**Important:** coverage, pricing, quotas, licensing and commercial terms must be validated before selection.

## TomTom

TomTom's routing SDK exposes truck vehicle types and vehicle dimensions/restrictions, indicating that it can also participate in a provider abstraction for truck-aware routing.

**Potential role:** alternative commercial routing/provider candidate.

**Important:** current API/product availability, coverage, pricing, licensing and exact backend capabilities must be validated before selection.

## Provider Strategy

TruckFood should separate these concerns:

1. **Map display provider** — visual map and basic geographic rendering.
2. **Geocoding provider** — address/place conversion.
3. **Routing provider** — route calculation.
4. **Restriction/data provider** — road and vehicle constraints.
5. **POI/business provider** — businesses and places.
6. **TruckFood-owned data** — community observations, trust, corrections and proprietary enrichment.

No provider should become the domain model.

## Key Technical Finding

A route engine may know that a truck restriction exists, but TruckFood still needs its own model for:

- provenance;
- freshness;
- confidence;
- conflicts between sources;
- community reports;
- TruckFood-specific recommendations;
- auditability.

## Initial Direction

For the MVP, the safest architecture is:

`TruckFood Domain → Provider Adapter → External Provider`

rather than:

`TruckFood Domain → HERE/TomTom/OSM-specific objects everywhere`

## Open Questions

- Which provider gives the best Portugal + Europe truck coverage for the required budget?
- Which provider permits the intended commercial use and storage of returned data?
- Can routing results be cached, stored or analysed under the provider terms?
- Which parking/business data can be legally imported?
- What official Portuguese and European restriction sources can complement commercial routing?
- How should conflicting restrictions be represented?
- What minimum coverage is required before TruckFood displays a truck-risk warning?
