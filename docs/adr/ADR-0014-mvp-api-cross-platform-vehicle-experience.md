# ADR-0014 — MVP API Contracts, Cross-Platform Experience and Vehicle Selection

- **Status:** Proposed
- **Date:** 2026-10-30
- **Decision owners:** TruckFood project
- **Scope:** MVP API semantics, responsive clients, Android/device compatibility, PC access, driver onboarding and vehicle selection
- **Depends on:** ADR-0003 (vehicle model), ADR-0008 (architecture boundaries), ADR-0009 (API boundaries), ADR-0010 (offline packages), ADR-0011 (security/privacy), ADR-0012 (geospatial strategy), ADR-0013 (provider contracts)

## 1. Context

TruckFood must be useful across a heterogeneous device landscape: Android phones from different manufacturers and generations, different screen sizes and capabilities, tablets and PCs. The product must not assume one phone model, one Android version, touch-only input, a permanent network connection or high-performance hardware.

Vehicle context is equally central. A Jeep, passenger car, rigid truck, tractor unit with semi-trailer, road train/multiple-trailer combination or special/oversized load have materially different dimensions, masses, axle configurations, access rules and operational constraints. A generic "truck" switch or one default set of dimensions is not sufficient for reliable evaluation.

The API and UX must make the selected vehicle context explicit and preserve it consistently across search, route evaluation, parking/access suitability and offline use.

## 2. Decision

Adopt the following direction:

1. Define versioned, TruckFood-owned, use-case-oriented API contracts before binding the product to a client framework or provider.
2. Treat responsive multi-platform access as a product requirement: Android phones, Android tablets and PC/web must share the same domain semantics and account data.
3. Use progressive enhancement: core discovery and vehicle selection must remain usable on modest devices and constrained networks; richer features must not be prerequisites for basic use.
4. Make a structured Vehicle Profile a first-class user-owned entity. Every vehicle-sensitive operation must reference an explicit active profile or clearly state that vehicle context is absent.
5. Support multiple saved profiles and vehicle configurations, with the driver selecting the correct profile for each journey. Never infer that the last-used profile is always appropriate.
6. Distinguish vehicle category/mode from the actual physical configuration and measured/legal attributes. Category is a starting point, not a substitute for dimensions and weights.
7. Do not claim access suitability or truck-safe routing when required vehicle attributes or provider capabilities are missing, unsupported, stale or contradictory.

This ADR establishes product and API direction. It does not claim clients, APIs, vehicle calculations or compatibility tests have been implemented.

## 3. Cross-platform product requirements

### 3.1 Supported experience classes

The product should be designed and tested for:
- Android phones across supported OS versions, screen sizes, aspect ratios, memory and processor capabilities.
- Android tablets and larger touch displays.
- PC/web browsers, including keyboard and mouse operation and resizable windows.
- Future form factors only when they can use the same documented API and domain contracts.

The exact minimum Android version, browser support matrix and hardware floor must be chosen from measured user/device research and the selected technology stack. Do not invent a support promise before testing.

### 3.2 Responsive and adaptive behaviour

- Use responsive layouts rather than fixed device-specific dimensions.
- Support portrait and landscape where the use case benefits; do not assume one orientation.
- Adapt navigation, map panels, forms, tables and dialogs to available width and input method.
- On small screens, keep primary actions reachable and avoid dense multi-column forms.
- On PC, take advantage of larger displays without creating a separate product or divergent business rules.
- Support touch targets, keyboard navigation, visible focus, readable text scaling and accessible contrast.
- Respect system font/display scaling and avoid clipping when users enlarge text.
- Handle safe areas, cut-outs, status/navigation bars, system gestures and varying screen densities.
- Do not depend on a specific OEM skin, proprietary Android service or device-only API for core functionality.

### 3.3 Performance and constrained devices

- Set performance budgets after profiling representative low-, mid- and high-tier devices.
- Lazy-load nonessential screens and media; paginate large lists and bound map queries.
- Avoid keeping multiple high-resolution map layers or large datasets in memory unnecessarily.
- Provide clear loading, retry and degraded-mode states.
- Do not block basic discovery because optional analytics, animation or a secondary provider is unavailable.
- Make offline package size and required free storage visible before download.
- Test app lifecycle events, background/resume, process termination and interrupted downloads on real devices.

### 3.4 Connectivity and offline

- Distinguish online, offline, reconnecting and partially connected states.
- Preserve safe read-only access to downloaded public data when offline, within its coverage and freshness limits.
- Queue eligible user actions only when their semantics and conflict handling are defined; never present a queued submission as published or verified.
- On reconnection, re-authorize and synchronize according to ADR-0011.
- Explain which functions require a network connection, including live traffic, fresh provider routing and newly published restrictions.
- Offline map availability must not imply offline route calculation or complete restriction coverage.

## 4. Vehicle selection and profile experience

### 4.1 Vehicle mode versus physical profile

