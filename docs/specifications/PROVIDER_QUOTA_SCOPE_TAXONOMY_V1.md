# Provider Quota Scope Taxonomy v1

- **Status:** Decision framework; no provider scope is approved by this taxonomy
- **Date:** 2026-11-23
- **Related:** `PROVIDER_QUOTA_MANAGER_V1.md`, `SHARED_PROVIDER_QUOTA_LEDGER_V1.md`, `QUOTA_BACKEND_SELECTION_MATRIX_V1.md`

## Purpose

Make quota enforcement scope explicit before a shared ledger is implemented. A quota bucket must match the provider's real enforcement boundary, not the TruckFood caller or tenant boundary by convenience.

## Scope categories

| Scope | Meaning | Typical key inputs (opaque IDs only) | Safe default |
|---|---|---|---|
| Provider-global | Provider enforces one limit across all TruckFood usage | provider + operation + provider policy/window | Share one bucket across all tenants and credentials unless evidence proves separate limits |
| Provider account | Limit applies to a provider account/project | provider + account identity + operation | Share across callers using the same account |
| Credential | Limit is independently enforced per credential/token/key | provider + credential identity + operation | Credential identity must be stable, secret-free and centrally mapped |
| Tenant/organization | Provider contract or product plan explicitly grants isolated tenant quota | provider + tenant + operation + contract/policy | Do not partition by tenant without provider/contract evidence |
| Resource-specific | Limit applies to a resource (e.g. a particular project, endpoint, dataset) | provider + resource identity + operation | Explicit provider policy; resource IDs must be normalized and scoped |

## Required mapping

Each configured provider operation must have a reviewed quota mapping record with:

- provider ID and operation;
- provider evidence URL/document reference and review date;
- enforcement scope category;
- stable non-secret scope identifier mapping;
- unit definition (request, lookup, cost unit, byte, or other provider-defined measure);
- limit and window/rate semantics (fixed, rolling, daily/monthly, concurrent, budget, or provider-defined);
- whether the provider returns authoritative usage/reset metadata;
- whether usage can be reconciled after timeout/crash;
- idempotency/status capability and known limitation;
- policy version and responsible reviewer.

Do not log, commit, or expose credential values. Use an opaque internal identifier or keyed fingerprint designed for identity mapping; never use raw secrets as quota keys or diagnostic labels.

## Admission and isolation rules

1. The configured quota scope is server-owned and cannot be chosen by an untrusted request.
2. A shared account/global quota must be enforced in one shared bucket. Creating per-tenant buckets would multiply the allowance and is prohibited.
3. A tenant-specific bucket is valid only when the provider or contract grants an independent quota boundary.
4. A credential-scoped bucket must reflect credential rotation and aliasing without accidentally resetting quota. Credential identity mapping and migration behavior must be defined.
5. Multiple provider operations may share one provider limit. The mapping must support a shared bucket or coordinated policy where evidence says so; operation labels alone must not create extra capacity.
6. Limits and units are not inferred from provider names, pricing pages alone, or generic assumptions. Confirm contractual/API documentation and actual headers/usage semantics.
7. Missing, contradictory or stale scope evidence fails closed for provider dispatch when quota enforcement is required.
8. Tenant authorization and provider quota accounting are separate: tenant identity must not be used to isolate a provider quota unless the provider's actual limit is tenant-partitioned.

## Current code gap

The in-memory `QuotaManager` keys policies and windows by exact `(provider_id, operation)`. This is suitable for a deterministic process-local foundation but cannot represent all shared account/credential/resource scopes or safely coordinate multiple operations consuming one quota. It is not evidence that real provider quota semantics are known.

## Provider evidence checklist

- [ ] Official quota/rate-limit docs or contract reviewed.
- [ ] Scope boundary confirmed (global/account/credential/tenant/resource).
- [ ] Shared limits across operations/endpoints identified.
- [ ] Units and window/reset semantics verified.
- [ ] Retry-after and authoritative usage headers/status verified.
- [ ] Provider status/idempotency/reconciliation capability documented.
- [ ] Secret-free stable identity mapping approved.
- [ ] Multi-worker key design and isolation tests defined.

## Decision

No concrete provider or scope is selected in this document. The next provider integration must complete the mapping above before quota policy configuration, live credentials, or dispatch activation.
