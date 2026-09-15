# TruckFood — Location / POI Model

**Version:** 1.0.0  
**Status:** Discovery baseline

## Core Decision

The central geographic entity is a **Location / Point of Interest**, not a restaurant.

A location can support one or more useful categories and can accumulate different kinds of professional-driver information.

## Initial Categories

- Restaurant
- Truck Stop
- Parking
- Fuel
- Workshop
- Hotel / Accommodation
- Hospital / Medical
- Supermarket
- Border / Customs
- Ferry
- Charging Station
- Other Driver Service

## Location Information

A location may eventually contain:

- geographic coordinates;
- name;
- categories;
- address;
- country/region;
- opening/access information;
- truck suitability;
- parking information;
- available services;
- pricing where relevant;
- photos;
- community observations;
- reviews;
- source/provenance;
- confidence;
- freshness;
- moderation status.

## Important Separation

A physical location and a user's opinion about that location are different concepts.

Likewise:

- official business information;
- map-provider information;
- community observation;
- inferred information

must not be treated as the same data type internally.

## Location Lifecycle

`Created → Validated → Published → Confirmed → Updated → Archived`

A location should not be permanently deleted merely because information becomes obsolete if historical integrity is required.

## Future Capability

A location may eventually support multiple services simultaneously. For example, one truck stop may contain parking, restaurant, showers, fuel and accommodation.

This is another reason not to make Restaurant the root entity.