The initial selection may offer understandable categories such as:
- Passenger car / 4x4 (including Jeep-type vehicles)
- Light commercial vehicle / van
- Rigid truck
- Tractor unit with semi-trailer
- Truck with multiple trailers / road-train configuration, where legally applicable
- Bus or coach, if included in product scope
- Special / oversized / abnormal load

These are UX starting points, not exhaustive legal classifications. The product must not assume that every country uses the same category names or legal limits.

Selecting a category may preconfigure relevant fields, but it must never silently invent or certify the actual vehicle dimensions, weights, axle loads, trailer arrangement or legal permissions. The driver must review and confirm the profile.

### 4.2 Multiple saved profiles

A driver may create and maintain multiple profiles, for example a personal 4x4, a rigid delivery truck and a tractor unit with a particular trailer combination.

Each profile must have:
- stable TruckFood profile ID and owner;
- user-defined name/label;
- vehicle category and configuration;
- dimensions and weight values with units;
- axle and trailer details relevant to the configuration;
- optional ADR/hazardous-material attributes where relevant;
- data completeness/verification state and last-confirmed date;
- created/updated timestamps and profile status.

The active profile is selected for a journey. Changing the active profile must be visible and must update subsequent vehicle-sensitive evaluations. Past journeys must retain the profile snapshot or version used at the time; editing a saved profile must not silently rewrite historical journey context.

### 4.3 Physical attributes

The model and UI must support, as applicable:
- overall vehicle/combination length;
- overall width;
- overall height, including relevant load or equipment;
- gross vehicle/combination mass;
- axle count and axle configuration;
- individual axle or axle-group loads where available/required;
- trailer count and trailer type/configuration;
- tractor and trailer relationship;
- articulation/combination configuration;
- load-related dimensions or overhang when operationally relevant;
- vehicle class and access category;
- ADR/hazardous-material class, UN number or other regulated attributes only when applicable and supported;
- country/jurisdiction and relevant permit/authorization context for special loads.

Do not collapse gross mass into axle load. Do not assume the tractor unit's dimensions represent the full combination. For multi-trailer or special-load configurations, the profile must represent the complete combination and relevant permits/conditions, not only the towing vehicle.

The precise field set and legal terminology must be validated against target jurisdictions before implementation.

### 4.4 Units, validation and completeness

- Store normalized values using a consistent internal unit convention; expose explicit units in API contracts and UI.
- Accept familiar user units where appropriate, convert visibly and avoid ambiguous unit entry.
- Validate plausible ranges and cross-field consistency, but do not treat plausible values as legally verified.
- Distinguish unknown, not provided, not applicable and verified values.
- Never replace missing safety-critical dimensions with a generic default.
- Show a completeness summary and explain which features are limited by missing fields.
- Permit a profile suitable for ordinary discovery while clearly preventing unsupported vehicle-sensitive conclusions.

### 4.5 Journey selection safeguards

Before a vehicle-sensitive route or access evaluation:
1. Show the selected vehicle profile name and configuration.
2. Allow the driver to switch profiles or review/edit details.
3. Identify missing or unconfirmed critical attributes.
4. Check whether the routing/restriction source supports the required vehicle parameters in the requested region.
5. Return a clear outcome: evaluated with stated coverage, partially evaluated, unsupported, insufficient data or unavailable.
6. Preserve the profile ID/version or a suitable immutable snapshot with the journey evaluation.

The interface must not silently carry a passenger-car profile into a truck journey, or a single-trailer profile into a multi-trailer journey.

## 5. Vehicle-aware domain and API semantics

Every vehicle-sensitive request must carry an explicit vehicle_profile_id or an explicit, documented vehicle_context_status explaining why no profile is used. The server must load and authorize the profile; it must not trust client-submitted owner IDs or dimensions as authoritative profile data.

For reproducibility, evaluation responses and journey records should identify:
- selected profile ID and profile version/snapshot;
- attributes actually applied;
- required attributes missing or unconfirmed;
- provider capability coverage for those attributes;
- restrictions/data sources and freshness context;
- limitations and warnings;
- evaluation timestamp and outcome state.

One profile may be used for a journey, but a journey's historical evaluation must remain tied to the version actually used.

## 6. MVP API surface

The first API specification should define versioned use cases, not expose database tables directly. Candidate operations:

### Identity and driver
- retrieve/update own driver preferences and display settings;
- retrieve own account context and supported client capabilities.

### Vehicle profiles
- list own vehicle profiles;
- create, retrieve, update and archive own profiles;
- select a profile for a journey;
- retrieve profile completeness and validation results.

### Locations and services
- search published Locations using bounded geographic filters and capability/service filters;
- retrieve a Location and its published capabilities, entrances and evidence summary;
- retrieve suitability information with explicit vehicle context where supported.

### Journey and evaluation
- create/update a private journey;
- select the active vehicle profile;
- request route candidates through supported adapters;
- evaluate known restrictions/access evidence against the selected profile;
- retrieve evaluation warnings, coverage and provenance.

### Offline packages
- list available packages and metadata;
- request/download/update/delete eligible packages;
- retrieve package manifest, coverage, data families, attribution and freshness.

