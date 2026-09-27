# ADR-0007 — Restriction & Effective-Time Domain Model

**Status:** Accepted — Discovery / Foundation
**Date:** 2026-09-27
**Decision:** TruckFood will represent restrictions as scoped, typed, time-aware domain facts that are evaluated against vehicle context and evidence. A restriction is never treated as globally applicable merely because it exists.

## 1. Context

TruckFood's core mission includes helping professional drivers avoid unsuitable roads and access points.

Existing discovery establishes restrictions such as maximum height, maximum weight, maximum width, maximum length, prohibited vehicle class, prohibited access, time-dependent restriction, temporary restriction, road closure, bridge restriction, low-clearance warning and local access restriction.

The model must also preserve provenance, freshness, geographic precision and uncertainty.

This ADR defines the domain semantics before database or routing implementation.

## 2. Decision

A Restriction is a fact about access or movement within a defined geographic scope and, when applicable, a defined time window and vehicle condition.

Conceptually:

Restriction = Scope + Rule + Applicability + Time + Evidence

The model must distinguish:

1. what is restricted;
2. where it is restricted;
3. when it is restricted;
4. to which vehicle/context it applies;
5. what evidence supports the restriction.

## 3. Restriction Target

A restriction may apply to:

- road segment;
- bridge;
- tunnel;
- entrance/access road;
- intersection/access point;
- location entrance;
- location/service;
- area/corridor;
- journey-relevant geographic feature.

The target must be explicit.

A restriction on a road must not automatically be interpreted as a restriction on the destination itself.

A restriction on a location's entrance must not automatically imply that every entrance is restricted.

## 4. Restriction Type

The initial taxonomy is:

### Dimension
- maximum height;
- maximum width;
- maximum length.

### Mass
- maximum gross weight;
- maximum axle weight.

### Vehicle / access
- prohibited vehicle class;
- prohibited access;
- local access restriction;
- hazardous-material / ADR restriction.

### Operational
- time-dependent restriction;
- temporary restriction;
- road closure;
- bridge restriction;
- low-clearance warning.

This taxonomy is deliberately extensible.

A provider-specific restriction type may be preserved at the integration boundary while being mapped to a canonical TruckFood type only when its semantics are understood.

## 5. Rule Representation

A restriction contains a rule describing the condition.

Conceptually:

Rule = Operator + Value + Unit + Optional Vehicle Condition

Examples:

- height > 4.00 m → access prohibited;
- gross weight > 7.5 t → access prohibited;
- width > 2.55 m → access prohibited;
- ADR = true → access prohibited;
- vehicle class = HGV → access prohibited.

The exact machine-readable rule language is deferred.

The domain must nevertheless preserve the semantic distinction between a threshold, categorical prohibition, warning, conditional rule and complete closure.

## 6. Hard Restriction vs Warning

Not every restriction-like fact means the same thing.

Initial semantic categories:

- prohibition — access/movement is stated as not permitted;
- limit — access is permitted only within a defined threshold;
- warning — a condition is known and requires attention but is not itself a legal prohibition;
- closure — movement/access is unavailable during the applicable period;
- conditional — applicability depends on vehicle, time, permit or another condition.

TruckFood must not convert a warning into a prohibition without evidence.

Likewise, it must not convert an absence of a warning into permission.

## 7. Vehicle Applicability

Restriction evaluation may use:

- vehicle type/class;
- overall height;
- overall width;
- overall length;
- gross permitted mass;
- current/estimated mass when relevant;
- axle count;
- axle weight when relevant;
- trailer/semi-trailer configuration;
- ADR/dangerous-goods relevance;
- refrigerated/special operational context where relevant.

A missing vehicle attribute must not automatically be interpreted as satisfying the restriction.

Example: if a road has a maximum height of 4.00 m and vehicle height is unknown, TruckFood should not conclude that the vehicle fits.

The result is unknown/insufficient data until the necessary context is available.

## 8. Time Model

Restrictions may have several distinct temporal concepts:

- valid_from — when the restriction becomes applicable;
- valid_until — when it ceases to be applicable;
- recurring schedule — weekdays or defined time windows;
- exception periods — dates/times during which the normal rule does not apply;
- observed_at — when the underlying fact was observed;
- received_at — when TruckFood received the evidence;
- validated_at — when the information was last checked;
- review_after — when TruckFood should reconsider the evidence.

These concepts must not be collapsed into one timestamp.

A temporary restriction may therefore be valid even when the evidence was received earlier or later.

## 9. Recurring Restrictions

The model must support recurring conditions without requiring a separate restriction record for every occurrence.

Examples:

- Monday-Friday 07:00-10:00;
- weekends only;
- night-time closure;
- seasonal restrictions.

The exact recurrence syntax is an implementation decision.

The semantic model must represent:

Applicable = Base Validity + Recurrence + Exceptions

## 10. Exceptions

Restrictions may contain explicit exceptions.

Examples:

- local residents;
- emergency vehicles;
- authorised deliveries;
- vehicles below a threshold;
- vehicles with a permit;
- defined time periods.

