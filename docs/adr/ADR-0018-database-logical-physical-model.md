# ADR-0018 — Database Logical and Physical Model

- **Status:** Proposed — pending validation
- **Date:** 2026-11-08
- **Decision owners:** TruckFood product/architecture
- **Related decisions:** ADR-0005, ADR-0006, ADR-0007, ADR-0008, ADR-0011, ADR-0012, ADR-0014, ADR-0015, ADR-0016, ADR-0017

## 1. Context

TruckFood has a sufficiently broad canonical domain to define a coherent relational persistence model. This decision translates that domain into logical table families, key relationships, tenant boundaries, temporal rules and physical-design constraints.

The model must preserve: driver-owned personal data; multi-tenant fleet data; complete and versioned vehicle configurations; historical journey context; location/service/access distinctions; time-dependent restrictions; evidence and provenance; privacy-sensitive location sessions; and subscription entitlements.

This ADR is a design proposal. It does **not** create a database, run migrations, enable PostGIS, configure RLS or implement application code.

## 2. Decision summary

1. Prefer a relational PostgreSQL model, with PostGIS for spatial data if hosting, extension availability, licensing, backup/restore and query tests validate the choice (ADR-0012).
2. Use TruckFood-owned UUID identifiers for canonical entities. Provider identifiers are external references, never canonical primary keys.
3. Separate personal identity from organization membership; organization assets from technical vehicle profiles; vehicle profile definitions from immutable journey snapshots; and locations from services, entrances, access rules and suitability assessments.
4. Use explicit tenant ownership and composite tenant-aware foreign keys for organization-owned records. Enforce authorization in the server and database; UI filtering is not a security boundary.
5. Model facts with effective time, observation/receipt time, provenance and lifecycle where relevant. Preserve conflicting evidence instead of overwriting it.
6. Store sensitive live-location data in a narrowly scoped family with explicit session, purpose, expiry, retention and audit controls.
7. Use migrations, deterministic fixtures and automated integrity/security tests. Do not freeze physical SQL until the validation gates in this ADR are satisfied.

## 3. Logical model and table families

Names below are proposed logical names, not a final migration contract. Normalized tables are preferred for relationships and history; JSON/JSONB is reserved for bounded provider payloads, variable source attributes or versioned snapshots where querying every field relationally is not required.

### 3.1 Identity and personal driver context

- `users`: application identity keyed to the chosen identity provider subject; account lifecycle and minimal platform metadata.
- `driver_profiles`: one optional personal driver profile per user; display/preferences and driver-specific settings.
- `user_devices`: registered device metadata and revocable sessions/tokens; never store reusable plaintext secrets.
- `user_consents` or purpose-specific consent/notice records: version, purpose, actor, timestamp and withdrawal where legally appropriate. Consent is not assumed to be the lawful basis for every processing purpose.

Personal driver data remains owned by the user. Joining or leaving an organization must not transfer ownership of the personal account/profile.

### 3.2 Organizations, membership and access

- `organizations`: tenant identity, status and lifecycle.
- `organization_memberships`: organization/user relationship, status, joined/left timestamps.
- `organization_invitations`: invitation lifecycle, target, expiry and secure token digest; never persist raw invitation secrets.
- `organization_role_grants`: role assignments with scope and effective lifecycle, if roles are persisted separately from membership.
- `groups`: groups owned by exactly one organization.
- `group_memberships`: user membership in a group, constrained to the same organization.
- `permission_definitions` and `role_permission_grants`: optional database-backed registry if permissions are made data-driven; otherwise stable permission identifiers may live in versioned application policy.

An active group membership must be backed by an active membership in the same organization. Membership, role grant and group membership are separate relationships. No cross-tenant foreign-key path is permitted.

### 3.3 Vehicle profiles and fleet assets

- `vehicle_profiles`: reusable technical profile owned by a user or organization according to explicit ownership rules; includes profile identity and lifecycle.
- `vehicle_profile_versions`: immutable version records with dimensions, gross mass, axle/axle-group configuration and loads, configuration, trailer composition, ADR attributes and permit context.
- `vehicle_profile_components`: optional normalized composition records for tractor, rigid body, trailer(s), multiple trailers and other combination components.
- `fleet_vehicles`: organization-owned operational asset/registration record, separate from the reusable technical profile.
- `fleet_vehicle_profile_links`: effective-dated link between an asset and a technical profile/version, where a fleet asset needs a validated configuration.
- `vehicle_assignments`: time-bounded relationship among organization, driver membership, fleet vehicle, optional group and operational purpose.

A vehicle profile version must not be silently edited after use. Correcting a profile creates a new version. A journey references the exact version and stores a self-contained snapshot of all safety-relevant values actually used. Missing, unknown, unconfirmed and not-applicable values remain distinct; no default dimensions or weights may be substituted.

