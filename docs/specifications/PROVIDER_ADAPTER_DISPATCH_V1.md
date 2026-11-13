# Provider Adapter Dispatch v1

## Purpose

The module src/truckfood_providers/adapters.py adds an in-process dispatch boundary after deterministic registry selection. A provider manifest is data only; it cannot name Python modules, trigger imports or execute code.

## Trust boundary

- Only application code may construct and register adapter instances.
- Registration is explicit and keyed by exact adapter_id + adapter_version.
- Dispatch requires a successful SelectionDecision from the provider registry.
- The selected capability declaration must explicitly mark the requested operation as supported.
- The registered adapter must implement that operation.
- Unknown adapter IDs, version mismatches, unsupported operations and adapter exceptions fail closed.
- Exceptions are normalized; raw exception text and provider response bodies are not exposed.

## Normalized adapter result

The adapter returns one of: success, empty, partial, unsupported, unavailable, rate_limited, invalid, or conflict. Error outcomes require a stable error_code; successful/empty/partial outcomes must not carry one. The dispatcher preserves normalized data, retryability and metadata.

## Explicit non-goals

This increment does not implement network clients, dynamic imports, credentials, automatic retries, failover, timeouts, circuit breakers, quotas, billing, telemetry or live providers. In particular, retryable is metadata only: no retry occurs. A future policy layer must apply bounded retries only to explicitly retryable transient failures and must never relax vehicle, geographic, rights or safety constraints.

## Test coverage

The unit tests cover explicit registration, successful dispatch, no-selection rejection, unknown adapter/version, capability and adapter operation mismatch, exception normalization, invalid adapter return values, duplicate registration and normalized-result validation. CI runs the complete unittest suite.

## Example

    dispatcher = AdapterDispatcher()
    dispatcher.register(
        adapter_id="trusted.poi",
        adapter_version="1.2.0",
        operations={"search_poi"},
        instance=TrustedPoiAdapter(),
    )
    result = dispatcher.dispatch(
        selection,
        operation="search_poi",
        payload={"country_code": "PT"},
    )

The TrustedPoiAdapter class and instance above are supplied by trusted application code; they are not loaded from the manifest.
