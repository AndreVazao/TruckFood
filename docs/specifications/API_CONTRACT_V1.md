# TruckFood — API Contract v1

- **Status:** Proposed contract — review required before implementation
- **Date:** 2026-11-10
- **Related:** ADR-0008, ADR-0009, ADR-0011, ADR-0013, ADR-0014, ADR-0016, ADR-0017, ADR-0018; `DATABASE_SCHEMA_V1.md`

## 1. Purpose

This document defines the first TruckFood-owned HTTP API contract shared by Android phones, Android tablets and the PC/web experience. It establishes resource boundaries, request/response conventions, authentication and authorization expectations, error semantics, pagination, idempotency and an MVP endpoint proposal.

It is a design specification, not a deployed API. No endpoint, server, database, authentication flow or provider integration is claimed implemented.

## 2. Contract principles

1. Clients call TruckFood-owned endpoints; provider SDK types and provider identifiers do not leak into public contracts.
2. The API is use-case/resource oriented, versioned and documented independently of client UI.
3. Every protected operation authenticates the caller and authorizes the target resource on the server.
4. Client-supplied owner, role, permission or organization claims are never trusted without server-side verification.
5. Unknown, missing, unconfirmed, not-applicable, stale, conflicting, partial and unavailable are distinct states.
6. A successful empty search is not an error. Partial provider results are not presented as complete.
7. Mutations validate input, apply transaction-safe invariants and return canonical TruckFood IDs.
8. Retry-safe create/update operations support idempotency where duplicate effects would matter.
9. Responses expose provenance, freshness and confidence when they affect driver decisions.
10. The API must never imply that no known restriction means a route or access is safe.
11. Sensitive provider credentials remain server-side.
12. API compatibility changes are deliberate and documented.

## 3. Base URL, versioning and media types

Proposed production base path:

`/api/v1`

All examples use relative paths. Hostname, deployment platform, authentication issuer and CORS policy remain deployment decisions.

- Request and response media type: `application/json`.
- Character encoding: UTF-8.
- Timestamps: ISO 8601/RFC 3339 with UTC offset; server-generated timestamps are UTC (`Z`).
- IDs: UUID strings.
- Units: metres, kilograms and degrees unless a field explicitly says otherwise.
- Coordinates: named `latitude` and `longitude` fields; never ambiguous positional arrays in the public API.
- Unknown/null semantics: a field's schema must state whether omission means unknown, not supplied or not applicable. Safety-critical fields use explicit state metadata.

Breaking changes require a new major version. Additive optional fields and new enum values still require clients to tolerate unknown values. Clients must not crash or silently reinterpret an unknown safety-related enum.

## 4. Authentication and request context

Protected endpoints require an authenticated user session using the selected identity provider. The exact token format is deployment-specific and must not be hard-coded into the domain contract.

Expected headers:

| Header | Use |
|---|---|
| `Authorization: Bearer <token>` | Required for protected operations |
| `Accept: application/json` | Response format |
| `Content-Type: application/json` | JSON body |
| `Idempotency-Key: <opaque-key>` | Required for designated retry-sensitive mutations |
| `X-Request-Id: <uuid>` | Optional client correlation ID; server generates one if absent |

The server derives the authenticated subject from validated credentials. An `owner_user_id`, role or permission in the request body is ignored or rejected; it cannot override the authenticated subject.

Anonymous access is permitted only for explicitly public, published location/service discovery operations. Draft, moderation, personal profile, vehicle, journey and contributor data require authorization.

## 5. Common response envelope

Successful single-resource response:

```json
{
  "data": {
    "id": "uuid",
    "resource": "..."
  },
  "meta": {
    "request_id": "uuid",
    "api_version": "v1"
  }
}
```

Successful collection response:

```json
{
  "data": [],
  "meta": {
    "request_id": "uuid",
    "api_version": "v1",
    "page": {
      "limit": 20,
      "next_cursor": null,
      "has_more": false
    },
    "result_state": "complete"
  }
}
```

The envelope is stable; resource-specific fields belong inside `data`. A collection with no matches returns HTTP 200, an empty `data` array and `result_state: complete`.

