from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from truckfood_providers.registry import (
    RegistryError,
    SelectionRequest,
    load_registry,
    select_provider,
)


ROOT = Path(__file__).resolve().parents[1]
CAPABILITY = ROOT / "docs/specifications/examples/provider-capability.fixture.json"


def build_manifest(root: Path, *, rights_state="reviewed", right="allowed"):
    raw = CAPABILITY.read_bytes()
    declaration = json.loads(raw)
    declaration.update({
        "provider_id": "test.provider",
        "adapter_id": "test.poi",
        "adapter_version": "1.0.0",
        "provider_product_version": "test",
        "capability_family": "poi_business",
        "operations": [{
            "operation": "search_poi",
            "support_state": "supported",
            "vehicle_parameters": {"height_m": True, "gross_mass_kg": True},
        }],
        "geography": {"coverage_state": "country_list", "country_codes": ["PT"]},
        "data_rights": {
            "rights_state": rights_state,
            "transient_processing": right,
            "display": right,
        },
    })
    # Serialize exactly once; the registry pins these exact bytes.
    cap_path = root / "capability.json"
    payload = (json.dumps(declaration, sort_keys=True) + "\n").encode()
    cap_path.write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    return {
        "registry_version": "1.0.0",
        "registry_revision": "test-1",
        "environment": "development",
        "entries": [{
            "registry_entry_id": "test.adapter",
            "provider_id": "test.provider",
            "adapter_id": "test.poi",
            "adapter_version": "1.0.0",
            "provider_product_version": "test",
            "environment": "development",
            "lifecycle_state": "enabled",
            "capability_declaration": {
                "reference": "capability.json",
                "sha256": digest,
                "contract_version": "1.0.0",
            },
            "rights_governance": {
                "review_state": "approved",
                "reviewed_at": "2026-11-13T11:00:00Z",
                "review_due_at": "2027-01-01T00:00:00Z",
            },
            "operational_health": {
                "state": "healthy",
                "checked_at": "2026-11-13T11:55:00Z",
            },
            "priority": 10,
        }],
    }


class ProviderRegistryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.manifest_path = self.root / "registry.json"
        self.now = datetime(2026, 11, 13, 12, 0, tzinfo=timezone.utc)
        self.request = SelectionRequest(
            environment="development",
            capability_family="poi_business",
            operation="search_poi",
            country_code="PT",
            required_vehicle_parameters=("height_m", "gross_mass_kg"),
            required_rights=("transient_processing",),
        )

    def tearDown(self):
        self.temp.cleanup()

    def load(self, manifest):
        self.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        return load_registry(self.manifest_path, self.root)

    def test_checked_in_synthetic_fixture_loads_but_is_not_selectable(self):
        manifest_path = ROOT / "docs/specifications/examples/registry.fixture.json"
        manifest = load_registry(manifest_path, ROOT)
        request = SelectionRequest(
            environment="fixture",
            capability_family="poi_business",
            operation="search_poi",
            country_code="PT",
        )
        result = select_provider(manifest, request, now=self.now)
        self.assertFalse(result.selected)
        self.assertIn("not_enabled_in_requested_environment", str(result.rejected))

    def test_selects_eligible_provider(self):
        manifest = self.load(build_manifest(self.root))
        result = select_provider(manifest, self.request, now=self.now)
        self.assertTrue(result.selected)
        self.assertEqual(result.selected_entry["registry_entry_id"], "test.adapter")

    def test_rejects_digest_mismatch(self):
        manifest = build_manifest(self.root)
        manifest["entries"][0]["capability_declaration"]["sha256"] = "0" * 64
        self.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(RegistryError, "SHA-256 mismatch"):
            load_registry(self.manifest_path, self.root)

    def test_rejects_path_traversal(self):
        manifest = build_manifest(self.root)
        manifest["entries"][0]["capability_declaration"]["reference"] = "../outside.json"
        self.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(RegistryError, "escapes"):
            load_registry(self.manifest_path, self.root)

    def test_rejects_identity_mismatch(self):
        manifest = build_manifest(self.root)
        manifest["entries"][0]["adapter_id"] = "other.adapter"
        self.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(RegistryError, "identity mismatch"):
            load_registry(self.manifest_path, self.root)

    def test_rejects_unknown_manifest_environment(self):
        manifest = build_manifest(self.root)
        manifest["environment"] = "production"
        self.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(RegistryError, "environment differs"):
            load_registry(self.manifest_path, self.root)

    def test_fails_closed_when_review_timestamp_missing(self):
        manifest = self.load(build_manifest(self.root))
        manifest["entries"][0]["rights_governance"]["reviewed_at"] = None
        result = select_provider(manifest, self.request, now=self.now)
        self.assertFalse(result.selected)
        self.assertIn("rights_review_missing_or_overdue", str(result.rejected))

    def test_fails_closed_for_unreviewed_rights(self):
        manifest = self.load(build_manifest(self.root, rights_state="review_required"))
        result = select_provider(manifest, self.request, now=self.now)
        self.assertFalse(result.selected)
        self.assertIn("provider_data_rights_not_reviewed", str(result.rejected))

    def test_fails_closed_for_prohibited_right(self):
        manifest = self.load(build_manifest(self.root, right="unknown"))
        result = select_provider(manifest, self.request, now=self.now)
        self.assertFalse(result.selected)
        self.assertIn("required_data_right_not_allowed", str(result.rejected))

    def test_rejects_missing_vehicle_parameter(self):
        manifest = self.load(build_manifest(self.root))
        request = SelectionRequest(
            environment="development", capability_family="poi_business",
            operation="search_poi", required_vehicle_parameters=("adr_hazmat",),
        )
        result = select_provider(manifest, request, now=self.now)
        self.assertFalse(result.selected)
        self.assertIn("required_vehicle_parameter_unsupported:adr_hazmat", str(result.rejected))

    def test_rejects_wrong_country(self):
        manifest = self.load(build_manifest(self.root))
        request = SelectionRequest(
            environment="development", capability_family="poi_business",
            operation="search_poi", country_code="ES",
        )
        result = select_provider(manifest, request, now=self.now)
        self.assertFalse(result.selected)

    def test_rejects_degraded_by_default(self):
        manifest = self.load(build_manifest(self.root))
        manifest["entries"][0]["operational_health"]["state"] = "degraded"
        result = select_provider(manifest, self.request, now=self.now)
        self.assertFalse(result.selected)

    def test_allows_degraded_only_when_requested(self):
        manifest = self.load(build_manifest(self.root))
        manifest["entries"][0]["operational_health"]["state"] = "degraded"
        request = SelectionRequest(**{**self.request.__dict__, "allow_degraded": True})
        result = select_provider(manifest, request, now=self.now)
        self.assertTrue(result.selected)

    def test_rejects_stale_health(self):
        manifest = self.load(build_manifest(self.root))
        manifest["entries"][0]["operational_health"]["checked_at"] = "2026-11-13T11:00:00Z"
        result = select_provider(manifest, self.request, now=self.now)
        self.assertFalse(result.selected)

    def test_rejects_disabled_entry(self):
        manifest = self.load(build_manifest(self.root))
        manifest["entries"][0]["lifecycle_state"] = "suspended"
        result = select_provider(manifest, self.request, now=self.now)
        self.assertFalse(result.selected)

    def test_registry_environment_mismatch(self):
        manifest = self.load(build_manifest(self.root))
        request = SelectionRequest(**{**self.request.__dict__, "environment": "production"})
        result = select_provider(manifest, request, now=self.now)
        self.assertEqual(result.reason, "registry_environment_mismatch")

    def test_no_candidate_is_not_a_fallback(self):
        manifest = self.load(build_manifest(self.root))
        request = SelectionRequest(
            environment="development", capability_family="routing",
            operation="truck_route", required_vehicle_parameters=("height_m",),
        )
        result = select_provider(manifest, request, now=self.now)
        self.assertFalse(result.selected)
        self.assertEqual(result.reason, "no_eligible_provider")

    def test_priority_and_id_are_deterministic(self):
        manifest = self.load(build_manifest(self.root))
        first = manifest["entries"][0]
        second = json.loads(json.dumps(first))
        second["registry_entry_id"] = "aaa.adapter"
        second["priority"] = first["priority"]
        manifest["entries"].append(second)
        result = select_provider(manifest, self.request, now=self.now)
        self.assertEqual(result.selected_entry["registry_entry_id"], "aaa.adapter")


if __name__ == "__main__":
    unittest.main()
