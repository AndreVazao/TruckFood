# TruckFood — Project Constitution

**Version:** 1.0.0  
**Status:** Active  
**Last Update:** 2026-09-15  

## 1. Purpose

TruckFood exists to help professional truck drivers complete journeys with better information about where they can **arrive, stop, eat, rest and continue**.

The product is not a restaurant directory. It is a heavy-vehicle travel intelligence platform whose first practical mission is to reduce avoidable routing and stopping problems for professional drivers.

## 2. Core Mission

**Chegar. Parar. Comer. Descansar. Continuar.**

The system must progressively help a driver:

1. avoid roads, streets, bridges and access points that are unsuitable for the driver's vehicle;
2. find appropriate places to stop and park;
3. find places to eat that are useful to professional drivers;
4. plan stops around rest and practical trip needs;
5. continue the journey with better information.

## 3. Non-Negotiable Principles

- Driver safety and practical usefulness come before growth features.
- Reality comes before assumptions.
- Stability comes before feature volume.
- Data provenance matters.
- Restrictions and vehicle suitability must never be presented with unjustified certainty.
- Manual control is preferred over destructive automation.
- Documentation is part of the product, not an afterthought.
- Important architectural decisions must be recorded.
- The repository is the project source of truth.
- Internationalisation must be considered from the beginning.
- Vendor lock-in must be avoided where a reasonable abstraction is possible.

## 4. Product Boundary

TruckFood should initially build a **Truck Intelligence layer** around existing mapping/routing capabilities rather than attempting to replace mature navigation systems immediately.

Conceptually:

`Driver → Origin/Destination → Map Engine → TruckFood Rules → Restrictions & Vehicle Profile → Truck Stops & Services → Recommendations`

TruckFood must not promise a universally safe truck route until the quality, coverage, freshness and licensing of the underlying data justify such a claim.

## 5. Central Concept

A restaurant is not the central object of the platform. A **Location / Point of Interest** is.

A location may represent, among other things:

- Restaurant
- Truck Stop
- Parking
- Fuel
- Workshop
- Hotel
- Hospital
- Supermarket
- Border / Customs
- Ferry
- Charging Station
- Other professional-driver services

Restaurants remain a major product category, but the platform is designed around the driver's journey.

## 6. Trust and Data

Relevant information must be associated, where applicable, with:

- source;
- provenance;
- confidence;
- recency;
- validation status;
- community confirmations or reports.

The product should distinguish information originating from official sources, map providers, community contributions and system inference.

## 7. Data Lifecycle

Important location/content data should follow a controlled lifecycle:

`Created → Validated → Published → Confirmed → Updated → Archived`

## 8. Vehicle Context

The platform should progressively support a vehicle profile containing characteristics that can affect route and stop suitability, such as dimensions, weight, configuration and relevant restrictions.

The exact initial vehicle model is an architectural decision to be defined before implementation.

## 9. Architecture Governance

Architecture is developed in layers and domains. Features must not bypass the agreed domain boundaries merely for speed.

Important decisions must be documented as ADRs. New ideas that can materially change architecture should enter through RFCs before becoming implementation requirements.

## 10. Definition of Done

A meaningful phase is not considered complete merely because code exists. It must have, as applicable:

- documentation;
- implementation;
- tests;
- validation;
- security considerations;
- operational considerations;
- known limitations;
- updated project state;
- recorded architectural decisions.

## 11. Change Rule

This constitution may evolve, but changes must be explicit, documented and reflected in the project state. No important principle should disappear silently.
