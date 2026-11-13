"""Deterministic, fail-closed provider registry loading and selection.

This module deliberately does not load third-party code or make network calls.
Adapters must be registered by trusted application code in a later integration
layer; a registry manifest is data, never an instruction to import code.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


class RegistryError(ValueError):
    """The registry or a pinned capability declaration is invalid."""


@dataclass(frozen=True)
class SelectionRequest:
    environment: str
    capability_family: str
    operation: str
    country_code: str | None = None
    required_vehicle_parameters: tuple[str, ...] = ()
    required_rights: tuple[str, ...] = ("transient_processing",)
    allow_degraded: bool = False


@dataclass(frozen=True)
class SelectionDecision:
    selected_entry: dict[str, Any] | None
    capability_declaration: dict[str, Any] | None
    rejected: tuple[tuple[str, str], ...]
    reason: str

    @property
    def selected(self) -> bool:
        return self.selected_entry is not None


def _parse_time(value: str | None) -> datetime | None:
    if value is None:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise RegistryError(f"Invalid ISO-8601 timestamp: {value!r}") from exc
    if parsed.tzinfo is None:
        raise RegistryError("Timestamps must include a timezone.")
    return parsed.astimezone(timezone.utc)


def _required(mapping: dict[str, Any], keys: Iterable[str], where: str) -> None:
    missing = [key for key in keys if key not in mapping]
    if missing:
        raise RegistryError(f"{where} missing required fields: {', '.join(missing)}")


def _safe_declaration_path(root: Path, reference: str) -> Path:
    root_resolved = root.resolve()
    candidate = (root_resolved / reference).resolve()
    if candidate != root_resolved and root_resolved not in candidate.parents:
        raise RegistryError("Capability declaration reference escapes repository root.")
    if not candidate.is_file():
        raise RegistryError(f"Capability declaration not found: {reference}")
    return candidate


def load_registry(manifest_path: str | Path, repository_root: str | Path) -> dict[str, Any]:
    """Load manifest and verify each referenced declaration's digest and identity."""
    manifest_file = Path(manifest_path)
    root = Path(repository_root)
    try:
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RegistryError(f"Cannot read registry manifest: {exc}") from exc

    if not isinstance(manifest, dict):
        raise RegistryError("Registry manifest must be a JSON object.")
    _required(manifest, ("registry_version", "registry_revision", "environment", "entries"), "manifest")
    if manifest["registry_version"] != "1.0.0":
        raise RegistryError("Unsupported registry_version.")
    if manifest["environment"] not in {"fixture", "development", "staging", "production"}:
        raise RegistryError("Invalid registry environment.")
    if not isinstance(manifest["entries"], list):
        raise RegistryError("entries must be an array.")

    seen: set[str] = set()
    for index, entry in enumerate(manifest["entries"]):
        where = f"entries[{index}]"
        if not isinstance(entry, dict):
            raise RegistryError(f"{where} must be an object.")
        _required(entry, (
            "registry_entry_id", "provider_id", "adapter_id", "adapter_version",
            "provider_product_version", "environment", "lifecycle_state",
            "capability_declaration", "rights_governance", "operational_health",
            "priority",
        ), where)
        entry_id = entry["registry_entry_id"]
        if not isinstance(entry_id, str) or not entry_id or entry_id in seen:
            raise RegistryError(f"{where} has an empty or duplicate registry_entry_id.")
        seen.add(entry_id)
        if entry["environment"] not in {"fixture", "development", "staging", "production"}:
            raise RegistryError(f"{where} has invalid environment.")
        if entry["environment"] != manifest["environment"]:
            raise RegistryError(f"{where} environment differs from manifest environment.")
        if entry["lifecycle_state"] not in {
            "draft", "under_review", "approved", "enabled", "suspended", "retired"
        }:
            raise RegistryError(f"{where} has invalid lifecycle_state.")
        if not isinstance(entry["priority"], int) or entry["priority"] < 0:
            raise RegistryError(f"{where} priority must be a non-negative integer.")

        pin = entry["capability_declaration"]
        if not isinstance(pin, dict):
            raise RegistryError(f"{where} capability_declaration must be an object.")
        _required(pin, ("reference", "sha256", "contract_version"), f"{where}.capability_declaration")
        if pin["contract_version"] != "1.0.0":
            raise RegistryError(f"{where} has unsupported capability contract version.")
        declaration_file = _safe_declaration_path(root, pin["reference"])
        raw = declaration_file.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != pin["sha256"]:
            raise RegistryError(f"{where} capability declaration SHA-256 mismatch.")
        try:
            declaration = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RegistryError(f"{where} capability declaration is invalid JSON.") from exc
        if not isinstance(declaration, dict):
            raise RegistryError(f"{where} capability declaration must be an object.")
        if declaration.get("declaration_type") != "provider_capability":
            raise RegistryError(f"{where} reference is not a capability declaration.")
        for key in ("provider_id", "adapter_id", "adapter_version", "provider_product_version"):
            if entry[key] != declaration.get(key):
                raise RegistryError(f"{where} identity mismatch for {key}.")
        entry["_capability_declaration"] = declaration

    return manifest


