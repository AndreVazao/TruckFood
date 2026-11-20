# Provider Quota Backend Selection Matrix v1

- **Status:** Decision-support document; no backend approved
- **Date:** 2026-11-20
- **Related:** `SHARED_PROVIDER_QUOTA_LEDGER_V1.md`, `PROVIDER_QUOTA_MANAGER_V1.md`, PR #9

## 1. Decision objective

Select the smallest operationally sound backend that can enforce quota admission atomically across workers, preserve reservations across restarts, and safely reconcile uncertain external provider operations.

The backend must not be selected by popularity, anticipated scale without evidence, or the ease of a first prototype. It must meet the correctness contract in the shared ledger specification.

## 2. Candidate comparison

| Candidate | Atomic multi-worker admission | Durability/recovery | Operational burden | Local development | Initial assessment |
|---|---|---|---|---|---|
| PostgreSQL transaction | Strong when bucket/reservation writes and quota admission use an appropriate transaction/locking or atomic update strategy | Durable when configured and backed up correctly | Moderate; may share the primary application database | Good if the project already uses it or can provide a consistent local instance | **Preferred candidate to investigate** |
| Redis atomic script / transaction | Strong for carefully designed atomic scripts/transactions; must validate data model and failure semantics | Depends on persistence, replication, failover and configuration; cannot assume durable by default | Additional service if not already operated | Easy with container/service but adds a dependency | Candidate only if throughput/latency evidence justifies separate operational system |
| SQLite | Atomic within one database file and suitable locking; write concurrency is limited | Durable file with backup/restore requirements | Low for single-host deployment | Excellent | Useful for single-host/offline/dev; not assumed suitable for multi-host workers |
| In-memory | Atomic within process locks only | Lost on restart | Very low | Excellent | Tests and local-only demonstration; **not** shared production authority |
| Managed database/ledger service | Depends on service's transaction and API guarantees | Depends on vendor durability, backup and recovery contracts | Vendor-managed, but adds contractual/security/egress considerations | May require emulator or remote dev environment | Evaluate only after concrete service and terms are known |

This table is qualitative and does not substitute for provider-specific documentation, benchmark results, deployment evidence or failure testing.

## 3. Weighted decision criteria

Score each shortlisted candidate from 1 (poor/not demonstrated) to 5 (excellent/demonstrated). A missing fact is scored **unknown**, not optimistically.

| Criterion | Weight | Evidence required |
|---|---:|---|
| Atomic quota admission under concurrent processes | 25% | Multi-process test that saturates a shared bucket without exceeding it |
| Durable reserve/settle/release state | 20% | Commit/restart/reconnect test and explicit failure behaviour |
| Correct uncertain-commit retry and idempotency | 15% | Timeout injection; same reservation ID recovers authoritative result |
| Crash/reconciliation and audit semantics | 10% | Worker crash after dispatch, stale retention and late settlement tests |
| Security and isolation | 10% | Scope model, least privilege, tenant isolation, credential handling |
| Operational fit (hosting, backups, monitoring, recovery) | 10% | Runbook, backup/restore evidence, owner and recovery objectives |
| Cost and deployment complexity | 5% | Actual monthly estimate, resource assumptions, operational dependencies |
| Local developer/test parity | 5% | Repeatable isolated setup and CI strategy |

**Gate:** Do not total a weighted score while any critical correctness criteria are unknown. The atomicity, durability, uncertain-commit and isolation criteria are hard gates, not trade-offs against convenience or cost.

## 4. Provisional direction

1. Investigate PostgreSQL first because the wider TruckFood architecture has already proposed PostgreSQL/PostGIS and a quota ledger could potentially share the same operational database.
2. Verify whether the proposal is actually adopted, available in development/CI and intended for the deployment target. The current repository evidence available for this increment does not establish a live database, deployment or production dependency.
3. If PostgreSQL is available, design a transaction using a bucket row/atomic conditional update plus reservation identity uniqueness. Validate isolation and deadlock/retry behaviour experimentally.
4. Keep Redis out of the first implementation unless measured contention/latency or an existing operational deployment justifies it. A second datastore increases failure modes and reconciliation complexity.
5. Keep SQLite as a possible local/single-host option, not an automatic production substitute for multi-host coordination.
6. Retain the in-memory implementation for deterministic unit tests and isolated local use, clearly labelled process-local.

No backend is approved by this matrix.

## 5. Evidence checklist before a decision

- [ ] Confirm runtime/package layout, Python version and supported process model.
- [ ] Confirm the existing database choice, if any, from repository configuration and deployment evidence.
- [ ] Identify whether application workers run on one host or multiple hosts.
- [ ] Define quota scope per provider (global/account/credential/tenant) using provider-specific evidence.
- [ ] Define the unit and whether quotas are rate, fixed-window, rolling-window, daily, monthly or budget limits.
- [ ] Define provider-specific status/idempotency APIs and the limitations of reconciliation.
- [ ] Define expected concurrent reservations, peak throughput and latency target from workload estimates.
- [ ] Confirm atomicity and durability semantics for the chosen service and failure modes.
- [ ] Define RPO/RTO, backup retention, restore procedure and operational owner.
- [ ] Estimate costs and dependency footprint for production and development.
- [ ] Verify security model, network access, secret rotation, authorization and audit.
- [ ] Create multi-process tests and fault injection for transaction ambiguity, restart and provider outcome uncertainty.
- [ ] Document rollback/migration plan and how outstanding reservations are preserved.

## 6. Scope and deployment assumptions

Do not infer a quota key from a user-provided value. Scope should be configured and validated by the trusted application. For example, if a provider enforces one shared account quota, tenant-specific ledgers must not multiply that quota. If the provider enforces separate credential limits, those credential identities must be mapped securely and consistently.

The ledger is an accounting and admission-control primitive, not a billing system. Cost units, monetary budgets and currency conversion remain separate domains.

## 7. Decision outcome

**Outcome: defer backend selection.** PostgreSQL is the first candidate for evidence gathering; it is not approved. No runtime code, dependency, schema, migration, credentials, service, paid integration or deployment is introduced by this document.

A subsequent implementation PR must cite the decision evidence, implement behind the quota domain port, and pass the shared-ledger verification matrix before any non-production enablement.
