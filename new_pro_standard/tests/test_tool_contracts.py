from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_tool_contracts  # noqa: E402


def valid_contract(**overrides: object) -> dict[str, object]:
    contract: dict[str, object] = {
        "name": "demo_tool",
        "purpose": "Demonstrate a valid tool contract.",
        "path": "scripts/check_tool_contracts.py",
        "command": "python3 scripts/check_tool_contracts.py",
        "inputs": ["registry JSON"],
        "outputs": ["stdout report", "process exit code"],
        "side_effects": ["read_repo"],
        "permissions": ["read-repo"],
        "timeout_seconds": 30,
        "destructive": False,
        "externally_visible": False,
        "automation_mode": "assistive",
        "verification_commands": ["python3 scripts/check_tool_contracts.py"],
    }
    contract.update(overrides)
    return contract


def registry(*contracts: dict[str, object]) -> dict[str, object]:
    return {"schema_version": 1, "contracts": list(contracts)}


class ToolContractValidationTest(unittest.TestCase):
    def errors_for(self, *contracts: dict[str, object]) -> list[str]:
        return check_tool_contracts.validate_registry(registry(*contracts), root=ROOT).errors

    def test_repository_registry_is_valid(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        result = check_tool_contracts.validate_registry(data, root=ROOT)
        self.assertEqual(result.errors, [])

    def test_stop_runtime_observation_contract_is_local_trace_writer(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        contracts = data["contracts"]
        contract = next(item for item in contracts if item["name"] == "stop_runtime_observation")

        self.assertIn("write_runtime", contract["side_effects"])
        self.assertIn("write-runtime", contract["permissions"])
        self.assertIn(".agent-trace.jsonl", "\n".join(contract["outputs"]))
        self.assertFalse(contract["destructive"])
        self.assertFalse(contract["externally_visible"])
        self.assertIn("scripts/check_agent_trace_schema.py", "\n".join(contract["verification_commands"]))

    def test_otlp_pilot_contract_defaults_to_no_network_export(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        contracts = data["contracts"]
        contract = next(item for item in contracts if item["name"] == "export_agent_trace_otlp_pilot")

        self.assertIn("--format otlp-http-json", contract["command"])
        self.assertEqual(contract["side_effects"], ["read_repo"])
        self.assertFalse(contract["externally_visible"])
        self.assertIn("--send", contract["dangerous_flags"])
        self.assertIn("network_exported evidence flag", "\n".join(contract["outputs"]))

    def test_requires_unique_names(self) -> None:
        errors = self.errors_for(valid_contract(), valid_contract())

        self.assertTrue(any("duplicate name" in error for error in errors))

    def test_rejects_missing_required_field(self) -> None:
        contract = valid_contract()
        del contract["purpose"]

        errors = self.errors_for(contract)

        self.assertTrue(any("missing required field purpose" in error for error in errors))

    def test_rejects_missing_entrypoint_and_verification_path(self) -> None:
        errors = self.errors_for(
            valid_contract(
                path="scripts/missing_tool.py",
                verification_commands=["python3 scripts/missing_tool.py"],
            )
        )

        text = "\n".join(errors)
        self.assertIn("path does not exist", text)
        self.assertIn("references missing path scripts/missing_tool.py", text)

    def test_rejects_unknown_enums_and_bad_timeout(self) -> None:
        errors = self.errors_for(
            valid_contract(
                side_effects=["read_repo", "magic"],
                automation_mode="autopilot",
                timeout_seconds=0,
            )
        )

        text = "\n".join(errors)
        self.assertIn("unknown side_effects value magic", text)
        self.assertIn("automation_mode must be one of", text)
        self.assertIn("timeout_seconds must be between", text)

    def test_rejects_destructive_default_without_human_confirmation(self) -> None:
        errors = self.errors_for(valid_contract(destructive=True))

        text = "\n".join(errors)
        self.assertIn("destructive default command must use human_confirmed", text)
        self.assertIn("human-confirmation-required", text)

    def test_allows_destructive_default_with_required_gate(self) -> None:
        errors = self.errors_for(
            valid_contract(
                destructive=True,
                automation_mode="human_confirmed",
                permissions=["read-repo", "human-confirmation-required"],
            )
        )

        self.assertEqual(errors, [])

    def test_rejects_externally_visible_unattended_default(self) -> None:
        errors = self.errors_for(valid_contract(externally_visible=True, automation_mode="ci"))

        self.assertTrue(any("externally visible default command" in error for error in errors))

    def test_external_write_side_effect_requires_visible_flag(self) -> None:
        errors = self.errors_for(valid_contract(side_effects=["network_write"]))

        self.assertTrue(any("require externally_visible=true" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