Assignments preserve history. Overlap/exclusivity is an explicit policy per assignment type, not a universal database assumption. Where a policy forbids overlap, use a transaction-safe constraint or serialized application operation and test concurrent writes.

### 3.4 Journeys and route evaluation

- `journeys`: owner, optional organization/assignment context, origin/destination, lifecycle and selected vehicle context.
- `journey_vehicle_snapshots`: immutable snapshot and profile-version reference used for that journey.
- `routes`: route candidate/version, provider and evaluation lifecycle.
- `route_segments`: ordered segments with geometry/reference, direction and relevant evaluation context.
- `route_evaluations`: result state, evaluated vehicle snapshot, provider capability/version, data freshness and limitations.
- `route_restriction_matches`: link between a route/segment and applicable or potentially applicable restrictions, including evaluation outcome and evidence references.

A journey must remain historically interpretable if the driver's profile, fleet assignment, provider or restriction data changes later. Route geometry and provider payload retention are conditional on provider licensing. Never claim that a route is truck-safe merely because no known restriction matched.

### 3.5 Locations, services and access

- `locations`: canonical TruckFood place/site identity, public/private lifecycle, name and core descriptive metadata.
- `location_geometries`: one or more typed geometries per location (site point/area, entrance, parking area, service area), with SRID, precision and source quality. A site pin is not an entrance.
- `location_capabilities`: controlled capability definitions such as parking, food, fuel, showers, toilets, accommodation, workshop and rest.
- `location_services`: service instances offered at a location, optionally linked to child locations and capability definitions.
- `location_entrances`: explicit access points with direction, geometry and operational status.
- `access_rules`: vehicle/service/entrance-specific access conditions and applicability.
- `suitability_assessments`: result for a specific vehicle context, service/entrance and assessment time; preserve suitable, conditional, known unsuitable, unknown, temporarily unavailable and insufficient-data states.

Do not collapse service capability, physical access and vehicle suitability into one category field. A location may have several services and different access outcomes for each.

### 3.6 Restrictions and temporal applicability

- `restrictions`: canonical restriction identity, type, scope, rule and lifecycle.
- `restriction_geometries`: point/line/area spatial scope, directionality and spatial quality.
- `restriction_applicability`: vehicle classes and parameter conditions, including dimensions, gross/axle weight, ADR, access class and permits.
- `restriction_time_rules`: effective start/end, recurrence/time zone, exceptions and temporary windows.
- `restriction_evidence_links`: links to supporting source/evidence records.

A restriction's rule, geographic scope, vehicle applicability, effective time and evidence must be independently inspectable. Missing vehicle attributes cannot satisfy a restrictive condition. Evaluation outcomes include applies, does-not-apply, potentially-applies, unknown, insufficient-data, expired and conflicting.

### 3.7 Evidence, provenance and community

- `sources`: source registry entry, source class, publisher, terms/licence and known coverage.
- `source_records`: source-specific record identity, retrieval metadata and source revision.
- `provenance_records`: origin, collection method, timestamps, attribution and rights/retention constraints.
- `external_references`: provider/source namespace plus external identifier, linked to a canonical entity; uniqueness is scoped by provider and entity type.
- `provider_snapshots`: bounded raw/normalized payload snapshots only where terms permit; include provider, schema/version, retrieval time, expiry and permitted use.
- `observations`: time-stamped factual reports with actor/source, location/service/subject and moderation lifecycle.
- `reviews`: user feedback and moderation state, separated from factual observations.
- `evidence_links`: typed links connecting evidence to restrictions, locations, access rules, suitability and assessments.

Evidence status (active, superseded, expired, withdrawn, conflicting, invalidated) is distinct from freshness and confidence. Provider payloads must not become canonical truth by being ingested. Retention and redistribution must follow source-specific rights.

### 3.8 Fleet location sessions and telemetry

- `location_sharing_sessions`: driver, organization, assignment, device, purpose, start/end, visible status and revocation state.
- `location_samples`: timestamped phone/device coordinates, accuracy, capture source and session reference.
- `location_session_events`: start, pause, resume, stop, expiry, revocation and relevant failures.
- `location_access_audit`: access/export records for sensitive location information, with actor, scope, purpose and timestamp.

Only a valid, visible, purpose-bound session may accept samples. Session expiry, revocation, off-duty state and assignment changes must stop further collection/access according to policy. Phone GPS must be labelled as phone/device location, not vehicle tracker telemetry. Keep retention short and purpose-specific; do not infer driver absence, vehicle absence, misconduct or abandonment from stale/missing coordinates.

### 3.9 Plans, subscriptions and usage

