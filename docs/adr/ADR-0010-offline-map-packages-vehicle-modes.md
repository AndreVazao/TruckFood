# ADR-0010 — Offline Map Packages & Vehicle Modes

**Status:** Proposed — Discovery / Foundation  
**Date:** 2026-10-14  
**Decision:** TruckFood should plan for user-selected offline map packages and an explicit vehicle/travel mode. Offline packages must distinguish base map/navigation data from truck-relevant locations and restrictions, show data freshness and coverage, and never imply real-time traffic or guaranteed truck-safe routing.

## 1. Context

Professional drivers may have no mobile data, weak network coverage, roaming constraints or a limited data allowance. They may still need basic map access, a previously downloaded route, known truck parking, and known restrictions.

TruckFood also serves different travel contexts: a normal passenger car, a standard truck/HGV and a special or oversized load. The vehicle context changes which access restrictions and route constraints may be relevant.

These capabilities are important product requirements, but offline routing and truck restriction completeness depend on provider licensing, local storage rights, data quality and implementation choices that have not yet been validated.

## 2. Decision

TruckFood will design for two related capabilities:

1. **Offline area packages** that users explicitly download, inspect, update and delete.
2. **An explicit travel mode and vehicle profile** selected or confirmed when the user starts using map/journey features.

These capabilities will be introduced incrementally. This ADR records the product direction; it does not claim offline functionality already exists.

## 3. Vehicle / Travel Mode Selection

The app should offer a simple first-use choice, with the ability to change it later:

- **Car** — passenger car / ordinary daily vehicle.
- **Truck** — heavy goods vehicle, using a saved vehicle profile.
- **Special / oversized load** — a truck or combination whose dimensions, mass, configuration or permit conditions exceed ordinary assumptions.

The choice is a starting point, not a complete vehicle specification. A truck profile should collect the attributes required by the selected features, such as height, width, length, gross weight, axle information where relevant, trailer configuration and ADR status when applicable.

For special loads, the app must ask for the relevant dimensions and weights and, where applicable, permit/escort or route constraints. It must not assume that choosing “special load” alone gives enough information to calculate a lawful route.

The user must be able to:
- save multiple vehicle profiles;
- choose the active profile for a journey;
- edit or temporarily override a profile with clear confirmation;
- see which profile was used for an assessment;
- know when missing attributes prevent a meaningful assessment.

## 4. Offline Package Contents

Offline downloads should be explicit, bounded packages for a selected region or corridor. A package may include, subject to provider and licensing rights:

- base map data needed for offline display;
- locally stored geographic features and roads;
- TruckFood-owned locations and selected services;
- known truck parking and service-area information;
- known restrictions and access facts that are eligible for offline storage;
- essential metadata for source, coverage, last update and review status;
- optional route data for a user-selected journey, if supported by the chosen mapping engine.

The package should be divided logically so that the user can understand what is included. Downloading a base map must not imply that the package contains complete truck restrictions or every parking facility.

## 5. Offline Capability Levels

The UI must distinguish the following capability levels:

1. **Offline map viewing** — display downloaded map content without network access.
2. **Offline saved places** — search or browse downloaded TruckFood locations and services within the package.
3. **Offline known restrictions** — display restrictions included in the package, with their source and freshness.
4. **Offline route calculation** — calculate a route locally only if the selected routing engine and its license/data support this.
5. **Offline truck-aware route evaluation** — evaluate vehicle constraints only to the extent that suitable local road, restriction and rule data exist and have been validated.

These are separate capabilities. Availability of one does not prove availability of the others.

## 6. Download Management

Users should be able to:
- choose a region, area or route corridor;
- see estimated download size before confirming;
- download on Wi-Fi by preference;
- pause/resume when technically supported;
- see progress and failure reasons;
- inspect package date, coverage and update status;
- update or delete a package;
- see device storage used by each package.

The system should prevent accidental unbounded downloads. Package size, retention limits and update policy must be configurable and tested on lower-capacity devices.

## 7. Freshness and Coverage

Every package must retain metadata such as:
- package identifier and version;
- geographic coverage and precision;
- included data families;
- creation and last-update timestamps;
- source/provider attribution where required;
- known limitations and exclusions;
- whether data is expired or needs review.

