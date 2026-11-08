# TruckFood — Database Schema Specification v1

- **Status:** Proposed specification — not an executable migration
- **Date:** 2026-11-08
- **Related:** ADR-0005, ADR-0011, ADR-0012, ADR-0016, ADR-0017, ADR-0018

## 1. Purpose and boundary

This specification narrows ADR-0018 into a first, reviewable database contract. It identifies the minimum useful persistence slice for the first TruckFood product: identity, driver-owned vehicle profiles, locations/services, provenance, community observations and basic journeys.

It intentionally does not activate fleet subscriptions, live GPS tracking, provider raw-payload retention, full restriction intelligence or offline map packages in the first migration. Their future tables must not be improvised as nullable columns in MVP tables.

**No SQL has been applied.** Names and types below are proposed PostgreSQL-oriented contracts. PostgreSQL/PostGIS and Supabase remain conditional until hosting, extension, cost, backup/restore, licensing and security validation are complete.

## 2. Design rules

1. UUID primary keys generated server-side.
2. UTC timestamps using `timestamptz`; use half-open effective intervals `[from, to)`.
3. Canonical measurements use metric units: metres, kilograms and degrees. API/UI conversions happen at boundaries.
4. Every persisted user-owned record has an explicit owner relationship.
5. Tenant-owned data introduced later carries `organization_id` and tenant-aware foreign keys.
6. Public location fields and private contributor/moderation fields are separate access surfaces.
7. Provider IDs are references, not canonical primary keys.
8. No safety-critical vehicle measurement is silently defaulted.
9. Unknown, unconfirmed and not-applicable are explicit states, not interchangeable nulls.
10. Core history is archived or anonymized through explicit workflows; broad cascading deletes are prohibited.
11. RLS and server authorization must be tested together if Supabase is selected.
12. All externally sourced records preserve source, retrieval time, terms and allowed use.

## 3. First migration scope

### Included in the first persistence slice

- `user_profiles`
- `vehicle_profiles`
- `vehicle_profile_versions`
- `vehicle_profile_components` (if combination modeling is needed for MVP; otherwise add before accepting multi-trailer profiles)
- `locations`
- `location_geometries` (initially point/entrance types only if geometry support is validated)
- `location_capabilities`
- `location_services`
- `sources`
- `provenance_records`
- `external_references`
- `observations`
- `reviews` (only if review moderation and ownership are in the first release)
- `journeys` (only when journey history is in the MVP release)
- `journey_vehicle_snapshots`

A migration should not create unused tables simply because they appear in the long-term model. The release scope must decide whether journeys/reviews are in the first deploy; the core location discovery and vehicle profile foundations are the minimum.

### Explicitly deferred

- Organizations, memberships, invitations, groups and fleet assignments.
- Subscription, billing, plans, entitlements and usage.
- Driver-phone live location sessions and telemetry.
- Full restriction/effective-time engine and route-segment matching.
- Offline map package manifests and tile/graph storage.
- Provider payload snapshots unless licensing has been approved.
- Full route geometry retention unless provider terms permit it.

Deferred domains have already been architected in ADR-0015 through ADR-0018; deferral is a sequencing decision, not abandonment.

## 4. Proposed table contracts

The following column types are indicative. Exact enum strategy, PostGIS geometry types and generated constraints require implementation review.

### 4.1 `user_profiles`

| Column | Type | Rules / purpose |
|---|---|---|
| id | uuid | PK; same identity UUID as authenticated subject where provider supports it |
| display_name | text | Optional public-facing name; length bounded |
| avatar_path | text | Optional private/storage reference, never arbitrary executable URL |
| locale | text | Optional validated locale |
| created_at | timestamptz | Required |
| updated_at | timestamptz | Required |

Private account/security metadata belongs to the identity provider or restricted server-side records, not this public-facing profile row.

### 4.2 `vehicle_profiles`

| Column | Type | Rules / purpose |
|---|---|---|
| id | uuid | PK |
| owner_user_id | uuid | FK to user_profiles.id; required for personal profiles |
| name | text | User label, bounded |
| ownership_kind | text | Initial value personal; future organization ownership is a separate model |
| status | text | draft, active, archived |
| current_version_id | uuid | Optional FK to version; must belong to this profile |
| created_at / updated_at | timestamptz | Required |