- `plans`: versioned commercial plan definitions.
- `subscriptions`: organization subscription lifecycle and provider billing reference.
- `entitlements`: feature/limit grants derived from plan and explicit overrides.
- `usage_counters` or append-only `usage_events`: metered usage and period aggregation.
- `billing_webhook_events`: idempotency key, provider event reference, processing status and minimal audit metadata.

Billing status and entitlement evaluation are separate from authorization. A paid subscription does not bypass tenant/resource permission checks. Webhook processing must be authenticated, idempotent and auditable.

### 3.10 Audit and operational records

- `audit_events`: append-only security/business events with actor, tenant, action, resource reference, timestamp and minimal redacted context.
- `outbox_events`: transactional event publication where reliable asynchronous work is required.
- `idempotency_records`: scoped request keys and result metadata for retry-safe operations.
- `moderation_actions`: actor, target, decision, reason category and timestamp.

Avoid putting passwords, tokens, raw invitation secrets, full location histories or unnecessary personal data into generic logs.

## 4. Key and relationship conventions

- Canonical primary keys: UUID, generated server-side.
- Timestamps: UTC `timestamptz`; preserve the source time zone/offset where local civil-time rules matter.
- Physical dimensions: numeric values with explicit units and validated positive ranges; store canonical units and convert only at boundaries.
- Mass/load: numeric with explicit canonical units; gross vehicle mass and axle/axle-group loads remain separate.
- Coordinates: explicit longitude/latitude order at API boundaries; spatial columns use a documented SRID and geometry/geography type appropriate to each query.
- Enumerations: stable domain codes with controlled evolution; do not rely on UI labels as persisted values.
- Nullable fields: null means unknown/not supplied only when the field contract says so. Use explicit status fields where null would conflate unknown, unconfirmed, not applicable and absent.
- Foreign keys: restrictive by default for core history; use explicit archival/deletion workflows rather than cascading deletion through journeys, evidence or audit history.
- External IDs: unique by provider namespace and entity type, not globally unique.

For organization-owned tables, include `organization_id` where it materially improves tenant-scoped querying and policy clarity. Use composite foreign keys such as `(organization_id, group_id)` referencing a unique pair on the parent, so a row cannot point to a group from another tenant even if application code is defective. Where a user/organization ownership alternative exists, model it explicitly rather than permitting ambiguous nullable ownership combinations.

## 5. Constraints and indexes

The initial migration design should evaluate at least:

- Unique active membership per `(organization_id, user_id)`, with lifecycle/history strategy explicitly chosen.
- Unique group name/key within an organization where product rules require it.
- Unique provider external reference per `(provider, entity_type, external_id)`.
- Composite tenant-aware foreign keys for group, fleet vehicle, assignment and location-session references.
- Check constraints for positive dimensions, non-negative mass, valid time intervals, allowed status transitions where practical and coordinate validity.
- Effective-period indexes for assignments, profile links, restrictions and access rules.
- GiST spatial indexes for relevant PostGIS geometries; B-tree indexes for tenant IDs, lifecycle/status, foreign keys and time columns.
- Partial indexes for active/current records only when query plans demonstrate benefit.
- GIN indexes for JSONB only when measured query patterns justify them.
- Idempotency uniqueness scoped to actor/tenant/operation.
- Append-only or restricted-update policies for audit and immutable version/snapshot records.

Do not add every conceivable index up front. Use representative Portugal-first fixtures, EXPLAIN plans and measured query patterns. Spatial indexes do not prove route safety or data completeness.

## 6. Temporal and history rules

Use explicit time concepts rather than one ambiguous `updated_at`:

- `observed_at`: when a person/device/source says the fact was true.
- `received_at`: when TruckFood received it.
- `validated_at`: when a trusted process/person assessed it.
- `effective_from` / `effective_to`: when the fact applies in the real world.
- `expires_at` or review deadline: when the record should no longer be treated as fresh without review.
- `created_at` / `updated_at`: persistence lifecycle metadata.

Intervals should use a documented inclusive/exclusive convention (prefer half-open `[from, to)`) and explicit time zone handling for recurring local rules. Preserve superseded and conflicting records where needed for audit and historical route explanation. Do not mutate past journey snapshots when current profile data changes.

## 7. Tenant isolation and authorization enforcement

If Supabase is selected:

1. Every tenant-owned record must have a defensible organization scope, including indirect child tables.
2. RLS policies must enforce the ADR-0017 permission model; policies must not trust client-supplied role names or organization IDs without membership/resource validation.
3. Use helper functions only when their security-definer/search-path/ownership behaviour is reviewed and tested.
4. Separate public read access to deliberately published location fields from private contributor, moderation, fleet and operational fields.
5. Sensitive location tables default to no access; expose narrow server-authorized operations/views for active sessions only.
6. Service-role credentials remain server-side and are never shipped in mobile/web clients.
7. Test anonymous access, cross-user reads/writes, cross-tenant joins, revoked membership, group boundary, assignment expiry, role downgrade, exports, storage objects and offline sync.
8. Audit sensitive reads/exports as well as writes where required.

