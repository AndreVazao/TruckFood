# Provider Runtime v1 — Implementation Notes

- **Status:** Initial executable foundation on feature branch; not production-ready.
- **Package:** `src/truckfood_providers`
- **Tests:** `tests/test_provider_registry.py`
- **Runtime dependencies:** Python standard library only.

## Implemented in this increment

The first runtime slice provides:

1. JSON manifest loading.
2. Safe resolution of capability declaration paths under an explicit repository root.
3. SHA-256 verification of pinned declaration bytes.
4. Provider/adapter/product version identity matching between registry entry and declaration.
5. Fail-closed candidate filtering for environment, lifecycle, rights-review governance, review due date, health state/freshness, capability family, operation support, country coverage, required vehicle parameters and exact data-use rights.
6. Deterministic selection by ascending priority, then lexical registry entry ID.
7. Rejection reason codes for audit and diagnostics.
8. No dynamic imports, network requests, credential loading or automatic fallback.

## API sketch

```python
from truckfood_providers import SelectionRequest, load_registry, select_provider

manifest = load_registry(
    "config/providers/registry.json",
    repository_root=".",
)
decision = select_provider(
    manifest,
    SelectionRequest(
        environment="fixture",
        capability_family="poi_business",
        operation="search_poi",
        country_code="PT",
    ),
)
```

The checked-in synthetic fixture can be loaded and its digest/identity verified, but it is intentionally ineligible for selection: its lifecycle is `draft`, rights are unreviewed and health is unknown. The code example points to an application-managed manifest with valid pins; no such production manifest is supplied here.

## Current boundaries and limitations

- The loader verifies the pinned declaration's digest and key identity fields. Full JSON Schema validation remains a CI responsibility in this increment.
- The selector currently requires a country code to be explicitly present unless the declaration says coverage is global. Regional geometry matching is not implemented.
- Rights conditions are not evaluated automatically. Only an exact `allowed` value is accepted for each requested right; conditional rights fail closed.
- Health freshness is currently a fixed 15-minute threshold, not a configurable service-level policy.
- Cost/quotas are not yet enforced by the runtime.
- The module selects a registry entry only. It does not instantiate or invoke provider adapter code.
- No live providers, credentials, API calls, map rendering, routing or location processing are included.

## Local test command

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

CI runs this command after schema and fixture validation. A green CI run is required before this increment can be considered validated.