When offline, the app must say that live information cannot be checked. It must not show stale information as live.

A package may contain restrictions that have since changed. Therefore:
- temporary restrictions need effective-time and expiry/review handling;
- expired or stale facts must be visibly flagged;
- data that cannot be validated offline must remain uncertain;
- absence of a restriction from the package is not evidence that the road is unrestricted;
- downloaded data must not be presented as a guarantee of legal or physical access.

## 8. Offline Routing Safety Boundary

TruckFood must not promise a universally safe offline route until road coverage, vehicle restrictions, licensing, routing behaviour and validation have been proven for the target area.

If offline routing is supported, the app must communicate:
- the active vehicle profile;
- the geographic scope and update date of the data;
- which constraint families are included;
- important data gaps;
- that live traffic, incidents, temporary closures and newly introduced restrictions cannot be assumed available without a connection.

If the available data cannot support an assessment, the result must be unknown or insufficient data, not safe.

## 9. Provider and Licensing Boundary

Offline storage is not automatically permitted merely because data can be downloaded through an API.

Before choosing a map/routing provider, TruckFood must verify:
- whether offline map tiles or vector data may be stored;
- whether offline routing is permitted;
- whether downloaded restrictions/POIs may be retained and for how long;
- attribution and redistribution requirements;
- territory and usage restrictions;
- update, cache and deletion obligations;
- whether TruckFood-owned and community data can be packaged independently.

Provider-specific implementations must sit behind adapters and must not leak vendor schemas into the canonical domain.

## 10. Architecture Implications

The architecture should support:
- a package manifest and version;
- region/corridor coverage definitions;
- independently updateable data families where practical;
- local storage and schema-version migration;
- package integrity checks and interrupted-download recovery;
- separation between canonical TruckFood data and provider-licensed content;
- offline read-only access to eligible downloaded data;
- a synchronization policy for user-created observations made offline, including conflict handling and retry safety.

Offline submissions should be queued only when safe and practical, then synchronized with idempotency and clear status. The app must not silently claim a submission was published while it remains local.

Exact file format, local database, map renderer, routing engine and synchronization mechanism remain open.

## 11. MVP Recommendation

The first release should not attempt to deliver complete offline truck navigation immediately.

Recommended progression:

**Stage A — Offline saved information**
- save selected locations and essential truck-stop details;
- display the last-known data time;
- make the offline state obvious.

**Stage B — Downloadable local area**
- allow a bounded area package if provider licensing and storage are validated;
- include map display and eligible TruckFood-owned locations;
- show package size, coverage and freshness.

**Stage C — Offline map engine**
- add offline map rendering and local search after provider/technology evaluation.

**Stage D — Offline routing**
- add only if routing-engine licensing, vehicle constraints, local data coverage, storage and validation justify it.

Truck-specific offline route restrictions must not be advertised as complete until they have been independently validated.

## 12. Non-Goals

This ADR does not decide:
- map or routing vendor;
- map tile/vector format;
- offline storage technology;
- exact maximum download size;
- exact vehicle form fields or regulatory rules for special loads;
- route algorithm;
- offline synchronization implementation;
- commercial provider contract;
- launch date or promise of full offline navigation.

## 13. Consequences

### Positive
- Helps drivers with weak/no data coverage and limited data plans.
- Makes vehicle-specific constraints an explicit part of product entry.
- Supports a staged rollout rather than an unsafe all-at-once offline promise.
- Makes package freshness, scope and limitations visible.
- Preserves provider licensing as a design constraint.

### Trade-offs
- Offline maps and routing can require significant storage and engineering effort.
- Data freshness is inherently limited without connectivity.
- Commercial map providers may restrict offline storage or routing.
- Oversized/special-load routing requires more than a single mode selector.
- Local data synchronization and conflict handling add complexity.

## 14. Follow-up Decisions

1. Evaluate offline-capable mapping and routing options, including licensing and total cost.
2. Define the first vehicle-mode and profile UX.
3. Decide local storage, package manifest and update mechanics.
4. Define privacy/security for locally stored vehicle and journey data.
5. Define the API/provider contracts needed to build and update packages.
6. Define which data families may legally and technically be stored offline.
7. Validate requirements with drivers who regularly experience poor connectivity.
