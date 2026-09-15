# TruckFood

TruckFood is a professional truck-driver journey intelligence platform.

Its mission is simple:

**Chegar. Parar. Comer. Descansar. Continuar.**

The platform is designed to help truck drivers avoid unsuitable access and road situations, find realistic places to stop and park, find food and services, and make better journey decisions.

## Core Problem

A truck driver does not only need to know where a restaurant is. The driver needs to know whether the journey and the stop make sense for the vehicle.

TruckFood therefore treats the following as first-class concepts:

- vehicle context;
- road and access restrictions;
- truck parking;
- restaurants and food;
- rest and useful services;
- community observations;
- data provenance, freshness and confidence.

## Product Direction

TruckFood will initially build a **Truck Intelligence layer** around existing map and routing capabilities rather than attempting to replace mature navigation systems immediately.

The architecture will keep external providers behind adapters so that maps, routing, geocoding and data sources can evolve independently.

## Product Interfaces

The planned platform includes:

- Mobile app
- Web platform
- Administration platform
- Backend/API

## Initial Technology Direction

- Mobile: React Native with Expo
- Web: Next.js
- Backend/data: Supabase / PostgreSQL / Auth / Storage
- Maps/routing: provider abstraction
- Source control: GitHub

Technology choices remain provisional until discovery validates cost, licensing, coverage, performance and operational requirements.

## Safety & Trust Principle

The absence of a known restriction is **not proof that no restriction exists**.

TruckFood must not claim universally safe or legally compliant truck routing until the underlying data quality, coverage, licensing and validation justify that capability.

## Documentation

The repository is documentation-first. The project state, product decisions, requirements, data strategy and architecture decisions are maintained in `docs/`.

Start with:

- `PROJECT_CONSTITUTION.md`
- `PRODUCT_MANIFESTO.md`
- `docs/PROJECT_STATE.md`
- `docs/VISION.md`
- `docs/MVP.md`
- `docs/DATA_STRATEGY.md`
- `docs/PROVIDER_RESEARCH.md`
- `docs/DISCOVERY_FINDINGS.md`
- `docs/adr/`

## Status

**Phase -1 — Discovery & Product Foundation**

The product foundation and initial provider/data research are in progress. Application implementation begins only after the core architecture and data boundaries are validated.