Do not permit an arbitrary client to set ownership or publish a profile without authorization. A later fleet profile must not be represented by pretending it is a personal profile.

### 4.3 `vehicle_profile_versions`

| Column | Type | Rules / purpose |
|---|---|---|
| id | uuid | PK |
| vehicle_profile_id | uuid | FK to vehicle_profiles.id |
| version_number | integer | Positive; unique per profile |
| configuration_code | text | Controlled domain code |
| overall_length_m | numeric(8,3) | Nullable only when unknown/not supplied; positive when present |
| overall_width_m | numeric(8,3) | Same |
| overall_height_m | numeric(8,3) | Same |
| gross_mass_kg | numeric(12,2) | Non-negative when present |
| axle_count | smallint | Nullable; positive when present |
| adr_status | text | not_applicable, applicable, unknown, unconfirmed |
| adr_details | jsonb | Validated schema/version; no arbitrary unbounded payload |
| permit_context | jsonb | Validated, versioned permit attributes |
| completeness_state | text | draft, incomplete, verified, needs_review |
| created_at | timestamptz | Required; immutable after use |

Axle-group loads and trailer components must be modeled explicitly before the product evaluates axle restrictions. Do not infer axle loads from gross mass. If `current_version_id` is stored on the parent, enforce same-profile ownership with a composite unique key/FK or derive current version through a controlled query.

### 4.4 `vehicle_profile_components` (conditional first slice)

| Column | Type | Rules / purpose |
|---|---|---|
| id | uuid | PK |
| profile_version_id | uuid | FK to vehicle_profile_versions.id |
| sequence_no | smallint | Positive; order in combination |
| component_kind | text | tractor, rigid_body, trailer, dolly, load or controlled extension |
| length_m / width_m / height_m | numeric(8,3) | Optional, positive when present |
| gross_mass_kg | numeric(12,2) | Optional, non-negative |
| axle_configuration | jsonb | Validated and versioned; use normalized axle rows before axle-level calculations |
| attributes | jsonb | Bounded validated extension fields |

Unique `(profile_version_id, sequence_no)`. Do not claim this table alone is sufficient for legal axle-load calculations until axle-group structure and measured load semantics are specified.

### 4.5 `locations`

| Column | Type | Rules / purpose |
|---|---|---|
| id | uuid | PK |
| name | text | Required, bounded |
| description | text | Optional, bounded |
| lifecycle_status | text | draft, published, suspended, archived |
| visibility | text | public or restricted |
| country_code | char(2) | ISO country code |
| administrative_area | text | Optional |
| locality | text | Optional |
| address_text | text | Optional display address; not a routing authority |
| created_by_user_id | uuid | Nullable system/import actor; FK when user-originated |
| created_at / updated_at | timestamptz | Required |

Do not put every capability into a single category enum. Public read views must omit private contributor, moderation and internal risk fields.

### 4.6 `location_geometries`

| Column | Type | Rules / purpose |
|---|---|---|
| id | uuid | PK |
| location_id | uuid | FK to locations.id |
| geometry_kind | text | site_point, site_area, entrance, parking_area, service_area |
| geometry | geometry | PostGIS type/SRID to be chosen after validation |
| precision_m | numeric(8,2) | Optional, non-negative |
| source_provenance_id | uuid | FK to provenance_records.id, where known |
| observed_at | timestamptz | Optional |
| created_at | timestamptz | Required |

A point is not automatically an entrance. Geometry validity, SRID, longitude/latitude ordering and source rights must be validated at ingestion. If PostGIS is unavailable or not approved, this table must use a documented interim representation and must not pretend spatial indexes exist.

### 4.7 `location_capabilities`

| Column | Type | Rules / purpose |
|---|---|---|
| code | text | PK; stable code such as parking, food, fuel, shower, toilet, rest |
| label | text | Display label |
| active | boolean | Required |

Controlled reference data. Capability codes must be stable and not coupled to translated UI text.

### 4.8 `location_services`

