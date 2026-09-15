# TruckFood — Data Strategy

**Version:** 1.0.0  
**Status:** Discovery baseline

## Objective

Build a data foundation in which useful information can be combined without losing its origin, freshness or uncertainty.

## Data Families

### 1. Geographic Base Data

Map geometry, addresses, coordinates and basic geographic entities.

### 2. Road / Restriction Data

Vehicle restrictions, closures, access rules and other journey-relevant facts.

### 3. Location / Business Data

Restaurants, parking, fuel, workshops and other useful places.

### 4. Community Data

Reviews, observations, confirmations, corrections and photos.

### 5. Vehicle Data

Vehicle characteristics needed to evaluate suitability.

## Source Categories

Every imported or externally derived dataset should be classified before production use:

- source owner;
- licence;
- geographic coverage;
- update frequency;
- technical access method;
- attribution requirements;
- commercial-use restrictions;
- data quality;
- known limitations.

## Source Registry

Before a source becomes an architectural dependency, it should be recorded in a source registry with its legal and technical constraints.

## Data Quality

For critical facts, the system should preserve enough information to answer:

- Where did this come from?
- When was it obtained?
- When was it last validated?
- How precise is it?
- Is there corroboration?
- Does another source disagree?

## Licensing Rule

No external dataset, map service, route service, image source or business directory should be copied into the product merely because it is technically accessible.

Technical accessibility does not imply permission for the intended commercial use.

## Discovery Work

Before database implementation, the project must identify realistic initial sources for:

- base maps;
- routing;
- road restrictions;
- truck parking;
- restaurants/businesses;
- community enrichment.

Only after that analysis should provider-specific implementation be frozen.
