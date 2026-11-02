# ADR-0016 — Organization, Membership, Fleet Groups and Assignment Domain

- **Status:** Proposed
- **Date:** 2026-11-02
- **Related:** ADR-0005, ADR-0008, ADR-0009, ADR-0011, ADR-0014, ADR-0015

## 1. Context

ADR-0015 established the direction for future B2B fleet management and driver-phone location sharing, but did not define the complete organization, membership, group, vehicle ownership or assignment lifecycle.

The domain must support transport companies, owner-operators and drivers who may work with more than one organization over time. It must distinguish a reusable technical Vehicle Profile, a real company Fleet Vehicle and a temporary driver-to-vehicle Assignment. These are separate concepts with separate ownership and lifecycles.

This ADR defines domain boundaries and invariants, not a database schema or implementation.

## 2. Decision

Adopt an explicit multi-tenant organization domain with separate concepts for:
1. TruckFood user identity and personal driver profile;
2. organizations and organization memberships;
3. invitations and membership lifecycle;
4. organization groups and group memberships;
5. fleet vehicles and versioned technical vehicle profiles;
6. effective-dated operational assignments;
7. subscription plans, entitlements and usage;
8. audit, ownership and retention records.

An organization is the tenant boundary for company-managed resources. A user's personal account remains independent and may participate in multiple organizations through explicit memberships.

## 3. Canonical domain model

### 3.1 User Account and Driver Profile

- User Account represents the authenticated TruckFood identity and is never owned by an organization.
- Driver Profile contains driver-controlled preferences and personal information, subject to privacy policy.
- Organization membership does not transfer ownership of the account or personal profile.
- A driver may have memberships in multiple organizations, subject to policy and applicable law.
- Employer-visible identity and personal/community identity must be separately controlled. Fleet membership does not automatically publish personal information.

### 3.2 Organization

An Organization represents a transport company, fleet operator or business customer. It has a stable TruckFood ID, legal/display name, country/jurisdiction, configured time zone, lifecycle state, timestamps and references to billing state.

Suggested lifecycle states: pending_setup, active, suspended, closing and closed.

A suspended or closing organization cannot create new memberships, assignments or location-sharing sessions. Read/export and closure behaviour must follow explicit policy. Billing-provider objects remain outside the canonical domain.

### 3.3 Organization Membership and invitations

Organization Membership links one user account to one organization. It is not a group membership or vehicle assignment.

Suggested lifecycle: invited, accepted, active, suspended, revoked and expired.

Requirements:
- Membership has a stable ID, organization ID, user ID when claimed, invitation reference, role grants, status and effective timestamps.
- Pending invitations grant no tenant access.
- Acceptance verifies the intended account. Invitation tokens are single-use, time-limited, safely stored and revocable.
- Email is an invitation/delivery attribute, not canonical user identity.
- Revocation/suspension takes effect on subsequent authorization checks and invalidates or re-evaluates relevant sessions/claims.
- Preserve audit history; do not delete membership records to hide former access.
- Re-invitation must not silently reactivate a revoked membership or inherit old privileges.
- Roles in one organization never carry into another.

### 3.4 Roles and permissions

Use organization-scoped role grants mapped to explicit permissions, not UI labels alone.

Candidate initial roles:
- owner: accountable organization owner; manages ownership transfer and closure.
- fleet_admin: manages settings, memberships, groups, fleet assets and assignments.
- dispatcher: manages operational groups/assignments and sees only information needed for authorized work.
- safety_manager: reviews authorized vehicle/compliance records, without automatic access to unrelated personal data.
- driver: accesses own membership context, assigned work/vehicle and explicitly enabled sharing controls.
- viewer: read-only access to explicitly scoped fleet information.

This is a candidate vocabulary, not a final permission matrix. Every operation is authorized server-side per resource. Deny by default. High-impact operations such as ownership transfer, billing changes, role escalation, exports, closure and retention overrides require stronger authorization and audit. Broad administrator access to all historical GPS points must not be assumed.

### 3.5 Groups and hierarchy

An Organization Group is a tenant-scoped operational grouping such as a depot, regional team, dispatch unit or subcontractor team.

- Each group belongs to exactly one organization.
- Optional parent groups support bounded, cycle-free hierarchy.
- Group membership is separate from organization membership and may be effective-dated.
- Active organization membership is required before group access is granted.
- Users may belong to multiple groups when explicitly assigned.
- Group membership grants only policy-defined scoped permissions and cannot bypass tenant authorization.
- Groups should normally be archived rather than hard-deleted.
- Cross-organization groups are not supported initially. Subcontractor collaboration requires explicit, audited collaboration grants.

### 3.6 Vehicle Profile versus Fleet Vehicle

Keep these concepts separate:

