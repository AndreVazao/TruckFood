# ADR-0004 — Location / POI Domain Model

**Status:** Accepted  
**Date:** 2026-09-15  
**Decision owners:** TruckFood project  

## 1. Context

TruckFood started as a restaurant-discovery concept but has evolved into a professional truck-driver journey intelligence platform.

The product sequence is:

**Chegar → Parar → Comer → Descansar → Continuar**

A single useful place may provide several of these functions. A service station, for example, may offer truck parking, fuel, restaurant, toilets, showers and other services. OpenStreetMap also models restaurants, fuel stations and additional facilities as distinct features, which supports keeping the geographic place separate from individual services.

Therefore the domain must not make `Restaurant` the root geographic entity.

## 2. Decision

TruckFood will use **Location** as the primary geographic/domain entity.

A `Location` represents a real-world place or operational site that can contain one or more services, facilities or access characteristics relevant to professional drivers.

Services are represented as capabilities attached to the Location rather than as mutually exclusive Location types.

Examples:

- restaurant;
- truck parking;
- fuel station;
- service area;
- rest area;
- showers;
- toilets;
- accommodation;
- workshop;
- tyre service;
- supermarket/shop;
- EV charging;
- medical/emergency service;
- border/customs service;
- other driver-relevant services.

A Location may have several capabilities simultaneously.

## 3. Core Model

Conceptually:

```text
Location
├── Identity
├── Geographic position
├── Address / locality
├── Access profile
├── Vehicle suitability
├── Capabilities
│   ├── Parking
│   ├── Food
│   ├── Fuel
│   ├── Rest
│   ├── Hygiene
│   ├── Accommodation
│   ├── Workshop
│   ├── Shopping
│   └── Other services
├── Opening / availability rules
├── Restrictions / access conditions
├── Source / provenance
├── Confidence / freshness
├── Community observations
└── Media / reviews
```

The model deliberately separates:

1. **Where the place is** — Location.
2. **What exists there** — capabilities/services.
3. **Whether the driver's vehicle can reach/use it** — access and suitability.
4. **How trustworthy the information is** — provenance, freshness and confidence.

## 4. Location Identity

A Location should have a TruckFood-owned stable identifier independent of external providers.

External identifiers must be stored as source references rather than becoming the primary key.

Minimum conceptual identity:

- `location_id`
- canonical name
- geographic coordinates
- country
- administrative locality/region where available
- source references
- lifecycle state

The canonical identity must remain stable when provider-specific identifiers change.

## 5. Capabilities

Capabilities describe what a driver can actually find/use at the location.

Capabilities must be extensible rather than encoded as a large enum that requires schema redesign for every new service.

Examples of initial capability families:

### Parking

- truck parking available
- approximate capacity
- free/paid
- reserved/controlled access
- overnight allowed
- security information
- lighting
- surveillance
- suitable vehicle characteristics where known

### Food

- restaurant
- cafe
- fast food
- takeaway
- cuisine
- opening hours
- driver suitability
- truck access/parking relationship

### Fuel

- diesel
- AdBlue
- alternative fuels where relevant
- truck-compatible access
- opening hours
- payment/fleet-card information where legally and contractually usable

### Rest and hygiene

- toilets
- showers
- rest area
- sleeping/rest possibility
- drinking water
- laundry where available

### Services

- workshop
- tyres
- washing
- supermarket/shop
- accommodation
- EV charging
- medical/emergency
- customs/border services

## 6. Access Is Not the Same as Capability

A location can have a capability without being suitable for every truck.

For example:

```text
Location: Restaurant X
Capability: Restaurant
Capability: Parking

Access:
  max_height = 3.80 m
  max_length = 12.00 m
  HGV = permitted

Vehicle:
  height = 4.00 m

Result:
  Restaurant exists.
  TruckFood must not present the location as suitable for this vehicle.
```

This distinction is mandatory.

The Location model therefore supports an **access/suitability layer** that is evaluated against the user's Vehicle Profile.

## 7. Parent Site vs Individual Services

TruckFood will support a parent Location with child service records where useful.

Example:

```text
Location: Área de Serviço X
├── Truck Parking
├── Fuel
├── Restaurant
├── Toilets
└── Showers
```

This prevents the product from treating each service as an unrelated place while still allowing precise service-level information.

A service may have its own opening hours, entrance, coordinates or restrictions when necessary.

## 8. Opening Hours and Temporal Conditions

