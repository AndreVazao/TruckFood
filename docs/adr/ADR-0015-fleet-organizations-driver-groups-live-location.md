# ADR-0015 — Fleet Organizations, Driver Groups and Consent-Based Live Location

- **Status:** Proposed
- **Date:** 2026-10-30
- **Scope:** Future business subscriptions, fleet administration, driver groups, mobile location sharing and PC fleet dashboard
- **Depends on:** ADR-0005, ADR-0008, ADR-0009, ADR-0011 and ADR-0014

## 1. Context

TruckFood may serve individual drivers and business customers. A transport company may subscribe to a fleet plan, create an organization with groups and vehicles, invite drivers using their own phones and view participating drivers' live shared positions from a PC dashboard.

Phone GPS provides a complementary operational signal without requiring a dedicated tracker in every truck. However, a phone reports the location of the phone and its user, not necessarily the truck. It cannot prove that the driver is inside, beside or still with the vehicle. Phone location and fixed vehicle-tracker telemetry are different sources and must never be represented as equivalent.

Live location is highly sensitive personal data. Fleet functionality must be designed around a clear purpose, transparency, lawful basis, proportionality, access controls and limited retention. It must not become covert employee surveillance or imply that a driver abandoned a vehicle based only on distance between phone and truck.

## 2. Decision

Prepare a future multi-tenant fleet capability with:

1. Business organizations and paid fleet plans, separate from individual consumer accounts.
2. Organization administrators who can create groups, invite/manage drivers and associate drivers with company vehicles and journeys, subject to authorization.
3. Driver access through the normal TruckFood mobile app on the driver's own compatible phone; no dedicated GPS hardware is required for phone-based sharing.
4. Explicit, visible, purpose-bound live-location sessions, normally associated with an assigned shift or journey and activated only under an approved lawful and product policy.
5. A PC/web fleet dashboard for authorized managers to see current shared positions, last update time, status and operational context.
6. A strict distinction between driver-phone location, vehicle-mounted tracker telemetry and manually reported vehicle location.
7. Privacy, safety, legal compliance, security and employee rights as release gates.

This ADR records future requirements. It does not implement subscriptions, tracking, background GPS or dashboard screens.

## 3. Organization and tenancy model

Future domain concepts:

- **Organization / Fleet Tenant:** business customer and billing/security boundary.
- **Organization Membership:** user-to-organization relationship with explicit status and role.
- **Fleet Group:** depot, region, team, shift or operational unit.
- **Driver Assignment:** time-bounded relationship between driver, group, journey and/or vehicle.
- **Fleet Vehicle:** organization-managed vehicle, linked to a reusable TruckFood Vehicle Profile where appropriate.
- **Fleet Plan / Entitlement:** subscription tier, licensed capacity and feature entitlements.
- **Location Sharing Session:** time-bounded, auditable session for sharing a driver's phone location for a stated purpose.
- **Location Observation:** timestamped observation with source type, accuracy, freshness and provenance.
- **Fleet Event:** assignment, session start/end, stale signal or driver-reported status.

A user may belong to more than one organization where policy allows. The driver retains an individual account and personal vehicle profiles; organization membership does not transfer ownership of the personal account. Organization assignments and company-owned vehicle records remain tenant-scoped.

Every tenant-owned object must carry an enforceable organization boundary. Cross-tenant access is denied by default and tested at API and persistence levels. Organization administrators must not gain access to unrelated personal journeys or data merely because a driver joined a fleet.

## 4. Roles and permissions

Initial role concepts:

- **Fleet Owner / Billing Admin:** subscription, billing and organization lifecycle.
- **Fleet Administrator:** membership, groups, fleet vehicles and policy configuration.
- **Dispatcher / Fleet Manager:** access only to assigned groups, drivers, vehicles and operational views.
- **Driver:** own profile, assignments, sharing-session visibility and controls, subject to clearly disclosed organization policy.
- **Auditor / Compliance role:** narrowly scoped access to required audit and compliance records.

Permissions must be separate for live positions, historical traces, personal profile data, vehicle data and exports. Roles must be scope-aware, not a single unrestricted company-admin flag. Privileged actions require audit records. Role changes and membership removal must take effect promptly, including for active sessions and cached clients.

## 5. Driver phone and location semantics

### 5.1 Phone location is driver/device location

The mobile app may obtain location from the phone's supported location services, subject to OS permissions, user settings, device capability, battery and network conditions.

Every observation must identify its source, for example:
- driver_phone_gps;
- vehicle_tracker (only when integrated with a genuine vehicle device/provider);
- manual_driver_report;
- another explicitly identified source.

A phone GPS observation must never be labelled as a verified truck position. The UI should say "driver phone location" or equivalent. An assigned vehicle may be shown as operational context, but not as physically confirmed at the phone coordinates.

### 5.2 Visible, bounded sharing sessions