- Vehicle Profile describes technical configuration for journey evaluation: dimensions, gross mass, axle configuration/load, tractor, trailers, combination, ADR applicability, permits and jurisdiction-specific attributes. Profiles are versioned.
- Fleet Vehicle represents a real operational asset managed by an organization. It has an organization-owned identity, operational status, fleet reference/registration attributes and links to one or more versioned Vehicle Profiles.
- Personal Vehicle Profiles may be maintained independently by a driver and do not become company property when the driver joins a fleet.
- Copying/importing a personal profile into a company asset requires explicit authorization and a clear ownership/data-use rule.
- Configuration changes create a new profile version; historical journeys and assignments are never silently rewritten.
- Registration and identification fields are sensitive and require restricted visibility and retention controls.
- Candidate fleet asset states include draft, active, maintenance, inactive, retired and archived.

An assignment references the exact Fleet Vehicle and profile version used. Technical configuration must never be inferred from a generic label such as truck.

### 3.7 Assignments and operational history

An Assignment is an effective-dated operational relationship, not a permanent foreign-key shortcut.

Conceptual types:
- driver to fleet vehicle;
- driver to organization group;
- vehicle to organization group;
- driver to shift, work order or dispatch task, once that domain is defined.

Requirements:
- Store organization, subject, target, assignment type, status, start/end instants, operational time zone, creator, reason/reference and audit timestamps.
- Prevent invalid overlaps according to explicit policy. Do not assume every business permits only one driver per vehicle or one vehicle per driver: relief drivers, co-drivers, team operations and temporary swaps exist.
- Where exclusivity is required, enforce it transactionally on the server and return a clear conflict.
- Support planned, active, completed, cancelled and superseded states as appropriate.
- Reassignment closes/supersedes the prior period; it does not erase it.
- Historical assignments remain queryable by authorized users under retention policy.
- A driver may use a personal vehicle outside fleet assignments; this grants no company access.
- Journey records preserve driver, organization context, assignment and exact vehicle-profile snapshot applicable to the journey/evaluation.
- Corrections to historical assignments are auditable and do not silently rewrite derived journey facts.

### 3.8 Subscription, plans and entitlements

Separate commercial subscription state from authorization and domain ownership.

- Subscription records the commercial relationship and billing-provider references.
- Plan defines a versioned commercial offer.
- Entitlement represents a feature or limit granted to an organization for a period.
- Usage records metered events where quotas or billing require them.
- Billing provider identifiers and webhook payloads remain in an integration boundary.
- Authorization evaluates organization lifecycle and current entitlements; payment status alone is not an authorization rule.
- Grace periods, retries, plan changes, cancellation and suspension require explicit states/effective dates.
- Downgrades must not silently delete organization data or historical records; define read-only/export and retention behaviour.
- This ADR selects no billing provider, price or final plan limit.

## 4. Tenant isolation and authorization

Every tenant-owned resource carries an organization scope. Authorization verifies authenticated user, active membership, permission, resource organization, group/assignment scope and requested operation.

Required controls:
- deny-by-default server-side authorization;
- tenant-scoped queries/writes, including jobs and exports;
- database RLS if Supabase is selected, based on verified membership and permissions;
- never trust client-supplied organization IDs, roles, group IDs or assignment IDs without authorization;
- prevent cross-tenant object-reference/IDOR attacks;
- validate invitation claims and prevent token replay;
- promptly re-evaluate access after membership/role changes;
- audit privileged reads and mutations where justified;
- test anonymous, cross-user, cross-organization, suspended/revoked member, nested-group and stale-token cases;
- offline caches must have explicit expiry and authorization revalidation.

A global platform-operator role, if needed, is separate from organization roles, narrowly scoped, justified and audited.

## 5. Ownership, offboarding and lifecycle

On membership termination:
- stop new organization access when revocation takes effect;
- terminate or re-evaluate active location-sharing sessions and device authorization;
- remove the user from active groups and future assignments;
- preserve historical assignments and journeys according to retention policy;
- return/reassign organization-owned assets and tasks;
- do not delete the user's personal account or personal data merely because membership ends;
- provide appropriate organization export and driver personal-data access/export paths;
- record actor, time, reason and effective time.

On organization closure:
- block new operational activity;
- define an authorized export window and responsible contact;
- settle/terminate subscription entitlements;
- stop active sharing sessions;
- preserve records subject to legal retention and dispute holds;
- delete/anonymize only under an approved retention policy;
- retain minimal audit evidence where legally justified.

Ownership transfer requires explicit acceptance, confirmation of authority and a complete audit event. The last owner cannot be removed without a valid transfer or closure path.

## 6. Location-sharing integration

ADR-0015 remains authoritative for driver-phone location semantics and privacy safeguards. This ADR adds organization authorization context:

- A sharing session references the organization and, where relevant, the active assignment/task that justifies it.
- Membership alone never starts location sharing.
- Before sharing begins, the driver receives clear notice of purpose, audience, duration, update behaviour and controls.
- Sessions end at expiry, assignment end, off-duty transition, revocation, organization suspension or explicit driver stop, subject to reviewed policy and law.
- Dispatchers see only authorized drivers/locations within permitted scope and while a valid session exists.
- Group membership alone does not grant access to all location history.
- Live visibility does not imply indefinite historical access; retention is a separate minimized policy.
- Driver-phone GPS, vehicle-mounted tracker telemetry and manual reports remain distinct source types.

