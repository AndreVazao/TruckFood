# ADR-0011 — Security, Privacy, Authorization and Row-Level Security

- **Status:** Proposed
- **Date:** 2026-10-14
- **Decision owners:** TruckFood project
- **Scope:** Product, application/API, persistence, community submissions, administration and offline data
- **Depends on:** ADR-0005 (domain/persistence model), ADR-0008 (architecture boundaries), ADR-0009 (API boundaries), ADR-0010 (offline packages)

## 1. Context

TruckFood will handle user accounts, vehicle profiles, journeys, saved places and potentially sensitive location-related information. It will also accept community observations about parking, services and road/access conditions. These records may be wrong, stale, abusive or deliberately misleading.

The planned stack includes Supabase as a candidate for authentication and persistence, but the exact database schema, policies and implementation have not yet been approved. Security must be designed before the first production migration or public client.

## 2. Decision

Adopt a **least-privilege, deny-by-default security model** with authorization enforced at the server and persistence boundaries, not only by hiding UI controls.

The design must distinguish public information, authenticated user-owned information, moderated community content and privileged administration. Supabase Row-Level Security (RLS) is the current candidate for database-level enforcement if Supabase is selected. Equivalent enforcement must be provided if the persistence platform changes.

This ADR defines requirements and direction; it does not claim that policies, tests or application code have already been implemented.

## 3. Data access classes

### 3.1 Public, intentionally published data

Anonymous users may read only fields deliberately approved for public discovery, such as published location/service details and approved public observations. Public responses must not expose private user identifiers, private journeys, contact details, moderation notes, internal risk signals or operational secrets.

A record being geographically useful does not automatically make every field associated with it public.

### 3.2 Authenticated user-owned data

A user may access and modify only their own private profile, vehicle profiles, saved places, preferences and private journey records, subject to explicit product rules. Ownership must be checked using trusted authenticated identity, not a user ID supplied by the client alone.

Other users must not be able to read or modify these records by guessing IDs or calling APIs/database endpoints directly.

### 3.3 Community submissions

New observations, reviews, photos and access reports are untrusted input. Submission does not automatically make content authoritative or publicly visible. Publication, moderation, correction, expiry and withdrawal must preserve provenance and history where appropriate.

A user's permission to submit does not imply permission to approve their own content or modify another person's submission.

### 3.4 Moderator and administrator operations

Privileged actions must be explicitly role-gated and auditable. Roles and privileges must be derived from trusted server/database-controlled assignments, never from arbitrary client-provided fields. Administrative access should be limited to the minimum actions necessary for the assigned role.

## 4. Authentication and authorization boundaries

- Authentication establishes identity; authorization decides what that identity may do.
- Every protected use case must perform server-side authorization.
- API endpoints must validate input and enforce ownership/role rules even when RLS is also enabled.
- Database policies must remain effective when a caller bypasses the intended UI and accesses the database API directly.
- Anonymous access must be explicitly allowed only for intended public operations.
- Service-role keys, database credentials, provider secrets and other privileged tokens must never be embedded in mobile/web client bundles, committed to the repository or returned to users.
- Public provider keys, if any, must be restricted according to the provider's supported controls and must not be treated as server secrets.
- Development, preview and production credentials/data should be separated.

## 5. Supabase RLS direction

If Supabase/Postgres is selected:

1. Enable RLS on every exposed table containing user-owned, private, moderation or non-public operational data before exposing it through client-accessible APIs.
2. Define policies per operation (select, insert, update and delete) and per access class; avoid broad policies that grant all operations to every authenticated user.
3. Use trusted authenticated-user identity checks and trusted role claims or server-controlled role tables for privileged operations.
4. Ensure insert and update policies validate both the existing row and the proposed row where applicable, so ownership cannot be reassigned by changing an owner field.
5. Review views, functions, RPCs, storage buckets and related database objects for privilege escalation or RLS bypass behaviour.
6. Keep service-role access server-side and narrow its use to trusted backend jobs/operations.
7. Document any intentionally public table or policy and its exposed fields.
8. Treat RLS as a defence-in-depth control, not a substitute for application-level validation, authorization, monitoring or tests.

Exact table names, SQL policies and claims design remain implementation decisions and must be reviewed against the final schema.

