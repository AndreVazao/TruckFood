# ADR-0017 — Authorization Model and Organization Permission Matrix

- **Status:** Proposed
- **Date:** 2026-11-08
- **Related:** ADR-0005, ADR-0008, ADR-0009, ADR-0011, ADR-0015, ADR-0016

## 1. Context

ADR-0011 establishes least privilege, deny-by-default authorization and persistence-level enforcement. ADR-0016 defines organizations, memberships, roles, groups, fleet vehicles and assignments. The next step is to define what each actor may do, against which scope, under which conditions.

A role name alone is not a sufficient security policy. A dispatcher in one depot must not automatically see another depot's drivers; a fleet administrator must not automatically access every historical phone-location point; a driver must not gain company-wide access because they know a resource ID.

This ADR defines a permission vocabulary, scope hierarchy, decision procedure and minimum authorization test matrix. It does not implement authorization or freeze database policies.

## 2. Decision

Adopt permission-based authorization with:
- authenticated subject identity;
- organization-scoped membership and role grants;
- explicit resource scope (organization, group, assignment, self or public);
- operation-specific permissions;
- contextual conditions (resource ownership, assignment, lifecycle, sharing session and data classification);
- server-side enforcement at every protected use case;
- persistence-level enforcement as a second boundary where supported;
- auditable decisions for sensitive operations.

Roles are bundles of permissions, not security principals. The authorization engine evaluates permissions and scope, not UI labels.

## 3. Permission vocabulary

Permission identifiers use stable, namespaced strings. The initial vocabulary is proposed below and may be split or consolidated during implementation.

### 3.1 Organization administration
- `organization.read`
- `organization.update`
- `organization.suspend`
- `organization.close`
- `organization.transfer_ownership`
- `organization.export`

### 3.2 Membership and invitations
- `membership.list`
- `membership.invite`
- `membership.read`
- `membership.update_roles`
- `membership.suspend`
- `membership.revoke`
- `membership.accept_self`
- `membership.leave_self`

### 3.3 Groups
- `group.create`
- `group.read`
- `group.update`
- `group.archive`
- `group.manage_members`

### 3.4 Fleet vehicles and technical profiles
- `fleet_vehicle.create`
- `fleet_vehicle.read`
- `fleet_vehicle.update`
- `fleet_vehicle.assign`
- `fleet_vehicle.retire`
- `vehicle_profile.read`
- `vehicle_profile.manage_company`
- `vehicle_profile.import_personal`

### 3.5 Assignments and work
- `assignment.create`
- `assignment.read`
- `assignment.update`
- `assignment.close`
- `assignment.cancel`
- `assignment.read_history`

### 3.6 Location sessions and location data
- `location_session.start_self`
- `location_session.stop_self`
- `location_session.read_scoped_live`
- `location_session.revoke_scoped`
- `location_history.read_scoped`
- `location_history.export_scoped`

### 3.7 Compliance, audit and subscription
- `compliance.read_scoped`
- `audit.read_scoped`
- `audit.export_scoped`
- `subscription.read`
- `subscription.manage`
- `entitlement.read`
- `usage.read`

### 3.8 Platform operations
Any platform-level permission (for example `platform.support_access`) is outside organization role bundles, must be separately granted, time-bounded where possible, justified, strongly audited and unavailable to ordinary tenant members.

## 4. Scope model

Authorization must evaluate both permission and resource scope.

### 4.1 Scope types

- **Self:** the authenticated user's own profile, own membership actions or own sharing controls.
- **Assigned:** a resource directly linked to the user's active assignment.
- **Group:** resources within groups explicitly granted to the actor, subject to membership and policy.
- **Organization:** tenant resources in the actor's organization, only when the permission explicitly allows organization-wide scope.
- **Public:** fields intentionally published for anonymous discovery.
- **Platform:** exceptional platform operations, never implied by an organization role.

A scope cannot be widened by a client-supplied ID. The server resolves the resource's true organization and relationships before authorization.

### 4.2 Scope inheritance

- Active organization membership is a prerequisite for all non-public tenant scopes.
- Group scope does not imply organization-wide scope.
- Assignment scope does not imply access to unrelated assignments or historical location.
- Parent-group visibility does not automatically grant access to every descendant; an explicit inheritance rule is required and must be bounded, cycle-free and tested.
- Organization-wide permissions are granted explicitly, not inferred from group hierarchy.
- A user with roles in multiple organizations must select or resolve the relevant tenant context for each operation; tenant context is never proof of access.

## 5. Initial role-to-permission matrix

The following is a conservative starting proposal. `Org` means organization-wide scope; `Group` means explicitly assigned group scope; `Assigned` means direct assignment scope; `Self` means own resource only. A blank/omitted permission is denied.

