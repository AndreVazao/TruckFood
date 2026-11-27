"""Coordinator smoke/regression tests with synthetic adapters only."""
import unittest
from unittest.mock import Mock

from truckfood_providers.adapters import AdapterDispatcher, AdapterResult
from truckfood_providers.circuit_breaker import CircuitBreaker
from truckfood_providers.coordinator import ProviderExecutionCoordinator
from truckfood_providers.resilience import ResilienceExecutor, RetryPolicy
from truckfood_providers.quota import QuotaManager, QuotaPolicy


class FakeAdapter:
    def __init__(self, outcome="success", retryable=False):
        self.calls = 0
        self.outcome = outcome
        self.retryable = retryable

    def execute(self, operation, payload):
        self.calls += 1
        if self.outcome in {"success", "empty", "partial"}:
            return AdapterResult(outcome=self.outcome, data={"fixture": True})
        return AdapterResult(outcome=self.outcome, error_code="synthetic_error", retryable=self.retryable)


class Decision:
    selected = True
    reason = "synthetic"
    selected_entry = {"provider_id": "fake", "adapter_id": "fake-adapter", "adapter_version": "1"}
    capability_declaration = {"operations": [{"operation": "lookup", "support_state": "supported"}]}


class CoordinatorTests(unittest.TestCase):
    def make_coordinator(self, adapter, quota=True):
        dispatcher = AdapterDispatcher()
        dispatcher.register(adapter_id="fake-adapter", adapter_version="1",
                           operations={"lookup"}, instance=adapter)
        q = QuotaManager({("fake", "lookup"): QuotaPolicy(max_units=5)}) if quota else None
        coordinator = ProviderExecutionCoordinator(
            dispatcher=dispatcher, resilience=ResilienceExecutor(
                RetryPolicy(max_attempts=2, base_delay_seconds=0, max_delay_seconds=0),
                sleeper=lambda _: None, random_value=lambda: 0,
            ), circuit_breaker=CircuitBreaker(), quota_manager=q,
        )
        return coordinator, q

    def test_quota_reserved_before_dispatch_and_settled_conservatively(self):
        adapter = FakeAdapter()
        coordinator, quota = self.make_coordinator(adapter)
        result = coordinator.execute(Decision(), operation="lookup", payload={},
                                    deadline_seconds=1, reservation_id="r-1")
        self.assertEqual(result.dispatch.outcome, "success")
        self.assertEqual(result.quota_state, "settled_conservatively")
        self.assertEqual(adapter.calls, 1)
        snap = quota.snapshot("fake", "lookup")
        self.assertEqual(snap.consumed_units, 1)
        self.assertEqual(snap.reserved_units, 0)

    def test_requires_reservation_id_when_quota_enabled(self):
        adapter = FakeAdapter()
        coordinator, quota = self.make_coordinator(adapter)
        result = coordinator.execute(Decision(), operation="lookup", payload={},
                                    deadline_seconds=1)
        self.assertEqual(result.dispatch.error_code, "quota_reservation_id_required")
        self.assertEqual(adapter.calls, 0)

    def test_malformed_selection_fails_before_invocation(self):
        adapter = FakeAdapter()
        coordinator, _ = self.make_coordinator(adapter, quota=False)
        result = coordinator.execute(Decision(), operation="lookup", payload={},
                                    deadline_seconds=1)
        self.assertEqual(result.dispatch.outcome, "success")
        bad = Mock(selected=True, selected_entry="bad")
        rejected = coordinator.execute(bad, operation="lookup", payload={}, deadline_seconds=1)
        self.assertEqual(rejected.dispatch.outcome, "invalid")
        self.assertEqual(adapter.calls, 1)

    def test_quota_released_when_no_registered_adapter_is_invoked(self):
        adapter = FakeAdapter()
        dispatcher = AdapterDispatcher()
        coordinator = ProviderExecutionCoordinator(
            dispatcher=dispatcher,
            resilience=ResilienceExecutor(),
            circuit_breaker=CircuitBreaker(),
            quota_manager=QuotaManager({("fake", "lookup"): QuotaPolicy(max_units=5)}),
        )
        result = coordinator.execute(
            Decision(), operation="lookup", payload={}, deadline_seconds=1,
            reservation_id="not-invoked",
        )
        self.assertEqual(result.dispatch.error_code, "trusted_adapter_not_registered")
        self.assertFalse(result.provider_invocation_attempted)
        self.assertEqual(result.quota_state, "released_confirmed_no_invocation")
        snap = coordinator.quota_manager.snapshot("fake", "lookup")
        self.assertEqual(snap.consumed_units, 0)
        self.assertEqual(snap.reserved_units, 0)
        self.assertEqual(adapter.calls, 0)

    def test_quota_missing_policy_fails_closed(self):
        adapter = FakeAdapter()
        dispatcher = AdapterDispatcher()
        dispatcher.register(adapter_id="fake-adapter", adapter_version="1",
                            operations={"lookup"}, instance=adapter)
        coordinator = ProviderExecutionCoordinator(
            dispatcher=dispatcher, resilience=ResilienceExecutor(),
            circuit_breaker=CircuitBreaker(),
            quota_manager=QuotaManager({("other", "lookup"): QuotaPolicy(max_units=1)}),
        )
        result = coordinator.execute(Decision(), operation="lookup", payload={},
                                    deadline_seconds=1, reservation_id="missing")
        self.assertEqual(result.dispatch.error_code, "quota_admission_denied")
        self.assertEqual(adapter.calls, 0)


if __name__ == "__main__":
    unittest.main()