Location sharing must be:
- clearly explained before activation;
- visibly indicated in the driver app while active;
- associated with a stated purpose, such as an assigned work shift or journey;
- limited to the relevant time window and authorized organization/group;
- governed by a clear pause/stop policy reviewed for the applicable employment context;
- automatically ended at the defined session/shift boundary or when assignment ends, with explicit handling for exceptional cases;
- resilient to app closure, OS permission changes, connectivity loss and device restart without falsely showing a live position.

Do not hide tracking indicators, bypass OS permission controls or continue tracking after a session is no longer authorized. Background location permission, if technically required on a particular Android version, must be requested transparently and only after privacy/legal policy approval. No device-specific permission workaround may be used.

### 5.3 Signal quality and stale status

Each observation should preserve:
- coordinates and coordinate reference;
- observation timestamp and server receipt timestamp;
- reported horizontal accuracy where available;
- source/device/session identifiers with privacy safeguards;
- permission/session state;
- freshness and quality classification;
- relevant failure or degraded-state reason.

The dashboard must distinguish current, delayed, stale, unavailable, permission-disabled and offline states. It must show last-update time and accuracy context where useful. It must never present a driver's last coordinate as if it were live.

GPS accuracy varies. The system must not claim exact location or continuous availability. Battery optimization, background restrictions, network loss and manufacturer-specific Android behaviour can interrupt updates; these limitations must be visible and tested.

## 6. Driver-to-vehicle proximity and abandonment safeguards

Phone location may support an approximate proximity indicator only when there is a trustworthy, current vehicle reference position from a separate source or a clearly defined operational event. Proximity is not proof of physical presence, absence, abandonment, theft or misconduct.

The product must not automatically accuse, discipline, score or penalize a driver based solely on:
- distance between a phone and a vehicle's last known position;
- a stale or low-accuracy phone observation;
- missing GPS updates;
- app termination, battery loss or permission denial;
- an inferred stop or movement pattern.

If a future workflow includes a "driver may be away from assigned vehicle" operational alert, it must be labelled unverified, based on sufficiently fresh observations from separately identified sources, access-restricted, designed for human verification and subject to legal/privacy review. It must never be treated as proof of abandonment or wrongdoing.

A phone-only system cannot establish whether the driver is physically near the truck unless additional reliable evidence exists. A fixed tracker, BLE device or other proximity technology requires its own integration, threat model and validation; none is assumed here.

## 7. Fleet dashboard on PC/web

The future PC dashboard should support:
- organization and group selection;
- map view of currently shared driver-phone positions;
- separate symbols/labels for phone GPS and genuine vehicle-tracker positions;
- driver, assigned vehicle, group and active journey context where authorized;
- last update, signal freshness and accuracy state;
- filters for active, stale, offline and not-sharing sessions;
- group/vehicle/driver detail panels;
- assignment and shift overview;
- access-controlled event history and audit trail;
- exports only for defined business purposes and authorized roles.

The dashboard must not default to exposing every driver's full historical route. Historical trace access is a separate, narrowly permissioned feature with purpose, retention and audit controls. Map clustering and bounded queries should protect performance for large fleets.

The dashboard is a responsive PC/web experience using the same TruckFood API and domain rules as the mobile app; it must not become a separate source of truth.

## 8. Cross-device and Android compatibility

The fleet mobile client must work across the supported Android device/OS matrix established under ADR-0014. Background location behaviour differs by Android version, manufacturer, battery policy, permissions and user settings.

Requirements:
- define minimum supported OS versions from evidence, not assumption;
- test foreground and background operation on representative OEM devices;
- explain required location permissions and system settings;
- degrade honestly when background updates are restricted;
- show last update rather than pretending tracking is continuous;
- minimize battery and data consumption with configurable, policy-bounded update intervals;
- do not require a specific phone brand or model;
- support secure session revocation when a driver changes or loses a device.

The PC dashboard must work in supported desktop browsers. PC is the primary initial management experience.

## 9. Location data lifecycle and privacy

Before launch, the organization must document and communicate:
- the specific purpose(s) for collecting live location;
- the lawful basis and controller/processor responsibilities;
- which roles can see current and historical data;
- when collection starts and stops;
- retention periods and deletion/anonymization rules;
- whether data is used for dispatch, safety, proof of service or another purpose;
- whether automated decisions or employee performance assessments occur;
- contact and rights-request procedures.

Do not assume employee consent alone is a valid lawful basis in an employment relationship. The lawful basis, necessity, proportionality, transparency, consultation obligations and any data-protection impact assessment must be reviewed by qualified privacy/legal professionals for each target jurisdiction. GDPR and applicable national employment/privacy law must be considered before implementation and commercial release.

Data minimization defaults:
- collect only while an authorized sharing session is active;
- do not collect location for a driver who is off duty or not assigned to a covered session;
- avoid continuous historical trace retention by default;
- retain only the minimum detail and period justified by a documented purpose;
- separate live operational visibility from optional historical reporting;
- support correction, access, export and deletion workflows as legally applicable;
- secure backups and define deletion propagation;
- never sell or repurpose precise driver-location data for unrelated advertising or profiling.