Opening/availability must be modelled separately from static existence.

A service may be:

- permanently available;
- available only during certain hours;
- closed on specific days;
- temporarily closed;
- seasonally available;
- available only under conditions.

TruckFood must preserve source-provided temporal information rather than flattening it into a single `open=true/false` field.

## 9. Geographic Access

A Location record must not imply that the nearest road or entrance is automatically suitable for a truck.

Where available, TruckFood should distinguish:

- main location coordinates;
- vehicle entrance/access point;
- service-specific entrance;
- road/access segment;
- known access restrictions.

This is especially important for large sites where the car entrance and truck entrance differ.

## 10. Suitability Evaluation

TruckFood should eventually calculate a contextual suitability result from:

```text
Vehicle Profile
+
Location capability
+
Access restrictions
+
Road restrictions
+
Temporal conditions
+
Source confidence/freshness
=
Contextual suitability
```

Possible result states should be more expressive than `yes/no`:

- suitable;
- suitable_with_conditions;
- unsuitable_known;
- unknown;
- temporarily_unavailable;
- insufficient_data.

The product must never turn `unknown` into `suitable` merely because no restriction was found.

## 11. Provenance

Every important Location/service fact must retain its provenance.

The model must support:

- source type;
- source identifier;
- observed/created time;
- last verification time;
- freshness information;
- confidence;
- validation state;
- conflict information when sources disagree.

Source classes include:

- official;
- commercial/provider;
- community;
- operator/business;
- TruckFood-generated/inferred.

## 12. Community Data

Community observations are first-class supporting evidence, not automatically authoritative truth.

Examples:

- parking full;
- access blocked;
- restaurant closed;
- shower unavailable;
- entrance too tight;
- temporary construction;
- new truck entrance;
- service no longer offered.

Community observations should carry timestamp, author/context where appropriate, moderation state and confidence.

## 13. External Provider Mapping

A Location can be linked to multiple provider records:

```text
TruckFood Location
├── OSM reference
├── HERE reference
├── TomTom reference
├── business/POI provider reference
└── TruckFood internal reference
```

Provider identifiers are references, not the TruckFood identity.

This preserves the provider-abstraction decision from ADR-0002.

## 14. Why Not a Single Giant POI Type Enum?

The model will not define locations as only one of:

`restaurant | fuel | parking | hotel | workshop | ...`

because real-world truck locations frequently combine services.

Instead:

```text
Location
  + Capability[]
```

A location may therefore be both a fuel station and restaurant, or a service area with parking, food, toilets and showers.

## 15. MVP Scope

The first implementation should not model every possible facility in the world.

Initial capabilities:

1. truck parking;
2. restaurant/food;
3. fuel;
4. toilets;
5. showers;
6. rest area;
7. workshop/service;
8. accommodation;
9. shop/supermarket;
10. EV charging.

The capability framework remains extensible for later services.

## 16. Decision Consequences

### Positive

- Matches the real-world multi-service nature of truck stops and service areas.
- Supports the Chegar → Parar → Comer → Descansar → Continuar journey.
- Prevents restaurant-centric architecture.
- Allows provider data from different systems to converge on one TruckFood location.
- Supports vehicle-specific suitability.
- Supports temporal restrictions and freshness.
- Makes future international expansion easier.

### Negative / trade-offs

- The domain model is more complex than a simple restaurant table.
- Deduplication/entity matching becomes an important technical problem.
- Access and service suitability require more data than ordinary POI search.
- Provenance and freshness require additional storage and processing.

## 17. Explicit Non-Decisions

This ADR does not yet freeze:

- exact SQL tables;
- exact JSON/API schema;
- exact capability enumeration;
- exact trust-score algorithm;
- exact geospatial database implementation;
- exact provider;
- automatic route safety claims.

Those decisions require subsequent architecture/data ADRs.

## 18. Validation Sources

OpenStreetMap's current tagging guidance demonstrates that restaurants, fuel stations and additional facilities can be represented as distinct features, including opening hours, fuel capabilities, HGV suitability and maximum-height information. This supports the decision to keep the TruckFood Location entity separate from its capabilities and access properties.

## 19. Result

**Accepted.**

TruckFood's geographic core is now:

**Location + Capabilities + Access + Vehicle Suitability + Provenance + Freshness + Community Evidence**.

This becomes the basis for the next architecture step: defining the initial persistence/domain model without prematurely coupling it to a provider.