| Column | Type | Rules / purpose |
|---|---|---|
| id | uuid | PK |
| location_id | uuid | FK to locations.id |
| capability_code | text | FK to location_capabilities.code |
| child_location_id | uuid | Optional FK when service is represented as a child location |
| status | text | reported, confirmed, unavailable, suspended, unknown |
| attributes | jsonb | Bounded, schema-versioned service details |
| provenance_id | uuid | FK to provenance_records.id, when evidence exists |
| valid_from / valid_to | timestamptz | Optional half-open real-world validity |
| created_at / updated_at | timestamptz | Required |

The same physical site may expose multiple services. Service status must not imply truck access suitability.

### 4.9 `sources`

| Column | Type | Rules / purpose |
|---|---|---|
| id | uuid | PK |
| source_code | text | Unique stable identifier |
| source_class | text | official, provider, community, inferred |
| publisher_name | text | Required |
| terms_url | text | Optional reference |
| attribution_text | text | Optional |
| coverage_notes | text | Optional |
| created_at / updated_at | timestamptz | Required |

Licensing rights must be assessed per use: display, transient processing, caching, persistent storage, transformation, redistribution and offline use.

### 4.10 `provenance_records`

| Column | Type | Rules / purpose |
|---|---|---|
| id | uuid | PK |
| source_id | uuid | FK to sources.id |
| source_record_id | text | Optional external record reference |
| collection_method | text | import, provider_api, user_report, moderator, official_publication |
| observed_at | timestamptz | Optional |
| received_at | timestamptz | Required |
| validated_at | timestamptz | Optional |
| effective_from / effective_to | timestamptz | Optional half-open interval |
| freshness_expires_at | timestamptz | Optional review/expiry |
| evidence_status | text | active, superseded, expired, withdrawn, conflicting, invalidated |
| confidence | numeric(4,3) | Optional 0..1; must not replace status |
| attribution | text | Optional |
| rights_code | text | Controlled policy reference |

Freshness, confidence and evidence status are independent. Conflicts remain visible to the evaluation layer.

### 4.11 `external_references`

| Column | Type | Rules / purpose |
|---|---|---|
| id | uuid | PK |
| entity_type | text | Controlled canonical entity family |
| entity_id | uuid | Canonical entity ID; polymorphic reference requires server validation |
| provider_code | text | Stable namespace |
| external_id | text | Provider's identifier |
| first_seen_at / last_seen_at | timestamptz | Required |

Unique `(entity_type, provider_code, external_id)`. Because polymorphic FKs cannot be enforced with one ordinary FK, consider typed link tables for high-integrity entities instead of relying on application-only validation.

### 4.12 `observations`

| Column | Type | Rules / purpose |
|---|---|---|
| id | uuid | PK |
| location_id | uuid | FK to locations.id |
| service_id | uuid | Optional FK to location_services.id |
| author_user_id | uuid | FK to user_profiles.id; nullable for approved imports |
| observation_kind | text | Controlled type |
| statement | text | Bounded user-visible report |
| observed_at | timestamptz | Required |
| received_at | timestamptz | Required |
| moderation_status | text | pending, approved, rejected, needs_review |
| provenance_id | uuid | FK to provenance_records.id |
| created_at / updated_at | timestamptz | Required |

An observation is evidence, not authoritative truth. Rate limits, abuse controls and moderation are application/security requirements.

### 4.13 `reviews` (only if in MVP)

| Column | Type | Rules / purpose |
|---|---|---|
| id | uuid | PK |
| location_id | uuid | FK to locations.id |
| author_user_id | uuid | FK to user_profiles.id |
| rating | smallint | 1..5 |
| body | text | Optional, bounded |
| moderation_status | text | pending, published, rejected, hidden |
| created_at / updated_at | timestamptz | Required |

Unique policy (one review per user/location or multiple visits) remains a product decision. Review scores must not be treated as proof of access suitability.

### 4.14 `journeys` and `journey_vehicle_snapshots` (only if journey history is in MVP)

`journeys` fields: id UUID PK; owner_user_id FK; selected_vehicle_profile_id optional FK; selected_vehicle_version_id optional FK; origin/destination as validated structured values; status; started_at/completed_at; created_at/updated_at.

`journey_vehicle_snapshots` fields: id UUID PK; journey_id unique FK; source_profile_id/version_id nullable historical references; snapshot_schema_version; snapshot JSONB validated by server; captured_at. The snapshot must contain every vehicle attribute actually used by an evaluation and preserve unknown/not-applicable states.