| Capability | Owner | Fleet admin | Dispatcher | Safety manager | Driver | Viewer |
|---|---|---|---|---|---|---|
| Read organization settings | Org | Org | — | — | limited | limited |
| Update organization settings | Org | Org | — | — | — | — |
| Suspend/close organization | Org | — | — | — | — | — |
| Transfer ownership | Org + step-up | — | — | — | — | — |
| List/read memberships | Org | Org | Group-limited roster | Group-limited roster | Self | limited roster |
| Invite members | Org | Org | — | — | — | — |
| Change roles/revoke members | Org | Org, excluding owner transfer | — | — | — | — |
| Manage groups | Org | Org | assigned groups only, if delegated | — | — | — |
| Read fleet vehicles | Org | Org | Group/assignment | Group/assignment | Assigned | explicitly scoped |
| Create/update/retire fleet vehicles | Org | Org | — | compliance fields only if delegated | — | — |
| Manage company vehicle profiles | Org | Org | — | compliance fields only if delegated | — | — |
| Import a personal vehicle profile | explicit consent + Org policy | explicit consent + Org policy | — | — | self-initiated consent | — |
| Create/change assignments | Org | Org | assigned groups | — | — | — |
| Read active assignments | Org | Org | assigned groups | assigned groups where needed | Self/Assigned | explicitly scoped |
| Read assignment history | Org, purpose-limited | Org, purpose-limited | assigned groups, time-limited | relevant compliance scope | own relevant history | — |
| Start/stop own location sharing | — | — | — | — | Self | — |
| View live driver-phone location | no automatic grant | no automatic grant | valid Group/Assignment session | no automatic grant | own session status | — |
| Revoke sharing session | Org only with documented authority and audit | limited, reason required | only scoped session if explicitly delegated | — | own session stop | — |
| Read historical location | no default grant; separate purpose/approval | no default grant; separate purpose/approval | no default grant | no default grant | own data subject access path | — |
| Read compliance records | Org, restricted | limited operational need | — | Group/Assignment | own relevant records | — |
| Read audit records | Org, restricted | scoped administration | — | scoped compliance | own security events where appropriate | — |
| Manage subscription | Org | — | — | — | — | — |
| Export organization data | Org + step-up + audit | only delegated, limited export | — | — | own data export path | — |

This matrix is a policy baseline, not a final grant of legal authority. Every cell must be translated into named permissions and conditions before implementation. Sensitive access must be purpose-limited and minimized even where a role could technically grant it.

## 6. Sensitive data rules

### 6.1 Location data

Live and historical location are separate permissions and data classes.

- Membership alone grants neither.
- Live access requires a valid, active, visible, purpose-bound session and authorized organization/group/assignment scope.
- The viewer must receive only the minimum fields needed (for example approximate position, accuracy, source and last update) for the authorized operational task.
- Historical access is denied by default to all ordinary roles. Any exception requires a separately defined purpose, lawful basis, retention period, permission and audit.
- Location exports are separately controlled and should be disabled until an approved operational/legal use case exists.
- A manager cannot infer misconduct from missing updates, stale coordinates, permission denial or distance from a vehicle.

### 6.2 Personal data and vehicle profiles

- A company role does not grant general access to private driver profile fields.
- Personal vehicle profiles remain driver-controlled. Import into a company fleet record requires clear, affirmative consent and must create an organization-owned copy or reference under an explicit data-use rule.
- Registration, contact, identity and compliance fields are field-classified and returned only when needed.
- Public discovery APIs must not expose fleet membership, assignments, registration identifiers or private vehicle data.

### 6.3 Audit and exports

- Sensitive reads (especially location history, personal data and compliance records) should be auditable, not only writes.
- Audit events record actor, organization, action, target, outcome, timestamp, reason/context where appropriate and correlation ID; avoid duplicating raw sensitive payloads.
- Audit access is itself permission-controlled and audited.
- Exports require explicit scope, purpose, authorization, step-up authentication where appropriate, expiry and download audit.
- Bulk exports must not bypass per-resource scope.

## 7. Authorization decision procedure

Every protected operation follows this order:

1. Authenticate the caller and establish a trusted subject ID.
2. Resolve the target resource from server-side persistence; do not trust client-supplied tenant ownership.
3. Resolve the resource's organization and relevant group/assignment relationships.
4. Confirm organization and membership lifecycle permit the operation.
5. Resolve active role grants and effective permissions at the current instant.
6. Check the requested permission for the required scope.
7. Evaluate contextual conditions: ownership, assignment validity, resource state, data classification, sharing-session state, purpose and any step-up requirement.
8. Apply field-level filtering/minimization to the returned representation.
9. Execute the operation transactionally where invariants can race (membership revocation, assignment overlap, role changes, ownership transfer).
10. Record required audit event and return a stable API outcome.