### Community
- submit an observation/report with source time and location precision;
- retrieve the authenticated user's submission status;
- moderation operations remain privileged and separately authorized.

Exact HTTP paths, payload schemas and OpenAPI representation remain to be specified in the implementation RFC. Do not expose raw persistence models as public API.

## 7. API outcome and error semantics

At minimum preserve distinct outcomes:
- success
- partial
- empty
- unsupported
- insufficient_data
- unknown
- stale
- conflicting
- unavailable
- rate_limited
- invalid_response

Stable error categories should include validation, authentication, authorization, not found, conflict, unsupported capability, provider timeout/unavailable, quota exceeded, licensing denied and internal failure.

A successful HTTP response must not imply a positive safety/suitability decision. The business outcome and transport status are separate concepts. Responses must include safe messages, stable machine codes, correlation IDs and field-level validation where relevant, without leaking secrets or infrastructure details.

## 8. Compatibility and client capability negotiation

- API versioning must be independent of Android OS version and client release version.
- Clients should send app/client version and supported capability identifiers where useful, but the server remains authoritative for permissions and data.
- Prefer additive API evolution and explicit deprecation windows.
- Older clients must receive a compatible response or a clear minimum-version requirement; do not silently misinterpret new vehicle fields.
- Use feature detection/capability negotiation rather than assuming every device supports every feature.
- Device-specific optimizations must remain optional and must not change domain results.
- Define a migration strategy for local databases and offline package formats.

## 9. Accessibility, language and usability

- Design for one-handed operation during safe stationary use; do not encourage interaction while driving.
- Use plain language for vehicle categories, dimensions and warnings, with technical detail available when needed.
- Provide localized labels, units and validation messages; keep canonical API values language-neutral.
- Support text scaling, screen readers, keyboard navigation and sufficient contrast.
- Avoid color-only safety signals; pair status with text and/or icons.
- Make critical vehicle mismatch and insufficient-data warnings explicit and understandable.

## 10. Privacy and security

Vehicle profiles and journeys are private user-owned data under ADR-0011. The server must authorize every read/write. Public location discovery must not expose a user's vehicle or journey context. Offline private profile storage must follow local cache/logout/account-switch rules. A client cannot elevate permissions by changing profile IDs, role fields or request payloads.

## 11. Validation and test matrix

Before claiming platform support, test representative combinations of:
- Android OS versions selected for the support policy;
- different manufacturers/OEM skins;
- small and large phones, varied aspect ratios and display densities;
- Android tablets;
- low-, mid- and high-memory/performance devices;
- portrait/landscape and large text scaling;
- touch-only and accessibility input;
- PC browsers and keyboard/mouse;
- poor, intermittent and absent connectivity;
- app background/resume, process kill and interrupted download;
- old client against newer API and migration between offline package versions.

Vehicle tests must include at least:
- Jeep/4x4 or passenger car;
- light van;
- rigid truck;
- tractor unit with semi-trailer;
- multi-trailer combination;
- special/oversized load with conditional permits;
- missing, unconfirmed and conflicting dimensions;
- different axle loads despite similar gross mass;
- ADR applicable and not applicable;
- region/provider combinations where specific parameters are unsupported.

Tests must verify not only form display but correct profile persistence, selection, API payload, evaluation inputs, warnings and historical journey reproducibility.

## 12. Consequences

### Positive
- One coherent product experience across phone, tablet and PC.
- Avoids device-specific assumptions and makes compatibility measurable.
- Treats vehicle selection as a safety-critical journey input rather than a cosmetic preference.
- Supports multiple vehicles and complex combinations without reducing all drivers to one generic truck profile.
- Makes missing data and provider capability gaps visible.
- Preserves historical journey evaluation context.

### Trade-offs
- More deliberate onboarding and profile validation are required.
- Responsive and compatibility testing increases QA scope.
- Complex vehicle combinations require careful domain design and jurisdiction-specific validation.
- Older devices may need reduced map/media capabilities.
- Exact supported Android/browser versions cannot be promised until stack and testing evidence exist.

## 13. Open questions

- Select client technology/architecture and minimum supported Android/browser versions based on evidence.
- Decide whether PC experience is responsive web, installable PWA or another client, while preserving shared API/domain contracts.
- Confirm whether bus/coach and additional specialist categories belong in the first release.
- Finalize jurisdiction-aware vehicle classifications and legal field definitions.
- Define which vehicle attributes are mandatory for each evaluation type.
- Define immutable profile snapshot strategy for journey history.
- Set performance budgets and representative device test inventory.
- Define offline storage limits and package compatibility policy.

## 14. Implementation gate

Do not freeze the client framework, claim broad device compatibility, implement vehicle-sensitive route claims or create final vehicle database migrations until the device support matrix, vehicle field definitions, journey profile-selection flow, API contracts and representative tests are reviewed. This ADR defines direction and acceptance criteria; it does not claim a cross-platform application or vehicle engine has been implemented.
