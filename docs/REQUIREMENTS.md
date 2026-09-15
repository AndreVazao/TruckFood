# TruckFood — Initial Product Requirements

**Version:** 1.0.0  
**Status:** Discovery draft

## 1. Primary User

The primary user is a professional truck driver travelling for work.

Secondary users may include:

- fleet operators;
- owner-drivers;
- restaurant/service operators;
- community contributors;
- administrators.

## 2. Core Functional Requirements

### FR-001 — Driver Identity

The system must support an authenticated driver identity suitable for storing preferences and contributions.

### FR-002 — Vehicle Context

The system must be able to associate a driver with a vehicle profile containing characteristics relevant to journey and location suitability.

### FR-003 — Location Discovery

The system must allow discovery of relevant locations on a map and through search.

### FR-004 — Location Categories

The system must support multiple professional-driver-relevant categories rather than restaurants only.

### FR-005 — Location Details

A location should expose useful practical information, its provenance where available, and its confidence/freshness state.

### FR-006 — Community Contributions

Drivers should be able to contribute reviews, observations, photos and useful factual updates subject to moderation and abuse controls.

### FR-007 — Parking

The platform must treat truck parking as a first-class product capability.

### FR-008 — Food

The platform must support restaurant discovery with truck-relevant information.

### FR-009 — Restrictions

The architecture must support road/access restrictions and vehicle suitability information.

### FR-010 — Trust

Critical information should have a trust/confidence mechanism that can evolve with source quality, freshness and confirmations.

### FR-011 — Administration

Administrators must be able to moderate content and manage important location information.

### FR-012 — Internationalisation

The architecture must support multiple countries, languages, currencies, units and timezones.

## 3. Non-Functional Requirements

### NFR-001 — Reliability

Critical user journeys must be designed for graceful failure when external services are unavailable.

### NFR-002 — Security

Authentication, authorisation, secrets and user-generated content must be treated as security-sensitive from the first implementation phase.

### NFR-003 — Observability

The backend must provide sufficient logging and diagnostics to identify failures without exposing sensitive data.

### NFR-004 — Data Provenance

The system must preserve the origin and relevant freshness information for critical external and community data.

### NFR-005 — Provider Abstraction

Maps and other external providers should be abstracted where doing so is technically and economically reasonable.

## 4. Explicit MVP Boundary

The MVP must not attempt to solve every truck-navigation problem.

The discovery phase must determine the smallest useful product that can reliably deliver:

- location discovery;
- truck-relevant parking information;
- food discovery;
- useful community information;
- basic driver/vehicle context;
- foundations for future restriction intelligence.

## 5. Open Requirements

The following remain to be researched and decided:

- exact vehicle schema;
- initial countries/regions;
- initial map provider;
- routing provider;
- road restriction sources;
- parking data sources;
- licensing terms;
- minimum trust/confidence model;
- legal/privacy requirements;
- retention policies;
- moderation policy;
- initial monetisation boundary.
