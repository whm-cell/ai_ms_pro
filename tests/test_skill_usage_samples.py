from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_skill_usage_samples  # noqa: E402


SAMPLE_REGISTRY = """# Candidate Skill Eval Samples

### SAMPLE-001 prd

- Date: 2026-05-05
- Skills: prd-to-project-skills
- Evidence Type: real-task
- Outcome: accepted
- baseline_without_skill: baseline
- run_with_skill: run
- delta: less context
- acceptance: accepted
- verification: review

### SAMPLE-002 team

- Date: 2026-05-05
- Skills: team-pr-conflict-control
- Evidence Type: real-task
- Outcome: rejected
- baseline_without_skill: baseline
- run_with_skill: run
- delta: process tax
- acceptance: rejected
- verification: review
"""


class SkillUsageSamplesTest(unittest.TestCase):
    def test_report_includes_rejected_and_observed_skill_counts(self) -> None:
        original_registry = check_skill_usage_samples.SAMPLE_REGISTRY
        with tempfile.TemporaryDirectory() as temp_dir:
            registry = Path(temp_dir) / "skill-usage-samples.md"
            registry.write_text(SAMPLE_REGISTRY, encoding="utf-8")
            check_skill_usage_samples.SAMPLE_REGISTRY = registry
            try:
                report = check_skill_usage_samples.build_report(min_samples=2)
            finally:
                check_skill_usage_samples.SAMPLE_REGISTRY = original_registry

        reports = {item.name: item for item in report.candidate_skills}

        self.assertEqual(reports["prd-to-project-skills"].accepted_complete_eval_samples, 1)
        self.assertEqual(reports["team-pr-conflict-control"].tracking_scope, "observed")
        self.assertEqual(reports["team-pr-conflict-control"].rejected_real_task_samples, 1)


if __name__ == "__main__":
    unittest.main()