The exact retention schedule must be determined by documented business need and legal review.

## 10. Security and abuse prevention

- Authenticate every mobile and dashboard request.
- Enforce tenant, group, assignment and role scopes server-side.
- Never trust organization IDs, driver IDs, vehicle IDs or role claims supplied by a client without authorization checks.
- Use revocable session credentials and device/session management.
- Encrypt data in transit and protect stored location data and backups.
- Restrict live-location endpoints and exports; rate-limit and monitor unusual access.
- Audit administrative access, exports, membership changes, policy changes and access to historical traces.
- Prevent cross-tenant queries and insecure direct-object references.
- Do not expose precise coordinates in public endpoints, analytics logs or ordinary diagnostics.
- Define incident response for compromised manager accounts, unauthorized tracking and location-data exposure.

## 11. API and event contract direction

Future use-case contracts may include:
- create/invite organization membership;
- create/manage fleet groups;
- register/manage organization fleet vehicles;
- assign/unassign drivers and vehicles;
- start/end an authorized location-sharing session;
- submit a location observation;
- retrieve authorized live group positions;
- retrieve a driver's current sharing state and last-seen metadata;
- retrieve limited, authorized fleet events;
- revoke device/session access.

Every location event must include source identity, observation time, receipt time, accuracy/freshness and session/tenant scope. Ingestion must tolerate delayed, duplicated and out-of-order observations without rewriting history incorrectly.

Live updates may later use polling, server-sent events, WebSockets or another transport selected by measured scale and hosting constraints. The transport choice must not alter authorization, privacy or source semantics. Do not introduce expensive real-time infrastructure before measuring fleet size, update frequency and latency requirements.

## 12. Commercial model direction

A future business plan may be priced by organization, licensed driver seats, active fleet capacity or a combination. Plan entitlements may include:
- number of drivers/members;
- number of fleet groups and vehicles;
- live-location update policy/frequency;
- dashboard and dispatch capabilities;
- retention/reporting features;
- support and administrative controls.

Pricing and quotas must account for location-ingestion volume, storage, real-time fan-out, map rendering, notifications and support costs. Do not promise unlimited tracking or unlimited history. Individual TruckFood use must remain distinct from fleet subscription entitlements; a company subscription must not silently grant access to unrelated consumer features or personal data.

## 13. Validation and release gates

Before any fleet pilot:
1. Complete privacy/legal review for each target jurisdiction, including employment context and any required impact assessment or consultation.
2. Define controller/processor responsibilities and organization contract terms.
3. Define session lifecycle, driver notice and permission UX.
4. Test Android foreground/background behaviour across representative OEM/OS combinations.
5. Test inaccurate, stale, duplicated, delayed and missing location observations.
6. Verify tenant/group/role isolation with automated security tests.
7. Verify off-duty cessation, session expiry, logout, device replacement and permission revocation.
8. Validate dashboard freshness labels and phone-versus-vehicle source distinction.
9. Measure battery, data, storage, API and real-time infrastructure costs at realistic fleet sizes.
10. Run a limited opt-in pilot with transparent policy, feedback and incident handling before general release.

## 14. Consequences

### Positive
- Creates a future B2B revenue path and fleet-management product tier.
- Allows phone-based operational visibility without requiring a fixed tracker in every vehicle.
- Reuses the cross-platform architecture: driver mobile app and manager PC dashboard.
- Makes fleet, group, assignment and location data explicit domain concepts.
- Keeps driver-phone location distinct from actual vehicle telemetry.
- Builds privacy, employee rights, security and cost controls into the design from the beginning.

### Trade-offs
- Background GPS is technically variable across Android devices and cannot be guaranteed continuously.
- Location data introduces significant privacy, employment-law and security obligations.
- Real-time dashboards and frequent updates create infrastructure and support costs.
- A phone-only signal cannot verify that a driver is with the vehicle.
- Multi-tenant roles, assignments and auditing increase implementation complexity.

## 15. Open questions

- Define fleet subscription packaging, billing unit and trial/pilot model.
- Define organization invitation and driver membership lifecycle.
- Define shift/assignment model and how sharing sessions are activated.
- Determine pause/stop policy and how applicable employment policy governs it.
- Set update intervals and freshness thresholds based on dispatch needs, battery and cost.
- Define retention periods and historical reporting requirements after legal review.
- Decide which fleet features belong in the first paid tier versus later tiers.
- Evaluate optional third-party vehicle-tracker integrations without conflating them with phone GPS.
- Define fleet-size targets and real-time latency objectives.
- Confirm applicable Portuguese/EU privacy, employment and consultation requirements with qualified counsel.

## 16. Implementation gate

Do not implement covert or always-on employee tracking, infer misconduct/abandonment from phone proximity, expose historical traces by default, or launch fleet tracking commercially until the privacy/legal basis, driver transparency, tenant authorization, session controls, retention policy, Android behaviour and operational costs have been validated. This ADR prepares the future capability; it does not claim fleet tracking or subscriptions are implemented.
