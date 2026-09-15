# ADR-0005 — Initial Domain & Persistence Model

**Status:** Accepted — Discovery / Foundation
**Date:** 2026-09-15
**Decision:** Define a canonical TruckFood domain model that separates owned domain entities, time-varying facts, observations and external provider data before database implementation.

## 1. Context

TruckFood has established that the product is a professional truck-driver journey intelligence platform rather than a restaurant-only application.

The core sequence is:

**Chegar → Parar → Comer → Descansar → Continuar**

The domain must therefore connect:

```text
Driver
 ├── Vehicle / Vehicle Profile
 └── Journey
       ├── Route
       │     └── Route Segments
       ├── Restrictions / Conditions
       └── Relevant Locations
              ├── Capabilities / Services
              ├── Access Rules
              ├── Observations
              ├── Reviews
              └── Provenance
```

The existing discovery documents already establish that Location is the central geographic entity, vehicle context is first-class, and critical information must preserve provenance, freshness and confidence.

This ADR defines the first domain/persistence boundary. It intentionally does **not** freeze exact SQL tables, indexes, PostGIS implementation, API payloads or provider schemas.

## 2. Decision

TruckFood will use a **canonical domain model owned by TruckFood**.

External providers may supply maps, routes, POIs, restrictions or geocoding, but their request/response objects will not become the application's core persistence model.

The model is divided into five logical families:

1. **Identity & User Context**
2. **Vehicle & Journey Context**
3. **Location & Service Context**
4. **Restrictions, Access & Suitability**
5. **Evidence, Provenance & Community Data**

Provider snapshots and mappings remain separate from canonical domain records.

## 3. Canonical Entities

### 3.1 User / Driver

Represents the authenticated product user.

Minimum conceptual fields:

- `id`
- account/authentication reference
- preferred language
- country/region where relevant
- created timestamp
- updated timestamp
- lifecycle/status

A User is not itself a vehicle. One driver may use more than one vehicle/profile.

### 3.2 Vehicle

Represents a driver's real vehicle or vehicle combination.

A Vehicle references a Vehicle Profile/version containing the characteristics relevant to suitability calculations.

Conceptual fields:

- `id`
- `owner_user_id`
- `profile_id`
- display name/identifier chosen by user
- active/default status
- created/updated timestamps
- archived timestamp when applicable

### 3.3 Vehicle Profile

Represents the measurable/configurable characteristics used by TruckFood rules.

Minimum accepted context follows ADR-0003:

- overall length
- overall width
- overall height
- gross permitted mass
- axle count/context where required
- axle weight where available and relevant
- vehicle/configuration type
- trailer/semi-trailer context
- ADR/dangerous-goods relevance when applicable
- refrigerated transport when relevant
- special access requirements where applicable
- profile version/date

Profiles are versionable. A change to a vehicle's dimensions or configuration must not silently rewrite the historical interpretation of a previous journey.

### 3.4 Journey

Represents a driver-planned or driver-recorded movement from an origin toward a destination.

A Journey may contain:

- selected vehicle/profile
- origin
- destination
- departure/planning time
- status
- route/provider references
- relevant restrictions
- relevant locations/stops

The initial persistence model must not assume that TruckFood owns the complete navigation route.

### 3.5 Route

Represents a route result or route plan associated with a Journey.

A Route may originate from an external routing provider or a future TruckFood routing engine.

The canonical Route stores only information that TruckFood needs for product behaviour, auditing and continuity. Provider-specific response payloads remain provider data.

### 3.6 Route Segment

Represents a meaningful portion of a route where conditions, restrictions or suitability can differ.

A segment may reference:

- geometry/reference to geometry
- road/network identifier when legally usable
- sequence/order
- relevant restrictions
- provider reference
- confidence/coverage metadata where applicable

Exact geometry storage is intentionally deferred until provider/licensing and infrastructure decisions are complete.

### 3.7 Restriction

Represents a known or reported road/access constraint relevant to vehicles or journeys.

Examples include:

- maximum height
- maximum width
- maximum length
- maximum gross weight
- axle-weight restriction
- prohibited vehicle class
- prohibited access
- time-dependent restriction
- temporary restriction
- closure
- bridge restriction
- low-clearance warning
- local access restriction
- hazardous-material restriction

A restriction must be temporal when the underlying fact is temporal.

Minimum conceptual metadata:

- `id`
- restriction type
- value/condition
- geographic target
- effective-from / effective-until when known
- source/provenance reference
- observed/received/validated timestamps
- confidence/status

### 3.8 Location

Represents the stable TruckFood identity of a real-world place or operational site.

Location is the primary geographic entity, not Restaurant.

Minimum conceptual data:

