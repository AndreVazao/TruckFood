# Provider Operation Idempotency v1

## Status

Implemented as an explicit retry-safety gate in the provider retry executor. It is a contract-level safeguard, not proof that a remote provider honours idempotency keys.

## Policy

Every execution receives an `OperationRetryPolicy`. The default is `never`; an adapter's `retryable=True` flag cannot override it.

Supported declarations:

- `never`: exactly one attempt, regardless of transient outcome.
- `idempotent`: retries may occur for allowlisted transient outcomes when the adapter also marks the result retryable.
- `idempotency_key_required`: same retry eligibility as above, but a non-empty key is mandatory before the callback can run.

The executor passes an immutable `ExecutionContext` to every callback. For key-required operations, the exact same key is present on every attempt. The callback MUST forward it unchanged to the provider's documented idempotency mechanism. If the provider does not support such a mechanism, the operation must remain `never`.

## Safety rules

- Never infer idempotency from HTTP method, operation name, transport error or adapter retry flag.
- Reserve `never` for all operations until an explicit reviewed declaration exists.
- Reservation, order creation, payment and other side-effecting operations must use `never` unless the provider's idempotency contract and key scope/retention semantics have been verified.
- Keys must be stable across retries of one logical operation, unique across distinct logical operations, non-secret, and scoped according to the provider contract.
- Do not generate a new key per attempt.
- Do not log raw keys. Metadata records only whether a key-required policy was used.
- A timeout after a side effect may have committed is an uncertain outcome, not permission to issue a fresh operation.

## Limitations

This increment passes the key to the application callback but cannot independently prove that callback forwards it to a remote provider or that the provider deduplicates requests. No real provider, payment, booking, order or network integration is enabled.