Authorization failures must not disclose whether an inaccessible cross-tenant resource exists. Use a consistent not-found/forbidden policy appropriate to the endpoint and threat model.

## 8. Revocation, sessions and offline clients

- Role and membership changes must be reflected promptly; long-lived client claims cannot remain authoritative.
- Access tokens/session claims are not the sole source of current permissions for sensitive operations.
- Revocation of membership, role grants, organization status or sharing authorization invalidates relevant active sessions or causes immediate server-side re-evaluation.
- Offline clients may access only explicitly approved cached data within its retention/expiry window. Offline access must not enable new privileged operations.
- On reconnect, revalidate account, tenant membership, entitlements and resource authorization before synchronization.
- Logout/account switching clears or cryptographically isolates tenant-private local data. A user switching between organizations must never see another tenant's cached records.
- Cached location and sensitive personal data require shorter retention and stronger protection than public map tiles.

## 9. API and persistence enforcement

- Application use cases enforce permission checks even if the UI hides an action.
- Persistence policies provide defense in depth. If Supabase is selected, RLS must enforce tenant and owner boundaries for exposed tables; privileged service-role operations must be narrowly controlled server-side.
- RLS policies must not rely on untrusted client metadata for organization membership or role grants.
- Background jobs, scheduled tasks, webhook handlers, search indexes, storage objects, exports and analytics pipelines must apply equivalent tenant and permission boundaries.
- Storage access (photos, documents, exports) must authorize the object and its parent resource, not merely possession of a URL.
- Provider integrations receive only the minimum required data and must not receive internal authorization tokens or unrelated personal fields.
- Error responses follow ADR-0009 and do not leak tenant/resource existence.

## 10. Minimum security test matrix

Before any fleet feature is exposed, automated tests must cover at least:

1. Anonymous caller cannot read private tenant resources.
2. User A cannot read/update User B's private profile, journey or personal vehicle profile.
3. Member of Organization A cannot access Organization B by guessing IDs or altering request tenant IDs.
4. Pending/expired/revoked/suspended membership grants no normal access.
5. Membership in one organization grants no role in another.
6. Group-scoped dispatcher cannot access sibling/unassigned groups.
7. Group membership does not grant organization-wide administration.
8. Driver can read only own membership, assignment and assigned vehicle data.
9. Driver cannot change another driver's assignment or vehicle.
10. Dispatcher cannot see live location without a valid sharing session and matching scope.
11. No ordinary role can read historical location by default.
12. Revocation takes effect for existing sessions and subsequent requests.
13. Parent-group changes cannot create unintended inherited access or cycles.
14. Cross-tenant exports, object storage URLs and background jobs are denied.
15. Organization suspension/closure blocks new operational mutations and sessions.
16. Subscription downgrade changes entitlements without granting unauthorized access or deleting records.
17. Concurrent assignment/role changes preserve invariants transactionally.
18. Audit logs capture privileged reads/writes without storing unnecessary sensitive payloads.
19. Offline cache cannot be used to perform privileged mutations or leak data after account/tenant switching.
20. Platform support access is unavailable to ordinary organization roles and is fully audited.

Tests must include direct API/database access paths, not only UI workflows. Use synthetic fixtures and deterministic CI tests; do not require paid provider credentials.

## 11. Open questions

1. Which matrix cells require dual approval or step-up authentication?
2. Can fleet administrators see full membership rosters, or only operationally relevant fields?
3. Which group hierarchy inheritance model, if any, is needed for the first release?
4. What minimum live-location precision/update rate is operationally justified?
5. Which rare use cases, if any, justify historical location access, and under what legal basis and retention?
6. Which safety/compliance fields require a dedicated reviewer role or separation of duties?
7. Which exports are required for the first release, and who may approve them?
8. What is the exact policy for owner removal, emergency access and support access?
9. Which permissions are available in each commercial plan, without making subscription status a substitute for authorization?
10. What privacy, employment-law and data-protection review is required for each Portuguese/EU fleet deployment?

## 12. Implementation gates

Do not implement fleet RLS policies, expose fleet APIs or launch location visibility until:
- the role/permission matrix is approved by product and privacy/legal review;
- each permission has an explicit scope and resource/data classification;
- tenant ownership and group/assignment relationships are represented in the schema;
- membership/role revocation behaviour is defined and tested;
- sensitive location access and retention are approved;
- storage, background jobs, exports and offline caches have equivalent authorization rules;
- the minimum security test matrix runs in CI and passes;
- privileged support and emergency access are separately governed.

## 13. Status

This ADR is a proposed authorization specification. It does not claim that roles, permissions, policies, RLS, API guards, audit pipelines, location controls or security tests have been implemented or validated.
