# TruckFood — Discovery Findings

**Version:** 1.0.0  
**Status:** Discovery research baseline  
**Date:** 2026-09-15

## 1. Main Finding

The core TruckFood problem is technically viable, but the difficult part is not drawing a map. The difficult part is combining vehicle context, routing, restrictions, locations and community information without creating false confidence.

## 2. Truck Routing Exists as a Commodity Capability

Commercial providers already support truck-specific routing and vehicle parameters. This means TruckFood does not need to build a routing engine first.

The opportunity is to build the **professional-driver intelligence layer** around routing.

## 3. Restriction Data Is Richer Than a Single "Truck Allowed" Flag

Relevant constraints can include:

- height;
- physical height;
- width;
- physical width;
- length;
- physical length;
- weight;
- permitted weight rating;
- axle load;
- HGV access;
- hazardous-material access;
- conditional/time-dependent restrictions;
- closures and temporary restrictions.

Therefore the future TruckFood model must not reduce road suitability to a single boolean field.

## 4. Legal vs Physical Restrictions Must Be Separated

A road may have a legal maximum height while the actual physical clearance is represented separately. Similar distinctions exist for width and length.

This distinction is directly relevant to the product mission: the driver needs to avoid physically impossible situations, while the system also needs to respect legal restrictions.

## 5. Coverage Must Be Visible

A provider may support truck routing in a country while having incomplete truck-specific restriction coverage in some areas.

Therefore the TruckFood trust model must be able to express **coverage limitations**, not only confidence in an individual data point.

## 6. Open Data Is Valuable but Not Automatically Sufficient

OpenStreetMap provides useful restriction structures and global geographic coverage, but community-maintained data is not automatically complete or current enough to serve as the sole safety authority.

OSM licensing also requires deliberate architecture and attribution planning.

## 7. Provider Abstraction Is Mandatory

The project should keep provider-specific integrations behind adapters/interfaces so that routing, geocoding, maps and POI providers can change without rewriting the domain model.

## 8. MVP Consequence

The first release should focus on trustworthy discovery and context:

- places;
- parking;
- food;
- services;
- community observations;
- vehicle profile;
- provenance/freshness.

Full autonomous truck routing remains outside the first release until the data and legal foundations are proven.

## 9. Next Research Gate

The next discovery step is country-specific and commercial:

1. Portugal road/restriction sources.
2. Portugal truck parking sources.
3. Portugal restaurant/POI sources.
4. European expansion sources.
5. Provider pricing and quotas.
6. Data storage/caching rights.
7. Commercial redistribution rights.
8. Exact MVP operating cost.

## 10. Current Conclusion

**Proceed.**

The product concept is technically credible. The architecture should be built around provider independence, provenance, confidence, vehicle context and controlled data licensing.