- `id`
- name
- geographic position
- address/administrative context where available
- lifecycle/status
- source-independent identity metadata
- created/updated timestamps
- archived timestamp when applicable

A Location may contain multiple services/capabilities.

### 3.9 Location Capability / Service

Represents what is available at a Location.

Initial capability families include:

- truck parking
- restaurant/food
- fuel
- toilets
- showers
- rest area
- workshop/service
- accommodation
- shop/supermarket
- EV charging

Capabilities are deliberately separate from access/suitability.

A location can have a capability while a specific vehicle may still be unable to access that capability.

### 3.10 Access Rule

Represents conditions under which a Location, entrance or service can be accessed.

Access may vary by:

- vehicle dimensions
- weight
- vehicle class
- ADR/hazardous materials
- time
- entrance
- service
- temporary conditions

Access rules therefore must not be stored only as a boolean such as `truck_access=true`.

### 3.11 Suitability Assessment

Represents TruckFood's current assessment of whether a Location or access point is appropriate for a specific vehicle/context.

Conceptual states:

- `suitable`
- `suitable_with_conditions`
- `unsuitable_known`
- `unknown`
- `temporarily_unavailable`
- `insufficient_data`

The assessment must retain enough context to explain why it was produced, including relevant vehicle/profile, rules, evidence and evaluation time where applicable.

It is an assessment, not a legal guarantee.

### 3.12 Observation

Represents an observed fact or report, normally originating from a user/community or operational process.

Examples:

- parking currently full
- entrance blocked
- shower unavailable
- restaurant closed unexpectedly
- road restriction observed
- access difficult for a specific vehicle

Observations are evidence and should not automatically overwrite canonical facts.

Minimum metadata:

- observer/source
- observed time
- received time
- geographic/context reference
- statement/value
- confidence/status
- expiry/review time where appropriate

### 3.13 Review

Represents a user's evaluative opinion about a Location or service.

Reviews are intentionally different from factual observations.

A review may include:

- rating
- text
- user reference
- target Location/service
- created/updated time
- moderation status

A review must not be treated as an authoritative road or access restriction.

### 3.14 Provenance / Source Record

Represents where a critical fact originated and how it entered TruckFood.

Provenance classes established by discovery are:

1. Official
2. Provider
3. Community
4. Inference

Conceptual metadata:

- source class
- source owner/name
- source record identifier
- source URL/reference where permitted
- received timestamp
- observed timestamp when applicable
- validated timestamp
- review/expiry timestamp
- geographic precision
- confidence
- corroboration/conflict state
- licensing/use constraint reference

Provenance is attached to facts/evidence, not merely to an entire Location record.

### 3.15 External Reference

Maps a TruckFood canonical entity to an external provider identifier.

Examples:

- OSM object/reference
- Google Place reference
- HERE reference
- TomTom reference
- future provider identifiers

External IDs never become the TruckFood primary identity.

Multiple external references may map to one canonical Location when justified.

### 3.16 Provider Snapshot

Represents raw or normalized provider information retained for integration/audit purposes when licensing permits.

Provider snapshots are explicitly outside the canonical domain model.

Retention, caching and storage are subject to the provider's commercial and licensing terms.

## 4. Relationship Model

Conceptually:

```text
USER
 ├──< VEHICLE
 │      └── VEHICLE_PROFILE (versioned)
 │
 └──< JOURNEY
        └── ROUTE
              └──< ROUTE_SEGMENT
                     └──< RESTRICTION

LOCATION
 ├──< LOCATION_CAPABILITY / SERVICE
 ├──< ACCESS_RULE
 ├──< SUITABILITY_ASSESSMENT
 ├──< OBSERVATION
 ├──< REVIEW
 ├──< EXTERNAL_REFERENCE
 └──< PROVENANCE / EVIDENCE

RESTRICTION
 ├── geographic target
 ├── temporal conditions
 ├── provenance/evidence
 └── optional journey/segment relevance

SUITABILITY_ASSESSMENT
 ├── LOCATION or ACCESS target
 ├── VEHICLE_PROFILE context
 ├── relevant rules/evidence
 └── evaluation timestamp
```

`<` means one-to-many conceptually; exact relational cardinality remains an implementation decision.

## 5. Static Entities vs Time-Varying Facts

TruckFood must distinguish relatively stable identity from facts that can change.

### Relatively stable

- User identity
- Vehicle identity
- Location identity
- canonical capability identity
- external reference mapping

### Time-varying

- opening/access conditions
- parking availability
- temporary closures
- restrictions
- observations
- suitability assessments
- provider data snapshots
- reviews/moderation state

A time-varying fact must not silently mutate historical evidence when the product needs auditability.

## 6. Source of Truth Rules

The source of truth depends on the entity/fact:

