# ADR-0001 — TruckFood Product Direction

**Status:** Accepted  
**Date:** 2026-09-15  

## Context

TruckFood was initially described as an application for professional drivers to discover and share restaurants along their routes.

During product definition, the core problem was clarified: a truck driver needs more than food discovery. The driver needs practical support to avoid unsuitable roads and access points and to find appropriate places to stop, park, eat and rest.

## Decision

TruckFood will be designed as a **professional truck-driver journey intelligence platform**, with restaurant discovery as one major domain rather than the entire product.

The product sequence is:

**Chegar → Parar → Comer → Descansar → Continuar**

The initial technical strategy is to build a Truck Intelligence layer around existing mapping/routing capabilities instead of immediately replacing mature navigation engines.

## Consequences

### Positive

- The product solves a more meaningful driver problem.
- Parking, food, rest and services can share one location/domain model.
- Vehicle characteristics become a first-class architectural concern.
- The product can grow beyond restaurants without redesigning its foundation.

### Risks

- Road restriction data is difficult, dynamic and potentially safety-critical.
- Map and routing licensing may constrain implementation.
- The broader scope increases architectural complexity.
- The system must avoid presenting incomplete data as guaranteed safe routing.

## Implementation Guidance

The architecture must preserve clear separation between:

- external map/routing providers;
- TruckFood vehicle/rule logic;
- restriction data;
- location data;
- community data;
- trust/provenance logic.

Any future decision to provide autonomous truck routing must be supported by a separate ADR after data quality, coverage, licensing and safety considerations are validated.