No covert tracking or inference of misconduct is permitted.

## 7. Client and API boundaries

### PC/web fleet management
Support organization setup, invitations, role management, groups, fleet-vehicle records, assignments, entitlement visibility, audit views and permitted live-session monitoring. The UI is not the security boundary.

### Android driver experience
Show organization context, current assignment and assigned vehicle/profile; explain organization access to data; expose visible location-sharing status and controls. Personal journeys/profiles remain distinguishable from organization-managed work.

### Application/API use cases
Conceptual operations include create/update/close organization; invite/accept/revoke membership; grant/revoke permissions; create/archive groups and manage group membership; register/update/retire fleet vehicle; create/close assignment; retrieve authorized fleet overview; start/stop sharing session; retrieve entitlements/usage.

These are not frozen endpoint paths or implemented APIs. Every command authorizes at the application boundary and enforces invariants transactionally.

## 8. Core invariants

1. A user account is not owned by an organization.
2. Every tenant-owned resource belongs to exactly one organization.
3. A group cannot grant access without active organization membership.
4. Roles/permissions never cross organization boundaries implicitly.
5. Pending, expired, suspended or revoked memberships grant no normal tenant access.
6. A personal Vehicle Profile is not automatically a Fleet Vehicle or company asset.
7. Fleet Vehicle configuration is versioned; historical references remain stable.
8. Assignments are time-bounded and auditable; history is not overwritten.
9. Assignment exclusivity is a policy, not a universal assumption.
10. Fleet membership alone never starts location sharing.
11. Dispatcher visibility is limited by organization, group, assignment and valid session scope.
12. Subscription/payment and authorization are separate decisions.
13. Client-supplied tenant IDs and roles are never trusted without server verification.
14. Offboarding/closure cannot silently erase personal identity or legally required history.
15. Missing assignment, vehicle or profile data is unknown/incomplete, never guessed.

## 9. Consequences

**Benefits**
- Separates personal identity, company tenancy and operational assignment.
- Supports owner-operators and multi-company driver relationships without duplicate accounts.
- Preserves fleet asset and technical configuration history.
- Makes authorization and audit requirements explicit before database design.
- Supports PC fleet administration and Android driver workflows.

**Costs**
- More domain concepts/lifecycle states than a single organization_id field.
- Effective-dated assignments and versioned profiles require careful transaction/query design.
- Fine-grained group/dispatcher permissions increase security-test requirements.
- Entitlements, retention and offboarding need explicit operational policies.

## 10. Alternatives considered

- **Organization ID directly on User:** rejected; prevents legitimate multi-organization membership and conflates identity with tenancy.
- **Single vehicle_id on Driver:** rejected; cannot represent relief drivers, temporary swaps, teams or history.
- **Every vehicle is a driver's profile:** rejected; company assets have distinct ownership, lifecycle and audit requirements.
- **Subscription plan equals role:** rejected; commercial entitlement and authorization are distinct.
- **GPS sharing for every fleet member:** rejected; membership alone is not a sufficient purpose or legal/operational basis.

## 11. Open questions before implementation

1. Which organization types and business-verification levels are required for the first pilot?
2. Can a driver hold concurrent memberships in competing organizations, and what contractual/data boundaries apply?
3. What group hierarchy depth/delegation is genuinely needed?
4. Which assignment types are required first: driver-vehicle, driver-group, vehicle-group or shift/task?
5. Which operational cases require multiple drivers per vehicle or multiple vehicles per driver concurrently?
6. What is authoritative for vehicle ownership, registration and technical-profile verification?
7. Which fleet fields are visible to drivers, dispatchers, safety managers and owners?
8. What is the final role/permission matrix and high-impact approval policy?
9. Which subscription provider, plans, quotas, grace periods and downgrade behaviours are justified?
10. What retention, export, deletion and legal-hold rules apply to assignments, journeys and location data in Portugal/EU?
11. What controller/processor roles and lawful bases apply to each deployment?
12. What is the minimum audit event set and who may access it?

## 12. Implementation gates

Do not begin fleet schema migrations or expose fleet administration until:
- role/permission matrix is reviewed;
- tenant isolation and RLS policies are specified and tested;
- invitation, revocation, offboarding and ownership-transfer flows are defined;
- assignment overlap rules are explicit;
- fleet asset versus personal profile ownership is agreed;
- sharing purposes, notice, session controls and retention are privacy-reviewed;
- subscription entitlements are separated from authorization;
- API contracts and failure/error states are specified.

Keep the first implementation inside the modular monolith. Do not introduce microservices or a workflow engine without demonstrated need.

## 13. Status

This ADR records a proposed domain decision only. It does not claim organizations, memberships, invitations, groups, fleet vehicles, assignments, subscriptions, tenant isolation, APIs, GPS sharing or fleet dashboards have been implemented or tested.