For multi-provider searches, `result_state` may be `complete`, `partial`, `degraded` or `unavailable`. Include structured warnings and source/freshness metadata where relevant. Never convert provider failure into an apparently complete empty result.

## 6. Error contract

Error response:

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "The request contains invalid fields.",
    "details": [
      {
        "field": "vehicle.height_m",
        "reason": "must_be_positive"
      }
    ],
    "retryable": false
  },
  "meta": {
    "request_id": "uuid",
    "api_version": "v1"
  }
}
```

The `message` is safe for display/logging and must not disclose secrets or internal stack traces. `details` must not leak another user's data. Clients should branch on stable `code`, not parse human-readable text.

### Stable initial error codes

| HTTP | Code | Meaning | Client behaviour |
|---:|---|---|---|
| 400 | `BAD_REQUEST` | Malformed request or invalid syntax | Correct request |
| 401 | `UNAUTHENTICATED` | Missing, invalid or expired credentials | Re-authenticate |
| 403 | `FORBIDDEN` | Authenticated but not permitted | Do not retry unchanged |
| 404 | `NOT_FOUND` | Resource absent or intentionally concealed | Treat as unavailable |
| 409 | `CONFLICT` | State/version/idempotency conflict | Refresh and resolve |
| 410 | `EXPIRED` | Resource or action has expired | Obtain a new resource/session |
| 413 | `PAYLOAD_TOO_LARGE` | Body/upload exceeds limit | Reduce payload |
| 415 | `UNSUPPORTED_MEDIA_TYPE` | Unsupported content type | Use supported format |
| 422 | `VALIDATION_FAILED` | Syntactically valid but semantically invalid | Correct indicated fields |
| 429 | `RATE_LIMITED` | Rate/quota limit reached | Respect retry guidance |
| 500 | `INTERNAL_ERROR` | Unexpected server failure | Retry only if operation is safe |
| 502 | `UPSTREAM_ERROR` | Provider/upstream failure | Use partial/degraded state if available |
| 503 | `SERVICE_UNAVAILABLE` | Service temporarily unavailable | Retry with backoff |
| 504 | `UPSTREAM_TIMEOUT` | Upstream timed out | Retry within policy |

Additional domain codes:

- `RESOURCE_ARCHIVED`
- `RESOURCE_NOT_PUBLISHED`
- `STALE_VERSION`
- `IDEMPOTENCY_KEY_REUSED`
- `VEHICLE_PROFILE_INCOMPLETE`
- `VEHICLE_ATTRIBUTE_UNKNOWN`
- `PROVIDER_CAPABILITY_UNSUPPORTED`
- `PROVIDER_COVERAGE_INSUFFICIENT`
- `RESULTS_PARTIAL`
- `EVIDENCE_STALE`
- `EVIDENCE_CONFLICTING`
- `ACCESS_SUITABILITY_UNKNOWN`
- `RESTRICTION_EVALUATION_INSUFFICIENT_DATA`

HTTP status and domain code must agree with documented semantics. A provider timeout must not be reported as an empty successful result.

## 7. Pagination, filtering and sorting

Collection endpoints accept bounded pagination:

- `limit`: default 20, proposed maximum 100.
- `cursor`: opaque server-issued continuation token.
- `next_cursor`: null when no more results.
- Stable sort order must include a deterministic tie-breaker (normally canonical ID).
- Cursors must not expose internal SQL or provider state.

Filters are allowlisted per endpoint. Unknown filter names return `400 BAD_REQUEST`; clients must not construct arbitrary database query expressions. Sorting fields and direction are explicitly enumerated.

Offset pagination may be used for small administrative/reference lists only if its consistency and cost are acceptable. Cursor pagination is preferred for changing location/observation collections.

## 8. Idempotency and concurrency

- Designated POST operations require `Idempotency-Key`.
- Scope keys to authenticated actor, endpoint/operation and relevant tenant.
- Store a request digest and outcome; same key + same request returns the original outcome.
- Same key + different request returns `409 IDEMPOTENCY_KEY_REUSED`.
- Key retention is bounded and documented.
- Updates to versioned resources use an explicit version/ETag precondition where needed.
- A stale update returns `409 STALE_VERSION`; clients fetch current state and reconcile.
- Idempotency does not replace authorization or transaction constraints.

## 9. Initial endpoint catalogue

The list is a proposed MVP API surface. It does not mean all operations belong in the first public release; the release scope must be frozen before implementation.

### 9.1 Health and capability discovery

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/health` | Public/minimal | Liveness only; no secrets |
| GET | `/capabilities` | Public | API feature/version capabilities |

