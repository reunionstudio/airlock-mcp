from __future__ import annotations

import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from airlock_mcp.cli import main


def run_cli(args: list[str]) -> tuple[int, str, str]:
    stdout = StringIO()
    stderr = StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        exit_code = main(args)
    return exit_code, stdout.getvalue(), stderr.getvalue()


class CliTests(unittest.TestCase):
    def test_init_posts_workspace_checks_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(run_cli(["init", "feedback-loop", "--pattern", "posts", "--output", str(root)])[0], 0)
            workspace = root / "feedback-loop"
            self.assertTrue((workspace / "spec.config.json").exists())
            self.assertEqual(run_cli(["check", str(workspace)])[0], 0)

    def test_init_defaults_to_blank_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(run_cli(["init", "Customer Onboarding", "--output", str(root)])[0], 0)
            config = json.loads((root / "Customer Onboarding" / "spec.config.json").read_text())
            self.assertEqual(config["core_config"]["spec_name"], "customer_onboarding")

    def test_blank_workspace_uses_workspace_name_as_spec_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            exit_code, _stdout, _stderr = run_cli(
                ["init", "Weekly Timesheets", "--pattern", "blank", "--output", str(root)]
            )
            self.assertEqual(exit_code, 0)
            config = json.loads((root / "Weekly Timesheets" / "spec.config.json").read_text())
            self.assertEqual(config["core_config"]["spec_name"], "weekly_timesheets")

    def test_check_fails_on_duplicate_columns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(run_cli(["init", "bad", "--pattern", "blank", "--output", str(root)])[0], 0)
            workspace = root / "bad"
            config_path = workspace / "spec.config.json"
            config = json.loads(config_path.read_text())
            config["column_config"].append(config["column_config"][0])
            config_path.write_text(json.dumps(config), encoding="utf-8")
            self.assertEqual(run_cli(["check", str(workspace)])[0], 1)

    def test_import_spec_config_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.json"
            source.write_text(
                json.dumps(
                    {
                        "specName": "feedback",
                        "specConfig": {
                            "core_config": {
                                "spec_name": "feedback",
                                "spec_alias": "Feedback",
                                "description": "Imported feedback spec.",
                                "owner_role": "app_admin",
                            },
                            "column_config": [
                                {
                                    "name": "feedback_id",
                                    "type": "string",
                                    "description": "Feedback id.",
                                    "tests": ["not_null", "unique"],
                                },
                                {
                                    "name": "details",
                                    "type": "variant",
                                    "description": "Details.",
                                    "tests": [],
                                },
                            ],
                            "rules": [
                                {
                                    "type": "variant_shape",
                                    "column": "details",
                                    "allowed_root_keys": ["source"],
                                    "optional_paths": ["$.source.system"],
                                }
                            ],
                            "file_rules": {"file_format": {"file_type": "csv"}},
                        },
                    }
                ),
                encoding="utf-8",
            )

            self.assertEqual(run_cli(["import-spec", str(source), "imported", "--output", str(root)])[0], 0)
            workspace = root / "imported"
            self.assertEqual(run_cli(["check", str(workspace)])[0], 0)
            records = json.loads((workspace / "sample.records.json").read_text())
            self.assertEqual(records["spec_name"], "feedback")

    def test_clone_resets_spec_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(run_cli(["init", "source-spec", "--pattern", "blank", "--output", str(root)])[0], 0)
            self.assertEqual(
                run_cli(["clone", str(root / "source-spec"), "target-spec", "--output", str(root)])[0],
                0,
            )
            cloned = json.loads((root / "target-spec" / "spec.config.json").read_text())
            self.assertEqual(cloned["core_config"]["spec_name"], "target_spec")
            self.assertEqual(run_cli(["check", str(root / "target-spec")])[0], 0)

    def test_render_sql_uses_validate_only_create(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(run_cli(["init", "sql-spec", "--pattern", "blank", "--output", str(root)])[0], 0)
            exit_code, output, _stderr = run_cli(["render-sql", str(root / "sql-spec")])
            self.assertEqual(exit_code, 0)
            self.assertIn("CALL airlock.admin.create_spec", output)
            self.assertIn(", TRUE);", output)

    def test_summary_and_export_csv(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(run_cli(["init", "feedback-loop", "--pattern", "posts", "--output", str(root)])[0], 0)
            workspace = root / "feedback-loop"

            exit_code, summary, _stderr = run_cli(["summary", str(workspace)])
            self.assertEqual(exit_code, 0)
            self.assertIn("spec: posts (Posts)", summary)
            self.assertIn("guest_access: shared public folder: append_access, read_access", summary)

            exit_code, output, _stderr = run_cli(["export-csv", str(workspace)])
            self.assertEqual(exit_code, 0)
            header, row = output.splitlines()
            self.assertEqual(
                header,
                "post_id,reply_to_post_id,submitted_by,posted_at,body,tags,related_area,related_process,details",
            )
            self.assertIn("POST-001", row)
            self.assertIn('"{""agent"":{""name"":""Deb""}', row)

    def test_about_and_self_update_dry_run(self) -> None:
        exit_code, output, _stderr = run_cli(["about"])
        self.assertEqual(exit_code, 0)
        self.assertIn("airlock-mcp", output)
        self.assertIn("forge the handoff", output)
        self.assertIn("init-repo", output)

        exit_code, output, _stderr = run_cli(["self-update", "--dry-run"])
        self.assertEqual(exit_code, 0)
        self.assertIn("dry-run: self-update method:", output)
        self.assertIn("command:", output)

    def test_init_repo_bootstraps_codex_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "my-airlock-specs"
            exit_code, output, _stderr = run_cli(["init-repo", str(root)])
            self.assertEqual(exit_code, 0)
            self.assertTrue((root / "workspaces").is_dir())
            self.assertTrue((root / "AGENTS.md").exists())
            self.assertTrue((root / ".agents" / "skills" / "airlock-mcp" / "SKILL.md").exists())
            self.assertTrue((root / ".agents" / "skills" / "airlock-mcp" / "agents" / "openai.yaml").exists())
            self.assertIn("initialized", output)
            self.assertIn("What process do you want to improve", output)
            self.assertIn("Use Airlock to help me build and use specs", output)

            skill = (root / ".agents" / "skills" / "airlock-mcp" / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("name: airlock-mcp", skill)
            self.assertIn("Spec Design Questions", skill)

            agents_path = root / "AGENTS.md"
            self.assertIn("reunionstudio/airlock-mcp", agents_path.read_text(encoding="utf-8"))
            agents_path.write_text("custom guidance\n", encoding="utf-8")
            exit_code, output, _stderr = run_cli(["init-repo", str(root)])
            self.assertEqual(exit_code, 0)
            self.assertIn("kept AGENTS.md", output)
            self.assertEqual(agents_path.read_text(encoding="utf-8"), "custom guidance\n")

            exit_code, output, _stderr = run_cli(["init-repo", str(root), "--force"])
            self.assertEqual(exit_code, 0)
            self.assertIn("created AGENTS.md", output)
            self.assertIn("Spec Design Priorities", agents_path.read_text(encoding="utf-8"))

    def test_init_repo_rejects_file_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "not-a-directory"
            target.write_text("x", encoding="utf-8")
            exit_code, _output, stderr = run_cli(["init-repo", str(target)])
            self.assertEqual(exit_code, 2)
            self.assertIn("not a directory", stderr)

    def test_list_archive_restore_and_next_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(run_cli(["init", "alpha", "--pattern", "blank", "--output", str(root)])[0], 0)
            self.assertEqual(run_cli(["init", "beta", "--pattern", "blank", "--output", str(root)])[0], 0)

            exit_code, output, _stderr = run_cli(["list-workspaces", "--root", str(root)])
            self.assertEqual(exit_code, 0)
            self.assertIn("alpha", output)
            self.assertIn("beta", output)
            self.assertIn("active", output)

            exit_code, output, _stderr = run_cli(["next", str(root / "alpha")])
            self.assertEqual(exit_code, 0)
            self.assertIn("next:", output)
            self.assertIn("decisions.md", output)
            self.assertIn("messy process goal", output)

            exit_code, _output, stderr = run_cli(["restore", str(root / "beta")])
            self.assertEqual(exit_code, 2)
            self.assertTrue((root / "beta").exists())
            self.assertIn("restore source must be under _archive", stderr)

            exit_code, output, _stderr = run_cli(["rename", str(root / "alpha"), "alpha-renamed"])
            self.assertEqual(exit_code, 0)
            self.assertFalse((root / "alpha").exists())
            self.assertTrue((root / "alpha-renamed").exists())
            self.assertIn("spec identity retitled", output)
            renamed_config = json.loads((root / "alpha-renamed" / "spec.config.json").read_text())
            self.assertEqual(renamed_config["core_config"]["spec_name"], "alpha_renamed")

            exit_code, output, _stderr = run_cli(["archive", str(root / "beta")])
            self.assertEqual(exit_code, 0)
            archived = root / "_archive" / "beta"
            self.assertTrue(archived.exists())
            self.assertIn("archived", output)

            exit_code, output, _stderr = run_cli(["list-workspaces", "--root", str(root), "--all"])
            self.assertEqual(exit_code, 0)
            self.assertIn("archived", output)

            exit_code, output, _stderr = run_cli(["restore", str(archived)])
            self.assertEqual(exit_code, 0)
            self.assertTrue((root / "beta").exists())
            self.assertIn("restored", output)

    def test_next_advances_when_decision_prompts_are_filled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(run_cli(["init", "ready", "--pattern", "blank", "--output", str(root)])[0], 0)
            workspace = root / "ready"
            (workspace / "decisions.md").write_text(
                """# Decisions

## Row Grain

One row is:
one observed draft record.

## OODA Loop

- Observe:
- Orient: validate ids, timestamp, summary, and optional details.
- Decide: accept or revise the draft shape.
- Act: export sample CSV and render validate-only SQL.

## Identifiers

Stable ids and retry-safe keys: record_id.

## Business Time

Event, observed, captured, effective, or transaction timestamps: observed_at.

## Typed Columns

Fields people will filter, join, audit, aggregate, or report on: record_id, observed_at, summary.

## Variant Context

Optional context that may evolve: details.

## Evidence

Attachments and evidence metadata: optional supporting files.

## Access

Submitter, reviewer, reader, owner, and delegation model: app_admin owns review.

## Workflow And Expectations

States, pushback, due dates, order, or cadence: local validation before Airlock validation.
""",
                encoding="utf-8",
            )

            exit_code, output, _stderr = run_cli(["next", str(workspace)])
            self.assertEqual(exit_code, 0)
            self.assertIn("Record the messy process goal", output)

            decisions_path = workspace / "decisions.md"
            decisions_path.write_text(
                decisions_path.read_text(encoding="utf-8").replace(
                    "- Observe:",
                    "- Observe: source file and submitting user.",
                ),
                encoding="utf-8",
            )

            exit_code, output, _stderr = run_cli(["next", str(workspace)])
            self.assertEqual(exit_code, 0)
            self.assertIn("Export sample CSV", output)
            self.assertNotIn("Record the messy process goal", output)

    def test_export_csv_refuses_invalid_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(run_cli(["init", "bad-csv", "--pattern", "blank", "--output", str(root)])[0], 0)
            workspace = root / "bad-csv"
            records_path = workspace / "sample.records.json"
            records = json.loads(records_path.read_text())
            records["records"][0].pop("record_id")
            records_path.write_text(json.dumps(records), encoding="utf-8")

            exit_code, _stdout, stderr = run_cli(["export-csv", str(workspace)])
            self.assertEqual(exit_code, 1)
            self.assertIn("refusing to export CSV", stderr)

    def test_check_flags_shared_guest_access_without_enabled_subfolder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(run_cli(["init", "guest-access", "--pattern", "posts", "--output", str(root)])[0], 0)
            workspace = root / "guest-access"
            config_path = workspace / "spec.config.json"
            config = json.loads(config_path.read_text())
            config["guest_access"]["public_folder"]["subfolders"]["append_access"]["enabled"] = False
            config_path.write_text(json.dumps(config), encoding="utf-8")

            exit_code, output, _stderr = run_cli(["check", str(workspace)])
            self.assertEqual(exit_code, 1)
            self.assertIn("requires the matching public_folder subfolder", output)

    def test_check_warns_for_unshaped_variant(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(run_cli(["init", "unshaped", "--pattern", "blank", "--output", str(root)])[0], 0)
            workspace = root / "unshaped"
            config_path = workspace / "spec.config.json"
            config = json.loads(config_path.read_text())
            config["rules"] = []
            config_path.write_text(json.dumps(config), encoding="utf-8")

            exit_code, output, _stderr = run_cli(["check", str(workspace)])
            self.assertEqual(exit_code, 0)
            self.assertIn("Variant column `details` has no variant_shape rule", output)

    def test_doctor_and_show_pattern(self) -> None:
        self.assertEqual(run_cli(["doctor"])[0], 0)
        exit_code, output, _stderr = run_cli(["show-pattern", "posts"])
        self.assertEqual(exit_code, 0)
        self.assertIn("Starter Pattern: Posts", output)

    def test_install_surface_documents_external_mcp_repo(self) -> None:
        root = Path(__file__).resolve().parents[1]
        readme = (root / "README.md").read_text(encoding="utf-8")
        install_surface = (root / "docs" / "install-surface.md").read_text(encoding="utf-8")
        architecture = (root / "docs" / "architecture.md").read_text(encoding="utf-8")
        workflows = (root / "docs" / "workflows.md").read_text(encoding="utf-8")

        self.assertIn("reunionstudio/airlock-mcp", readme)
        self.assertIn("reunionstudio/airlock-mcp", install_surface)
        self.assertIn("reunionstudio/airlock-mcp", architecture)
        self.assertIn("reunionstudio/airlock-mcp", workflows)
        self.assertIn("npx @reunionstudio/airlock-mcp install", install_surface)
        self.assertIn("codex mcp add airlock", install_surface)
        self.assertIn("single installed interface", install_surface)
        self.assertIn("operating patterns around observe", install_surface)
        self.assertIn("orient, decide, and act", install_surface)
        self.assertIn("Prefer Rust with `rmcp`", install_surface)
        self.assertIn("stdout is the JSON-RPC protocol channel", install_surface)


if __name__ == "__main__":
    unittest.main()
