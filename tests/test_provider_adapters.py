from truckfood_providers.adapters import (
    AdapterDispatcher, AdapterRegistrationError, AdapterResult,
)
from truckfood_providers.registry import SelectionDecision
import unittest


class FakeAdapter:
    def __init__(self, result=None, error=None):
        self.result = result or AdapterResult("success", data={"items": [1]})
        self.error = error
        self.calls = []

    def execute(self, operation, payload):
        self.calls.append((operation, payload))
        if self.error:
            raise self.error
        return self.result


def selected_decision(adapter_id="fake.poi", adapter_version="1.0.0"):
    return SelectionDecision(
        {"registry_entry_id": "fake.entry", "adapter_id": adapter_id,
         "adapter_version": adapter_version},
        {"operations": [{"operation": "search_poi", "support_state": "supported"}]},
        (), "selected_by_priority_then_registry_id",
    )


class AdapterDispatcherTests(unittest.TestCase):
    def setUp(self):
        self.dispatcher = AdapterDispatcher()
        self.adapter = FakeAdapter()
        self.dispatcher.register(
            adapter_id="fake.poi", adapter_version="1.0.0",
            operations={"search_poi"}, instance=self.adapter,
        )

    def test_dispatches_to_explicitly_registered_instance(self):
        result = self.dispatcher.dispatch(
            selected_decision(), operation="search_poi", payload={"country": "PT"}
        )
        self.assertEqual(result.outcome, "success")
        self.assertEqual(result.data, {"items": [1]})
        self.assertEqual(len(self.adapter.calls), 1)

    def test_unselected_provider_is_never_invoked(self):
        decision = SelectionDecision(None, None, (), "no_eligible_provider")
        result = self.dispatcher.dispatch(decision, operation="search_poi", payload={})
        self.assertEqual(result.error_code, "provider_not_selected")
        self.assertEqual(self.adapter.calls, [])

    def test_unknown_adapter_id_fails_closed(self):
        result = self.dispatcher.dispatch(
            selected_decision("not.registered"), operation="search_poi", payload={}
        )
        self.assertEqual(result.error_code, "trusted_adapter_not_registered")

    def test_version_mismatch_fails_closed(self):
        result = self.dispatcher.dispatch(
            selected_decision(adapter_version="2.0.0"),
            operation="search_poi", payload={},
        )
        self.assertEqual(result.error_code, "trusted_adapter_not_registered")

    def test_operation_must_be_declared_by_provider(self):
        result = self.dispatcher.dispatch(
            selected_decision(), operation="get_route", payload={}
        )
        self.assertEqual(result.outcome, "unsupported")
        self.assertEqual(self.adapter.calls, [])

    def test_operation_must_be_implemented_by_adapter(self):
        decision = SelectionDecision(
            {"registry_entry_id": "fake.entry", "adapter_id": "fake.poi",
             "adapter_version": "1.0.0"},
            {"operations": [{"operation": "geocode", "support_state": "supported"}]},
            (), "selected_by_priority_then_registry_id",
        )
        result = self.dispatcher.dispatch(
            decision, operation="geocode", payload={}
        )
        self.assertEqual(result.error_code, "operation_not_implemented_by_adapter")
        self.assertEqual(self.adapter.calls, [])

    def test_adapter_exception_is_normalized_without_leaking_details(self):
        secret = "sensitive-provider-response"
        failing = FakeAdapter(error=RuntimeError(secret))
        dispatcher = AdapterDispatcher()
        dispatcher.register(
            adapter_id="fake.poi", adapter_version="1.0.0",
            operations={"search_poi"}, instance=failing,
        )
        result = dispatcher.dispatch(
            selected_decision(), operation="search_poi", payload={}
        )
        self.assertEqual(result.outcome, "unavailable")
        self.assertEqual(result.error_code, "adapter_execution_failed")
        self.assertNotIn(secret, str(result))

    def test_non_adapter_return_value_is_invalid(self):
        invalid = FakeAdapter(result="not-normalized")
        dispatcher = AdapterDispatcher()
        dispatcher.register(
            adapter_id="fake.poi", adapter_version="1.0.0",
            operations={"search_poi"}, instance=invalid,
        )
        result = dispatcher.dispatch(
            selected_decision(), operation="search_poi", payload={}
        )
        self.assertEqual(result.outcome, "invalid")
        self.assertEqual(result.error_code, "adapter_returned_invalid_result")

    def test_duplicate_registration_is_rejected(self):
        with self.assertRaises(AdapterRegistrationError):
            self.dispatcher.register(
                adapter_id="fake.poi", adapter_version="1.0.0",
                operations={"search_poi"}, instance=FakeAdapter(),
            )

    def test_invalid_result_contract_is_rejected(self):
        with self.assertRaises(ValueError):
            AdapterResult("success", error_code="unexpected")
        with self.assertRaises(ValueError):
            AdapterResult("unavailable")


if __name__ == "__main__":
    unittest.main()