Exceptions must be represented as conditions, not hidden in free-text notes.

Where the exception cannot be reliably interpreted, TruckFood should preserve the source information and present applicability as uncertain rather than inventing a rule.

## 11. Geographic Scope and Precision

The restriction target must retain its geographic precision.

Initial conceptual target types:

- exact point;
- entrance;
- road segment;
- bridge;
- tunnel;
- corridor;
- area;
- location/service.

A restriction with approximate geography must not be applied as though it were an exact road-segment restriction.

When provider geometry is used, licensing and storage rights remain applicable.

## 12. Directionality

A restriction may apply:

- both directions;
- one direction;
- a defined travel direction;
- an entrance/exit direction.

Directionality must therefore be part of the restriction semantics where relevant.

A one-way restriction must never be silently expanded to both directions.

## 13. Lanes and Sub-Features

Some restrictions may apply only to:

- a specific lane;
- a specific entrance;
- a specific carriageway;
- a specific service access.

The domain may represent these as more precise targets or sub-features.

MVP implementations may initially omit lane-level modelling where the source does not provide reliable precision.

## 14. Provenance and Evidence

Every critical restriction must reference its evidence/provenance.

At minimum the system should know:

- source class;
- source record;
- source identifier;
- observed time;
- received time;
- validated time;
- review/expiry information;
- geographic precision;
- conflict state;
- confidence/presentation state.

This follows ADR-0006.

An inferred restriction must identify the evidence and rule used to derive it.

## 15. Conflicting Restrictions

Two sources may disagree.

Examples:

- provider says unrestricted;
- official notice says temporary closure;
- driver reports a blocked access.

TruckFood must preserve both evidence records.

The assessment layer decides the current presentation state.

Possible results include:

- confirmed restriction;
- reported restriction;
- conflicting;
- expired/needs review;
- unknown.

The domain must never resolve a conflict merely by deleting the weaker-looking source.

## 16. Restriction Lifecycle

Conceptual lifecycle:

Discovered → Validated → Active → Superseded/Expired → Archived

Additional states may include:

- conflicting;
- withdrawn;
- invalidated.

A historical restriction should remain available where auditability requires it.

## 17. Evaluation Result

When a restriction is evaluated against a vehicle and time context, the result is not itself the restriction.

Conceptually:

Restriction + Vehicle Profile + Time + Evidence + Rules → Evaluation

Possible conceptual outcomes:

- applies;
- does_not_apply;
- potentially_applies;
- unknown;
- insufficient_data;
- expired;
- conflicting.

The result should retain enough context to explain why it was produced.

## 18. Safety Boundary

The absence of a restriction record is not a does_not_apply result.

It is an absence of evidence.

Likewise:

- unknown vehicle height + 4.00 m limit → unknown/insufficient data;
- stale temporary closure → expired/needs review;
- conflicting sources → conflicting;
- approximate restriction location → uncertainty must be preserved;
- provider coverage gap → not equivalent to unrestricted road.

This distinction is mandatory for future route intelligence.

## 19. Relationship with Suitability

Restriction evaluation is one input to suitability, not the entire suitability system.

Conceptually:

Vehicle + Route/Location Access + Restrictions + Other Evidence + Time → Suitability Assessment

A location can have no known restriction and still have insufficient information to be considered suitable.

## 20. MVP Direction

The MVP should establish the model so future route intelligence does not require redesign.

Initial support should cover:

- restriction type;
- target;
- rule/value/unit;
- basic vehicle applicability;
- validity period;
- provenance;
- evidence timestamps;
- active/expired/conflicting state;
- directionality where available;
- evaluation state.

Recurring schedules, complex exceptions, lane-level restrictions and advanced rule evaluation can be introduced progressively.

## 21. Non-Goals

This ADR does not decide:

- exact SQL schema;
- exact geospatial storage;
- exact recurrence syntax;
- exact rule engine;
- final route algorithm;
- legal interpretation of regulations;
- provider-specific mapping completeness;
- autonomous navigation;
- final UI wording.

## 22. Consequences

### Positive

- Prevents restriction data from becoming an unstructured collection of flags.
- Preserves time and geographic scope.
- Supports different vehicle configurations.
- Makes conflicts and uncertainty explicit.
- Provides a clean foundation for future route intelligence.
- Keeps provider-specific semantics outside the core model where they are not understood.

### Costs / trade-offs

- Temporal rules are more complex than a simple blocked flag.
- Evaluation requires vehicle and time context.
- Conflict resolution becomes an explicit concern.
- Spatial precision affects storage and querying.
- Some source semantics will remain unknown until validated.

These costs are accepted because incorrect truck restriction information is a critical product risk.

## 23. Follow-up Decisions

Next work should define:

1. system/module architecture;
2. API boundaries;
3. security/privacy and Supabase RLS;
4. spatial storage/query strategy;
5. provider adapter contracts;
6. MVP database migration plan;
7. practical freshness policies by data family;
8. validation of restriction semantics against real Portugal/Europe sources.