Health responses must not expose database credentials, environment variables, stack traces or detailed infrastructure topology.

### 9.2 Current user and driver profile

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/me` | User | Current authenticated subject and safe profile summary |
| PATCH | `/me/profile` | User | Update own display/preferences |

The server derives the user identity. A client cannot create or edit another user's profile by passing a different ID.

### 9.3 Vehicle profiles

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/vehicle-profiles` | User | List own profiles |
| POST | `/vehicle-profiles` | User | Create personal profile |
| GET | `/vehicle-profiles/{profileId}` | Owner | Read own profile and current version |
| PATCH | `/vehicle-profiles/{profileId}` | Owner | Update profile metadata only |
| POST | `/vehicle-profiles/{profileId}/versions` | Owner | Create a new immutable technical version |
| GET | `/vehicle-profiles/{profileId}/versions/{versionId}` | Owner | Read a specific version |
| POST | `/vehicle-profiles/{profileId}/activate-version` | Owner | Set current version after ownership/version validation |
| POST | `/vehicle-profiles/{profileId}/archive` | Owner | Archive profile without erasing historical references |

A technical version used in a journey cannot be overwritten. Creating a new version does not mutate past journeys. Safety-critical missing attributes remain explicit and may block a truck-sensitive evaluation.

### 9.4 Location discovery

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/locations` | Public, published fields only | Search/filter locations |
| GET | `/locations/{locationId}` | Public if published | Read public location details |
| GET | `/locations/{locationId}/services` | Public if published | List services/capabilities |
| GET | `/locations/{locationId}/evidence-summary` | Public-safe projection | Show evidence status/freshness summary |

Proposed query filters: `country_code`, `locality`, `capability`, `latitude`, `longitude`, `radius_m`, `cursor`, `limit`. Coordinate/radius search is enabled only when the selected spatial backend and query are validated. Maximum radius and bounding-box limits must be configured to prevent expensive unrestricted scans.

Public responses omit private author details, moderation notes, internal risk flags and non-redistributable provider payloads.

### 9.5 Community observations and reviews

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `/locations/{locationId}/observations` | User | Submit an observation |
| GET | `/locations/{locationId}/observations` | Public approved projection | Read approved observations |
| POST | `/locations/{locationId}/reviews` | User, if reviews in MVP | Submit a review |
| GET | `/locations/{locationId}/reviews` | Public published projection | Read published reviews |
| POST | `/observations/{observationId}/report` | User | Report content for moderation |

New contributions begin untrusted/pending unless a reviewed policy explicitly defines another safe path. Users can edit/delete only their own content subject to audit, retention and moderation rules. Public APIs never expose moderation queues.

### 9.6 Journeys (conditional MVP scope)

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/journeys` | Owner | List own journey history |
| POST | `/journeys` | Owner | Create journey with selected vehicle version |
| GET | `/journeys/{journeyId}` | Owner | Read own journey |
| POST | `/journeys/{journeyId}/complete` | Owner | Complete journey |
| POST | `/journeys/{journeyId}/cancel` | Owner | Cancel journey |

Journey creation must snapshot the exact vehicle attributes used. Journey endpoints do not imply continuous GPS tracking. Route planning/evaluation endpoints are deferred until provider capability, licensing and safety semantics are approved.

### 9.7 Future organization/fleet API — not MVP

Potential future namespaces:

- `/organizations`
- `/organizations/{organizationId}/memberships`
- `/organizations/{organizationId}/invitations`
- `/organizations/{organizationId}/groups`
- `/organizations/{organizationId}/vehicles`
- `/organizations/{organizationId}/assignments`
- `/organizations/{organizationId}/location-sessions`

These routes require ADR-0016/0017 authorization, tenant-aware persistence, privacy/legal review and audit. They must not be exposed merely because their names are listed here.

## 10. Representative request and response contracts

### 10.1 Create a personal vehicle profile

Request:

```json
{
  "name": "Conjunto principal",
  "initial_version": {
    "configuration_code": "tractor_semitrailer",
    "overall_length_m": 16.5,
    "overall_width_m": 2.55,
    "overall_height_m": 4.0,
    "gross_mass_kg": 40000,
    "axle_count": 5,
    "adr_status": "unknown",
    "completeness_state": "needs_review"
  }
}
```

The example values are illustrative only, not recommended vehicle defaults. The server validates ranges and the user's ownership. It must not mark the profile verified merely because values were supplied.

Response (illustrative shape):

```json
{
  "data": {
    "id": "uuid",
    "name": "Conjunto principal",
    "status": "draft",
    "current_version": {
      "id": "uuid",
      "version_number": 1,
      "configuration_code": "tractor_semitrailer",
      "overall_length_m": 16.5,
      "overall_width_m": 2.55,
      "overall_height_m": 4.0,
      "gross_mass_kg": 40000,
      "axle_count": 5,
      "adr_status": "unknown",
      "completeness_state": "needs_review"
    }
  },
  "meta": {
    "request_id": "uuid",
    "api_version": "v1"
  }
}
```

### 10.2 Search published locations

Request:

`GET /api/v1/locations?country_code=PT&capability=parking&latitude=38.7223&longitude=-9.1393&radius_m=15000&limit=20`

Response (illustrative):

```json
{
  "data": [
    {
      "id": "uuid",
      "name": "Example service area",
      "country_code": "PT",
      "capabilities": ["parking", "food", "toilet"],
      "location_state": "published",
      "evidence_summary": {
        "state": "reported",
        "last_observed_at": "2026-11-09T10:00:00Z",
        "freshness": "needs_review"
      },
      "truck_access": {
        "state": "unknown",
        "reason_code": "NO_VALIDATED_VEHICLE_ACCESS_ASSESSMENT"
      }
    }
  ],
  "meta": {
    "request_id": "uuid",
    "api_version": "v1",
    "page": {
      "limit": 20,
      "next_cursor": null,
      "has_more": false
    },
    "result_state": "complete"
  }
}
```

The example is illustrative, not a real location or a claim of data availability. The API must not infer that a location is truck-accessible from the presence of parking.

### 10.3 Submit an observation

Request:

```json
{
  "observation_kind": "parking_capacity",
  "statement": "Several marked heavy-vehicle spaces were occupied.",
  "observed_at": "2026-11-09T09:30:00Z"
}
```

Response indicates the canonical observation ID and moderation state (`pending` or the policy-approved state). The client must not represent a pending report as verified fact.

## 11. Domain response states

Use explicit enums rather than booleans for complex outcomes.

### Search result state

- `complete`
- `partial`
- `degraded`
- `unavailable`

### Evidence state

