# TruckFood — Provider Contracts v1

**Status:** Proposed language-neutral contract; no provider adapter is implemented.  
**Contract version:** 1.0.0  
**Source decision:** ADR-0013

## 1. Purpose and boundary

This specification defines two machine-readable records shared by TruckFood provider adapters:

1. A **capability declaration**, describing what a particular adapter can actually do, in which regions, with which vehicle parameters, under what data rights and cost constraints.
2. An **operation result**, describing the outcome of one bounded adapter call with normalized data, provenance, coverage, limitations, retry guidance and safe diagnostics.

The JSON Schema at `provider-contract-v1.schema.json` is the normative structural contract. The fixtures under `examples/` are deterministic validation examples only. They do not represent live provider access, verified coverage, licensing approval or production configuration.

## 2. Capability declaration

Every adapter declaration identifies:

- Contract, adapter and provider product versions.
- One independent capability family: `map_display`, `geocoding`, `routing`, `restriction_data`, `poi_business` or `truckfood_owned_data`.
- Supported, limited, unsupported or unknown operations.
- Geographic coverage, country/region boundaries and known gaps.
- Actual vehicle parameters accepted, including dimensions, gross mass, axle loads, trailer configuration, ADR/hazmat and conditional access.
- Time-dependent support, output features, freshness and source timestamp availability.
- Separate rights for display, transient processing, short-lived caching, persistent storage, transformation, derived analytics, redistribution and offline packages.
- Attribution, cost/metering and reliability characteristics.

A declaration is scoped to an adapter/product version and must be reviewed when terms, product versions, geography, quotas or capabilities change. A generic statement such as “truck supported” is not sufficient evidence of support for every truck parameter or region.

### Unknown versus unsupported

- `supported`: the adapter has verified support for the operation/parameter in the declared scope.
- `limited`: support exists with explicit constraints or omissions.
- `unsupported`: the adapter has determined it cannot provide the capability.
- `unknown`: evidence is insufficient to classify support.

Unknown must never be converted into supported or unsupported by inference. A missing vehicle parameter must not be treated as if the provider applied it.

## 3. Data rights are independent

Each use is classified separately as `allowed`, `conditional`, `prohibited` or `unknown`. The declaration also records an overall review state:

- `reviewed`: the applicable source terms have been reviewed for the recorded scope and date.
- `review_required`: rights are unresolved; persistent storage, redistribution and offline packaging remain blocked.
- `blocked`: the proposed use is not approved.
- `expired`: the recorded review/permission is no longer valid.

The schema is an engineering control, not legal advice. It does not replace current contract review. Display permission does not imply caching, persistence, transformation, redistribution or offline rights.

## 4. Normalized operation result

Every operation result carries:

- Contract version, operation, provider and adapter identity.
- Outcome: `success`, `partial`, `empty`, `unsupported`, `unavailable`, `rate_limited` or `invalid_response`.
- Normalized data when applicable.
- One or more provenance records and relevant timestamps.
- Coverage and limitations.
- Applicable data-rights classification.
- Retry guidance, request correlation, duration and optional cost units.
- Stable provider error category/code when the operation fails.

These outcomes are deliberately distinct. In particular:

- `empty` means the provider successfully processed the request and found no matching records.
- `unsupported` means the operation is not available from this adapter.
- `unavailable` means the provider could not currently serve the request.
- `partial` means some result data is present but known gaps/limitations remain.
- `invalid_response` means the external response could not be safely normalized.

A provider failure must never be converted into an apparently successful empty array. A partial response must retain its limitations and coverage state.

## 5. Stable provider error categories

The schema defines:

- `invalid_request`
- `authentication_configuration`
- `permission_licensing`
- `quota_rate_limit`
- `timeout`
- `network_unavailable`
- `provider_server_error`
- `invalid_provider_response`
- `unsupported_operation`

Adapters may retain a provider-specific safe code, but application/domain code consumes these TruckFood categories. Secrets, credentials, raw sensitive coordinates and unnecessary request payloads must not enter error messages or logs.

## 6. Vehicle and routing safety

The capability declaration must state actual support per vehicle parameter. It is not sufficient to declare a provider “truck compatible”. The application must know whether height, width, length, gross mass, axle load, axle count, trailer/configuration, ADR/hazmat and conditional restrictions were accepted and applied.

A successful provider route is not a TruckFood safety certification. Missing critical vehicle values must not be replaced with silent defaults. A generic car route must never silently replace a required truck route. Coverage gaps and omitted constraints must be disclosed.

## 7. Conformance requirements

Every adapter implementation must eventually pass deterministic tests for:

1. Supported, limited, unsupported and unknown capabilities.
2. Regional scope and known coverage gaps.
3. Each safety-relevant vehicle parameter mapping.
4. Time-dependent and conditional restriction support.
5. Empty, partial, unsupported, unavailable, rate-limited and malformed responses.
6. Provenance and timestamp preservation.
7. Rights checks for display, processing, caching, storage, transformation, redistribution and offline use.
8. Error normalization, timeout and bounded retry behaviour.
9. Cost metering and secret-safe logging.
10. Deterministic operation without network access or paid credentials.

Live provider smoke tests are optional supplements, not the sole evidence of correctness.

## 8. Versioning and compatibility

- The contract version changes when required fields, semantics or enum meanings change incompatibly.
- Additive optional fields may be introduced compatibly, subject to consumer tolerance.
- Unknown enum values must fail closed for safety and data-rights decisions.
- Provider API/product version and adapter version remain separate from the TruckFood contract version.
- Old declarations and results used for decisions should remain traceable through version and provenance metadata.

## 9. Implementation status

**Not implemented.** This document and its JSON Schema define proposed contracts only. There is no provider registry, live adapter, provider account, routing integration, ingestion job, licence enforcement engine, cost dashboard or production configuration. The validation workflow checks schema/specification artifacts and fixtures only; it does not call external providers.