## 6. Location privacy and journeys

Precise location, route history and journey patterns can reveal sensitive personal behaviour. TruckFood should collect and retain only what is needed for a clearly explained feature.

- Do not publish a driver's live or historical position by default.
- Do not expose private origin/destination pairs, saved locations or journey history through public location/search endpoints.
- Make any location-sharing feature explicit, scoped and revocable.
- Explain when location is processed and whether it is stored or shared.
- Avoid logging precise coordinates, tokens or full sensitive request payloads unless strictly necessary; prefer redaction and minimisation.
- Define retention periods and deletion behaviour before production launch.

## 7. Offline packages and local device data

Offline capability must not silently turn private account data into a permanently exposed local cache.

- Separate public offline content from private user-specific data.
- Store only the minimum data required for offline features.
- Document whether local storage is encrypted and what protections are available on each target platform; do not claim encryption unless verified.
- Define logout behaviour for private cached data, including whether private caches are cleared immediately.
- Consider shared/lost/stolen devices, app reinstall, interrupted sync and account switching.
- On sync, re-check server authorization and ownership; never trust a locally cached permission or role.
- Preserve provenance and conflict state when offline observations are synchronised. Local creation time must not be mistaken for server validation time.
- Clearly distinguish downloaded public map/location data from private vehicle profiles or journey information.

## 8. Uploads and untrusted input

Photos, text, coordinates and other submissions must be treated as untrusted. The implementation plan must define file type/size limits, content validation, safe storage paths, access rules, abuse controls and moderation workflows. User-supplied text must not be trusted as instructions or authoritative road-safety evidence.

## 9. Abuse prevention and auditability

Before public launch, define proportionate rate limits, spam/duplicate controls, reporting and moderation procedures, and alerts for suspicious activity. Privileged changes to restrictions, suitability assessments, moderation outcomes and role assignments should be auditable with actor, timestamp, action and relevant record reference. Audit logs must not become an uncontrolled store of secrets or sensitive location history.

## 10. User rights and lifecycle

Product and legal review must define applicable consent, privacy notice, data export, correction, deletion, retention and account closure flows. Deletion must consider backups, derived records, moderation/audit obligations and legal retention; exceptions must be documented rather than silently ignored.

The implementation should support data minimisation and avoid collecting information solely because it may be useful someday.

## 11. Required security validation

Before any production release that handles real user data, test at minimum:

- anonymous caller versus public/private records;
- User A versus User B for read, insert, update and delete;
- attempts to change record ownership;
- user attempts to assign themselves moderator/admin roles;
- direct database/API calls that bypass the intended UI;
- moderator/admin permissions and audit events;
- private data returned through search, joins, views, RPCs or storage;
- invalid, oversized and abusive submissions/uploads;
- logout, account switching, offline cache and subsequent sync;
- expired/revoked sessions and missing/invalid authorization;
- secrets absent from client bundles, logs and repository history.

Automated tests should use separate identities and representative fixtures. Passing a UI-only test is not sufficient evidence that access controls work.

## 12. Consequences

### Positive

- Establishes privacy and authorization as architecture requirements before implementation.
- Reduces risk of cross-user data exposure and accidental public disclosure.
- Aligns community trust controls with the provenance model.
- Provides explicit test cases for database and API security.
- Makes offline functionality account for local-device privacy and sync authorization.

### Costs and trade-offs

- More policy design and testing is required before implementation.
- Public/private field boundaries and moderation workflows must be specified carefully.
- RLS, server authorization and storage policies can be complex and must be reviewed together.
- Privacy-by-design may constrain analytics, retention and convenience features.

## 13. Open questions

- Confirm Supabase/Postgres as the production persistence and authentication platform.
- Define the final data classification for each entity and field.
- Choose role representation and moderator/admin lifecycle.
- Define exact retention, export, deletion and consent requirements with appropriate legal review.
- Select local-storage protections supported by each target platform.
- Decide which offline data is public, account-specific or excluded.
- Define operational incident response, backups, secret rotation and access review.

## 14. Implementation gate

No production schema or client-facing database access should be considered ready until the selected platform, data classification, ownership rules, RLS/policy matrix, secret handling, offline cache rules and security test plan have been reviewed. This ADR is a proposed design decision, not evidence of implemented security.