- `active`
- `superseded`
- `expired`
- `withdrawn`
- `conflicting`
- `invalidated)

### Freshness state

- `fresh`
- `aging`
- `needs_review`
- `expired`
- `unknown`

### Vehicle attribute state

For safety-critical values, use a value plus an explicit state where applicable:

- `known`
- `unknown`
- `unconfirmed`
- `not_applicable`

A null value alone must not be interpreted differently by different clients.

### Access/suitability state

- `suitable`
- `suitable_with_conditions`
- `unsuitable_known`
- `unknown`
- `temporarily_unavailable`
- `insufficient_data`

## 12. Validation and limits

Proposed baseline limits to validate through load/cost tests:

- JSON request body: 1 MiB for ordinary API operations; uploads use separate signed/authorized upload flow.
- Collection page: default 20, maximum 100.
- Search radius: configured per endpoint; no unbounded global scans.
- Text fields: field-specific maximum lengths.
- Rate limits: differentiated by anonymous search, authenticated reads, community writes and administrative operations.
- Coordinates: latitude -90..90, longitude -180..180; reject invalid/non-finite values.
- Numeric vehicle fields: positive dimensions, non-negative mass, bounded precision/ranges, domain-specific completeness checks.
- Timestamps: reject malformed values and invalid intervals.
- JSON extension objects: schema-versioned, bounded depth/size and allowlisted keys.

Exact quotas, radius caps and retention windows are deployment/product decisions; do not hard-code arbitrary limits without testing and cost review.

## 13. Security requirements

- Authenticate and authorize every protected request on the server.
- Apply least privilege and deny by default (ADR-0017).
- Verify resource ownership on reads, updates, deletes and nested routes.
- Do not trust client-supplied user/organization/role/permission fields.
- Use parameterized queries and schema validation.
- Keep provider secrets and service-role credentials server-side.
- Rate-limit public search and community submissions.
- Validate upload content, size and ownership; do not trust file extensions or client MIME claims.
- Protect state-changing browser requests against CSRF where cookie-based auth is used.
- Enforce TLS in production and secure token storage in clients.
- Redact tokens, personal data and precise location from logs.
- Audit privileged operations, moderation, exports and sensitive location reads.
- Apply the same authorization to background jobs, webhooks, exports and object storage.
- If Supabase is selected, enforce RLS as defence in depth and test it with real database roles.

## 14. Observability and request correlation

Every response includes a server-generated `request_id`. Server logs correlate the request ID with latency, operation, safe error code and provider outcome. Logs must not include bearer tokens, raw personal location, full request bodies by default or secret provider payloads.

Provider calls should record adapter, capability, latency, outcome and cost/quota metadata without exposing provider credentials. Metrics must distinguish complete, partial, degraded, timeout, rate-limited and unsupported results.

## 15. Compatibility and client behaviour

- Android phone, Android tablet and PC/web clients share the same domain contract.
- Clients must tolerate additive response fields and unknown non-critical enum values.
- Unknown safety-critical states render as unknown/insufficient data, never as safe.
- Clients must show stale/partial warnings where supplied.
- Offline clients may display previously downloaded/saved data with its timestamp and limitations; they must not present it as current.
- Clients must not cache private data beyond approved policy or reuse another account's cache after logout.
- API changes must be accompanied by contract fixtures and compatibility tests.

## 16. Minimum API contract test suite

1. Anonymous request to protected profile returns 401.
2. User A cannot read or mutate User B's vehicle profile.
3. User A cannot access User B's journey by guessing its UUID.
4. Client-supplied owner ID cannot change resource ownership.
5. Unknown vehicle attributes remain unknown in responses.
6. Missing safety-critical dimensions do not produce a verified profile.
7. A new vehicle version does not mutate a prior journey snapshot.
8. Published location response excludes private contributor/moderation fields.
9. Draft or suspended location is not exposed through public discovery.
10. Empty search returns 200 with empty data and complete state when providers succeeded.
11. Provider failure is represented as partial/degraded/unavailable, not a false empty result.
12. Stale evidence includes freshness metadata.
13. Conflicting evidence remains distinguishable.
14. Invalid coordinates/radius are rejected.
15. Pagination cursor cannot be modified to expose another tenant/user's records.
16. Repeated idempotency key with same request does not duplicate a write.
17. Reused idempotency key with different request returns conflict.
18. Stale version update returns conflict.
19. Rate limit returns 429 and safe retry guidance.
20. Error bodies contain no stack traces, secrets or other-user data.
21. Nested resource ownership is verified (location/service, profile/version, journey/snapshot).
22. Client cannot set moderation state to approved/published.
23. Upload authorization verifies owner, size and content.
24. Logs and request correlation do not expose tokens or precise location by default.
25. Unknown future enum values do not crash clients or become a safe/positive state.

## 17. Open decisions before implementation

1. Select HTTP framework, deployment target and identity provider.
2. Confirm whether journeys and reviews belong in MVP.
3. Decide exact location search semantics and spatial backend.
4. Decide whether public location discovery is anonymous or requires optional sign-in for richer features.
5. Approve API rate limits, quotas, maximum search radius and upload limits using cost tests.
6. Freeze vehicle schema and multi-trailer/axle representation before profile endpoints are implemented.
7. Approve moderation, reporting and deletion workflows.
8. Approve error catalog and enum evolution policy.
9. Approve privacy, logging and retention rules.
10. Generate OpenAPI 3.1 from the reviewed contract and add automated schema/contract tests before coding.

## 18. Implementation status

**Not implemented.** This document specifies proposed API behaviour only. No HTTP route, controller, OpenAPI document, auth middleware, database query, provider adapter or deployed service has been created by this specification.
