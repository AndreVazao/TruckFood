# TruckFood — Vehicle Profile

**Version:** 1.0.0  
**Status:** Discovery baseline — schema not final

## Purpose

Vehicle context is required because a route or location that works for a car may be unsuitable for a heavy vehicle.

The vehicle profile must therefore become a first-class product concept.

## Initial Candidate Attributes

### Dimensions

- overall length;
- overall width;
- overall height.

### Mass

- gross permitted mass;
- current/estimated mass where useful;
- axle configuration or relevant axle constraints where available.

### Vehicle Type

Examples to support conceptually:

- rigid truck;
- tractor + semi-trailer;
- articulated combination;
- van/light commercial vehicle;
- other heavy vehicle classes as the product evolves.

### Special Conditions

Potential flags include:

- refrigerated transport;
- ADR / dangerous goods relevance;
- trailer;
- multiple trailers where relevant;
- special access requirements.

## Important Rule

The profile must not imply that TruckFood can determine every legal or physical constraint from these fields alone.

Vehicle suitability is the result of:

`Vehicle Profile + Road/Location Data + Restrictions + Time + Source Quality + Rules`

## MVP Direction

The first MVP should use a deliberately small, understandable vehicle model containing only attributes that can materially affect the first product capabilities.

The final schema must be decided through an ADR before database implementation.
