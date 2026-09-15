# ADR-0003 — Minimum Viable Truck Vehicle Model

**Status:** Accepted — Discovery/Foundation
**Date:** 2026-09-15
**Decision:** Define a compact but operational vehicle profile as a first-class TruckFood domain object.

## 1. Context

TruckFood exists to help professional drivers make better decisions about whether they can arrive, stop, eat, rest and continue. Vehicle suitability is therefore part of the core domain, not an optional preference.

Portugal's road-vehicle rules explicitly distinguish dimensions, gross weight and gross axle weight. Current Portuguese legislation includes maximum dimensions such as 2.55 m general width, 4.00 m height for motor vehicles and their trailers, 16.50 m for tractor-semitrailer combinations and different limits by vehicle/combination configuration. citeturn0search4turn0search2

ADR is also a distinct concern: IMT publishes ADR 2025 with requirements covering classification, transport conditions, crew/equipment/operation/documentation and vehicle construction/approval. citeturn0search8

The model must therefore be useful enough to represent real restrictions without becoming an unnecessarily complex fleet-management system.

## 2. Decision

TruckFood will use the following **minimum viable vehicle context** for journey intelligence.

### 2.1 Required core dimensions

- `height_m`
- `width_m`
- `length_m`
- `gross_weight_t`

These are the first physical attributes used for route/access suitability.

### 2.2 Axle context

- `axle_count`
- `weight_per_axle_t` — optional initially, required when an axle restriction is relevant

TruckFood must not infer axle loading from gross weight alone. An axle restriction and a gross-weight restriction are different facts.

### 2.3 Vehicle configuration

- `vehicle_type`
- `configuration`
- `has_trailer`
- `trailer_type` — optional

Initial controlled values should cover common professional configurations without attempting to model every regulatory subtype.

Suggested initial values:

`rigid_truck`, `tractor_unit`, `truck_trailer`, `tractor_semitrailer`, `road_train`, `other_heavy_vehicle`

### 2.4 Hazardous materials / ADR

- `adr_enabled`
- `adr_classes` — optional list
- `adr_tunnel_category` — optional

ADR fields are conditional. A normal driver should not have to configure ADR information when it is irrelevant to the journey.

### 2.5 Operational attributes

- `refrigerated` — boolean
- `vehicle_name` — optional user label
- `profile_version`
- `updated_at`

`refrigerated` is not a road restriction by itself, but can materially affect suitable parking, services and stop recommendations.

## 3. What is deliberately NOT in the MVP model

The first model will not attempt to represent:

- complete vehicle registration data;
- engine details;
- manufacturer/model;
- fuel consumption;
- tyre data;
- maintenance state;
- driver hours/tachograph state;
- complete load manifest;
- every European regulatory vehicle class;
- fleet-management telematics;
- real-time axle weights unless a future integration provides them.

These may be added later only when a product requirement demonstrates value.

## 4. Important distinction: legal limits vs physical limits

TruckFood must represent restriction semantics separately.

Examples:

- `maxheight` — a legal/posted restriction;
- `maxheight:physical` — a physical clearance constraint;
- `maxweight` — a weight restriction;
- axle-specific restriction — a separate constraint.

A route engine or TruckFood rule must not collapse these into one generic "truck restriction" field.

## 5. Profile modes

The user experience should eventually support three modes:

### Simple

The driver enters the essential dimensions and weight.

### Professional

The driver can configure dimensions, axle information, configuration and operational attributes.

### ADR

The driver enables ADR and provides the applicable ADR information when required.

The backend domain model remains the same; the UI determines how much is exposed.

## 6. Safety rules

1. Missing vehicle data must not be silently replaced by optimistic assumptions.
2. A missing restriction must never be interpreted as proof that a road is suitable.
3. A provider's "truck route" result must remain distinguishable from TruckFood's own verified restriction information.
4. Where a required vehicle attribute is unavailable, TruckFood should report reduced confidence rather than invent a value.
5. Regulatory compliance must ultimately be verified against applicable official/legal sources and provider terms.

## 7. Initial domain object

Conceptually:

```text
VehicleProfile
├── identity
│   └── profile_id
├── dimensions
│   ├── height_m
│   ├── width_m
│   └── length_m
├── weight
│   ├── gross_weight_t
│   └── weight_per_axle_t?
├── configuration
│   ├── vehicle_type
│   ├── configuration
│   ├── axle_count
│   ├── has_trailer
│   └── trailer_type?
├── hazardous_materials
│   ├── adr_enabled
│   ├── adr_classes[]?
│   └── adr_tunnel_category?
├── operations
│   └── refrigerated
└── metadata
    ├── profile_version
    └── updated_at
```

This is a domain specification, not yet the final SQL schema.

## 8. Consequences

### Positive

- Vehicle context becomes usable across routing, restrictions, parking and locations.
- The model remains small enough for an MVP.
- Provider adapters can translate TruckFood vehicle context into provider-specific parameters.
- Future expansion can add regulatory or operational attributes without changing the product concept.

### Negative

- Some provider capabilities will require additional fields later.
- A driver may receive lower-confidence results when vehicle information is incomplete.
- International expansion may expose regulatory differences that require extensions.

## 9. Validation gate before implementation

Before the database schema is frozen, validate the model against:

1. Portugal legal restrictions.
2. OSM restriction tags and semantics.
3. HERE truck routing vehicle parameters.
4. TomTom truck vehicle parameters.
5. At least three real professional-driver journey scenarios.
6. ADR journey scenarios.
7. Parking/access scenarios.

## 10. Final decision

**Accepted.**

TruckFood will treat the vehicle profile as a first-class domain object with dimensions, gross weight, axle context, configuration and conditional ADR/operational attributes.

The model is intentionally minimal. More fields require a documented product or safety reason.