No live location history is implied by journey persistence. Route/provider payloads require separate licensing approval.

## 5. Cross-table integrity requirements

Before the first migration is approved, write executable tests for:

- vehicle version number unique within a profile;
- profile current version belongs to that same profile;
- positive dimensions and non-negative mass;
- service capability references a known capability;
- service child location belongs to a valid location hierarchy without cycles;
- geometry has expected SRID/type and valid coordinates;
- provenance source exists and effective intervals are valid;
- confidence is null or within 0..1;
- review rating is between 1 and 5;
- journey snapshot belongs to exactly one journey and cannot be silently rewritten;
- public queries never expose private contributor or moderation fields;
- owner A cannot read/write owner B's profile, journey or observations;
- unauthenticated users can read only deliberately published public location/service data;
- client-supplied owner IDs cannot create cross-user records.

For the future tenant model, add tests proving that organization A cannot reference or access organization B's groups, assets, assignments, sessions, snapshots or audit data.

## 6. Index strategy for the first release

Candidate indexes, subject to query plans:

- `vehicle_profiles(owner_user_id, status)`
- `vehicle_profile_versions(vehicle_profile_id, version_number)` unique
- `locations(lifecycle_status, country_code, locality)`
- `location_services(location_id, capability_code, status)`
- `provenance_records(source_id, evidence_status, received_at)`
- `observations(location_id, moderation_status, observed_at DESC)`
- `reviews(location_id, moderation_status, created_at DESC)`
- `journeys(owner_user_id, created_at DESC)`

Add GiST indexes only after PostGIS type/SRID and representative spatial queries are chosen. Do not create indexes for hypothetical filters without measuring read/write cost.

## 7. API and authorization implications

- Clients never write directly to tables that require multi-row invariants unless the operation is mediated by a validated server/database transaction.
- Owner IDs and organization IDs are derived from authenticated context or checked against it; they are not trusted because the client supplied them.
- Public location reads use an allowlisted projection/view, not unrestricted table access.
- Draft locations, pending observations, moderation data, source credentials and provider payloads are not public.
- A profile version used by a journey is immutable from the client's perspective.
- Any update that changes the profile's current version must verify ownership and version membership atomically.
- If Supabase is chosen, RLS policies and security-definer functions require explicit review and tests. Do not use a service-role key in a mobile or browser client.

## 8. Migration order and gates

1. Confirm identity provider and user UUID mapping.
2. Confirm PostgreSQL/PostGIS hosting and local-development parity.
3. Approve the exact MVP scope (especially reviews and journey history).
4. Approve measurement units, null/status semantics and vehicle combination representation.
5. Approve location geometry types/SRID and source licensing.
6. Produce SQL migration and rollback/recovery notes.
7. Run clean-database migration tests and integrity tests.
8. Run owner isolation, anonymous public-read and privilege-escalation tests.
9. Seed synthetic fixtures and validate nearby/location/service queries.
10. Only then deploy to a non-production environment.

## 9. Explicit non-goals

This specification does not claim:

- that TruckFood has a live or provisioned database;
- that Supabase has been selected or configured;
- that PostGIS is enabled;
- that RLS policies or SQL migrations exist;
- that location, route or restriction data has been imported;
- that provider licensing has been approved;
- that the proposed schema is ready for production without review and tests.

## 10. Decisions still required

1. Confirm first-release inclusion of journeys and reviews.
2. Confirm whether personal vehicle profiles support multi-trailer/axle components in the first release or whether the MVP limits evaluation to a smaller explicitly declared subset.
3. Decide whether polymorphic external references are acceptable or typed link tables are required.
4. Decide whether public locations may be created by users directly as drafts or only through moderated submissions.
5. Approve exact data-retention periods for observations, reviews, journey history and account deletion.
6. Select identity/database hosting after cost, privacy, backup/restore and operational validation.

## 11. Change control

Any change to ownership, tenant boundaries, safety-critical vehicle fields, evidence lifecycle, public/private exposure or location retention must update this specification and the relevant ADR before migration. Migration files must be reviewed as code and linked to a version of this specification.