def _candidate_rejection(
    entry: dict[str, Any],
    declaration: dict[str, Any],
    request: SelectionRequest,
    now: datetime,
) -> str | None:
    if entry["environment"] != request.environment or entry["lifecycle_state"] != "enabled":
        return "not_enabled_in_requested_environment"

    rights_governance = entry["rights_governance"]
    if rights_governance.get("review_state") != "approved":
        return "rights_governance_not_approved"
    reviewed_at = _parse_time(rights_governance.get("reviewed_at"))
    due = _parse_time(rights_governance.get("review_due_at"))
    if reviewed_at is None or reviewed_at > now or due is None or due <= now:
        return "rights_review_missing_or_overdue"

    health = entry["operational_health"]
    health_state = health.get("state", "unknown")
    checked = _parse_time(health.get("checked_at"))
    if health_state == "disabled" or health_state == "unavailable":
        return "provider_unavailable"
    if health_state == "degraded" and not request.allow_degraded:
        return "provider_degraded"
    if health_state not in {"healthy", "degraded"} or checked is None:
        return "provider_health_unknown"
    if (now - checked).total_seconds() > 900:
        return "provider_health_stale"

    if declaration.get("capability_family") != request.capability_family:
        return "capability_family_mismatch"
    operation = next(
        (item for item in declaration.get("operations", [])
         if item.get("operation") == request.operation),
        None,
    )
    if operation is None:
        return "operation_not_declared"
    if operation.get("support_state") != "supported":
        return "operation_not_fully_supported"

    geography = declaration.get("geography", {})
    if geography.get("coverage_state") == "unknown":
        return "geographic_coverage_unknown"
    if request.country_code:
        codes = geography.get("country_codes", [])
        if request.country_code not in codes and geography.get("coverage_state") != "global":
            return "country_not_in_declared_coverage"

    vehicle = operation.get("vehicle_parameters", declaration.get("vehicle_parameters", {}))
    for parameter in request.required_vehicle_parameters:
        if vehicle.get(parameter) is not True:
            return f"required_vehicle_parameter_unsupported:{parameter}"

    rights = declaration.get("data_rights", {})
    if rights.get("rights_state") != "reviewed":
        return "provider_data_rights_not_reviewed"
    for right in request.required_rights:
        if rights.get(right) != "allowed":
            return f"required_data_right_not_allowed:{right}"

    return None


def select_provider(
    manifest: dict[str, Any],
    request: SelectionRequest,
    *,
    now: datetime | None = None,
) -> SelectionDecision:
    """Select the best eligible entry; never silently relax mandatory constraints."""
    instant = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    rejected: list[tuple[str, str]] = []
    eligible: list[tuple[dict[str, Any], dict[str, Any]]] = []

    if manifest.get("environment") != request.environment:
        return SelectionDecision(None, None, (), "registry_environment_mismatch")

    for entry in manifest.get("entries", []):
        declaration = entry.get("_capability_declaration")
        if not isinstance(declaration, dict):
            rejected.append((entry.get("registry_entry_id", "<unknown>"), "declaration_not_loaded"))
            continue
        reason = _candidate_rejection(entry, declaration, request, instant)
        if reason:
            rejected.append((entry["registry_entry_id"], reason))
        else:
            eligible.append((entry, declaration))

    eligible.sort(key=lambda pair: (pair[0]["priority"], pair[0]["registry_entry_id"]))
    if not eligible:
        return SelectionDecision(None, None, tuple(rejected), "no_eligible_provider")
    entry, declaration = eligible[0]
    return SelectionDecision(entry, declaration, tuple(rejected), "selected_by_priority_then_registry_id")