| Domain | Canonical owner |
|---|---|
| User/account | TruckFood identity/auth system |
| Vehicle/Profile | Driver + TruckFood |
| Journey intent | TruckFood |
| External route result | Routing provider, represented through TruckFood route record |
| Location identity | TruckFood canonical entity |
| Provider POI attributes | Provider source, subject to licence |
| Official restriction | Competent official source when available |
| Community observation | Reporting user/community evidence |
| Suitability | TruckFood assessment derived from available evidence/rules |
| Review | User + TruckFood moderation |
| Provider identifier | External provider |

This does not mean an official source is always current or complete. Provenance and freshness remain mandatory.

## 7. Provider Data Boundary

The following must stay outside the core domain model:

- provider-specific request payloads
- provider-specific response objects
- provider authentication structures
- provider SDK model classes
- provider-specific geometry formats where not required by the domain
- provider-specific error objects

Adapters translate provider data into canonical TruckFood concepts.

Conceptually:

```text
External Provider
       ↓
Provider Adapter
       ↓
Normalization / Validation
       ↓
Canonical TruckFood Domain
       ↓
Persistence / API / UI
```

The reverse path may be used when TruckFood needs to request provider services, but provider models must not leak into domain logic.

## 8. Identity and Deduplication

TruckFood needs stable internal IDs for canonical entities.

A provider must never be assumed to be the identity authority for a Location.

Potential duplicate locations from different sources must be resolved through an explicit matching/merge process using evidence such as:

- geographic proximity
- name similarity
- address
- business/service characteristics
- external identifiers
- human validation where needed

Automatic merging must not destroy conflicting evidence.

## 9. Lifecycle and Deletion

The default strategy is non-destructive lifecycle management.

Where historical integrity matters, records should be archived/deactivated rather than physically deleted.

Conceptual lifecycle:

`Created → Validated → Published → Confirmed → Updated → Archived`

User-controlled deletion and legal/privacy deletion requirements remain separate concerns and must be handled through explicit policies.

## 10. MVP Persistence Scope

The MVP should prioritize these entities:

### Required foundation

- User / Driver
- Vehicle
- Vehicle Profile
- Location
- Location Capability / Service
- Access Rule (minimal)
- Observation
- Review
- Provenance / Source Record
- External Reference

### Journey intelligence preparation

- Journey
- Route
- Route Segment
- Restriction
- Suitability Assessment

These can be introduced progressively, but their boundaries should be respected from the beginning so the MVP does not require a destructive redesign when route intelligence is added.

### Later / optional

- media asset management
- favorites
- notifications
- analytics events
- advanced moderation workflows
- provider snapshot warehouse
- collaborative conflict resolution

## 11. Database Direction

The current product stack remains compatible with PostgreSQL/Supabase as established during discovery.

A geospatial database extension such as PostGIS is a strong candidate because Location, road segments and geographic restrictions are spatial concepts. However, this ADR does not freeze that implementation until architecture and provider/licensing decisions are completed.

Exact SQL tables, column types, indexes, constraints, RLS policies and migrations belong to the implementation phase.

## 12. Non-Goals

This ADR does not decide:

- exact SQL schema;
- exact PostGIS geometry strategy;
- exact trust/confidence algorithm;
- exact route safety algorithm;
- exact API schema;
- exact provider;
- permanent provider caching rights;
- legal interpretation of restrictions;
- autonomous truck navigation;
- final analytics/event schema.

## 13. Safety Rules Preserved

The domain model must preserve the existing safety boundary:

> The absence of a known restriction is not proof of absence of a restriction.

A missing restriction record means **unknown**, not automatically safe.

Likewise, a Location with parking capability does not imply that every truck can physically or legally reach that parking area.

## 14. Consequences

### Positive

- Prevents restaurant-centric modelling from becoming an architectural constraint.
- Keeps vehicle context connected to journey intelligence.
- Preserves provenance and uncertainty.
- Supports multiple providers without vendor lock-in.
- Allows a physical Location to expose several services.
- Supports future restriction and route intelligence without replacing the MVP domain.
- Makes conflicting and time-varying information representable.

### Costs / trade-offs

- More domain concepts are required than in a simple restaurant app.
- Trust/provenance creates additional persistence and UI complexity.
- Deduplication becomes an explicit product/operations problem.
- Provider adapters require upfront architecture work.
- Historical integrity can increase storage requirements.

These costs are accepted because the product's central value depends on reliable truck-relevant information rather than simple POI discovery.

## 15. Follow-up Decisions

The next ADR/specification work should define:

1. provenance/trust data structures and explainable confidence;
2. restriction and effective-time representation;
3. system architecture and module boundaries;
4. API contracts;
5. security/privacy and Supabase RLS strategy;
6. spatial storage and query strategy;
7. provider adapter contracts;
8. MVP database migration plan.