RLS is defence in depth, not a substitute for application authorization, and application checks are not a substitute for RLS.

## 8. Deletion, archival and retention

Define retention by data family and legal purpose before implementation. Prefer explicit lifecycle states and anonymization/deletion workflows over broad cascades. Personal account deletion must not accidentally erase legally required or operationally necessary organization records; equally, retention must not become indefinite by default. Separate public contribution attribution from personal identity where legally and technically justified. Location samples require a short, documented retention schedule and deletion propagation to replicas, exports and backups according to a disclosed policy.

Legal basis, controller/processor roles, employee monitoring implications, data subject rights and any required impact assessment must be reviewed for Portugal/EU before fleet location features are piloted.

## 9. Migration and implementation strategy

Proposed migration sequence:

1. Identity and personal driver context.
2. Canonical Location, capability/service and provenance foundations.
3. Vehicle profiles/versions and journey snapshots.
4. Restrictions, temporal applicability and evidence links.
5. Organization, membership, groups, fleet assets and assignments.
6. Authorization/RLS policies and security test fixtures.
7. Location-sharing sessions only after privacy/legal gates.
8. Plans, entitlements and usage only when commercial requirements are validated.
9. Spatial indexes and query optimization after representative data and hosting validation.

Every migration must be versioned, reviewable, repeatable in a clean environment and accompanied by rollback/recovery notes. Destructive transformations require a backup, explicit approval and a tested recovery path. Seed data must be clearly separated from production data.

## 10. Required validation before freezing SQL

- Confirm PostgreSQL and PostGIS versions/extensions, managed-hosting availability, pricing, backup/restore and local parity.
- Validate table ownership and composite tenant foreign keys against ADR-0016/0017.
- Review all nullable and safety-critical vehicle fields.
- Confirm spatial geometry types/SRID and representative query plans for nearby, corridor and restriction intersection.
- Confirm provider terms for raw payload retention, geometry storage, caching and offline distribution.
- Define location telemetry purpose, access, retention, revocation and legal review.
- Define deletion/export/anonymization and audit retention.
- Build migration tests, FK/check/uniqueness tests, concurrency tests and a minimum cross-tenant RLS matrix.
- Verify historical journeys remain reproducible when profile/provider/restriction records are revised.
- Confirm query and storage cost against realistic early-market volume.

## 11. Consequences

### Positive

- The model preserves the important distinctions already established in the domain.
- Tenant isolation can be enforced structurally as well as through policy.
- Historical journeys retain the vehicle and evidence context used at the time.
- Provider changes do not require replacing canonical TruckFood identities.
- Fleet location and billing remain isolated, auditable domains rather than incidental fields on user records.

### Costs and trade-offs

- More tables and explicit relationships increase initial modeling/migration work.
- Immutable versions, evidence history and temporal rules require lifecycle and retention discipline.
- RLS and tenant-aware constraints require careful test coverage.
- Spatial storage and provider snapshots may add hosting/storage costs and licensing complexity.
- JSON snapshots are flexible but must be versioned and validated; they must not become an unstructured substitute for core relational constraints.

## 12. Implementation status

**Not implemented.** This ADR documents a proposed logical/physical database design only. No SQL schema, migration, Supabase project configuration, PostGIS extension, RLS policy, index, trigger or application persistence layer has been created or applied by this decision.

## 13. Open questions

1. Is Supabase the selected first production persistence platform, or only the leading candidate?
2. Which vehicle-profile attributes should be normalized into component tables versus retained in a versioned validated snapshot?
3. Which organization-owned technical profiles may be reused across fleet vehicles, and who may edit/publish them?
4. Which route/provider geometry and payloads may legally be retained, and for how long?
5. Which community evidence needs immutable audit retention versus anonymization/deletion?
6. What are the exact privacy-approved retention periods for phone-location samples and access logs?
7. Which plan/entitlement dimensions are needed for the first commercial pilot?

## 14. References

- ADR-0005 — Initial Domain and Persistence Model
- ADR-0006 — Provenance, Trust and Confidence Model
- ADR-0007 — Restriction and Effective-Time Model
- ADR-0011 — Security, Privacy and Authorization/RLS
- ADR-0012 — Geospatial Storage and Query Strategy
- ADR-0015 — Fleet Organizations, Driver Groups and Live Location
- ADR-0016 — Organization Membership, Fleet Assignments
- ADR-0017 — Authorization Model and Permission Matrix
