# ADR-0002 — External Provider Abstraction

**Status:** Accepted  
**Date:** 2026-09-15

## Context

TruckFood depends on capabilities that may be provided by external services: maps, geocoding, routing, restrictions and business/POI data.

Research confirms that commercial routing providers already support truck-specific parameters and restrictions, while OpenStreetMap provides open geographic and restriction data. However, coverage, licensing, pricing and storage rights differ between sources.

## Decision

TruckFood will use a **provider abstraction layer**.

The domain model must not depend directly on a specific vendor's request/response structures.

The initial conceptual boundaries are:

- Map Provider
- Geocoding Provider
- Routing Provider
- Restriction/Data Provider
- POI/Business Provider

Each integration will be implemented behind an adapter.

## Consequences

### Positive

- provider replacement remains possible;
- domain logic remains independent;
- multiple sources can be combined;
- provider failures can be handled more cleanly;
- commercial negotiations do not require a domain rewrite.

### Negative

- additional abstraction and integration work;
- lowest-common-denominator design must be avoided;
- provider-specific capabilities may need explicit optional extensions.

## Important Constraint

Abstraction does not mean pretending providers are equivalent. Provider-specific capabilities must remain discoverable through explicit capability metadata rather than leaking vendor objects throughout the system.

## Future Requirement

Before production provider selection, TruckFood must evaluate Portugal/Europe coverage, cost, quotas, licensing, caching/storage rights, data quality and failure behaviour.
