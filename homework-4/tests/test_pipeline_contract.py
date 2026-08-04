from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parent
AGENTS = ROOT / "agents"
SKILLS = ROOT / "skills"
CODEX_AGENTS = REPOSITORY / ".codex" / "agents"
BUG_CONTEXT = ROOT / "context" / "bugs" / "001-order-receipt"

REQUIRED_AGENTS = {
    "bug-researcher.agent.md": ("Bug Researcher", "codebase-research.md"),
    "research-verifier.agent.md": (
        "Bug Research Verifier",
        "verified-research.md",
    ),
    "bug-planner.agent.md": ("Bug Planner", "implementation-plan.md"),
    "bug-fixer.agent.md": ("Bug Fixer", "fix-summary.md"),
    "security-verifier.agent.md": (
        "Security Vulnerabilities Verifier",
        "security-report.md",
    ),
    "unit-test-generator.agent.md": ("Unit Test Generator", "test-report.md"),
    "pipeline-orchestrator.agent.md": ("Pipeline Orchestrator", "run order"),
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class AgentDefinitionTests(unittest.TestCase):
    def test_all_agent_definitions_have_explicit_models_and_outputs(self) -> None:
        for filename, (name, output) in REQUIRED_AGENTS.items():
            with self.subTest(agent=filename):
                content = read(AGENTS / filename)
                self.assertTrue(content.startswith("---\n"))
                frontmatter = content.split("---", 2)[1]
                self.assertRegex(frontmatter, rf"(?m)^name:\s*{re.escape(name)}$")
                self.assertRegex(frontmatter, r"(?m)^description:\s*.+$")
                self.assertRegex(frontmatter, r"(?m)^model:\s*gpt-5\.6-(sol|terra)$")
                self.assertIn(output, content)

    def test_verifiers_and_generator_reference_required_skills(self) -> None:
        verifier = read(AGENTS / "research-verifier.agent.md")
        generator = read(AGENTS / "unit-test-generator.agent.md")

        self.assertIn("skills/research-quality-measurement.md", verifier)
        self.assertIn("skills/unit-tests-FIRST.md", generator)

    def test_planner_and_fixer_require_contract_safe_report_formats(self) -> None:
        planner = read(AGENTS / "bug-planner.agent.md")
        fixer = read(AGENTS / "bug-fixer.agent.md")

        for heading in (
            "## Files and Locations",
            "## Test Commands",
            "## Expected Results",
        ):
            self.assertIn(heading, planner)
        for heading in (
            "## Changes Made",
            "## Overall Status",
            "## Manual Verification",
            "## References",
        ):
            self.assertIn(heading, fixer)
        self.assertIn("homework-4/src/", fixer)
        self.assertIn("homework-4/tests/", fixer)

    def test_orchestrator_declares_exact_sequential_run_order(self) -> None:
        content = read(AGENTS / "pipeline-orchestrator.agent.md")
        expected = [
            "Bug Researcher",
            "Bug Research Verifier",
            "Bug Planner",
            "Bug Fixer",
            "Security Vulnerabilities Verifier",
            "Unit Test Generator",
        ]

        positions = [content.index(name) for name in expected]

        self.assertEqual(positions, sorted(positions))
        self.assertIn("sequential", content.lower())
        self.assertIn("stop", content.lower())


class SkillDefinitionTests(unittest.TestCase):
    def test_research_quality_skill_defines_all_levels(self) -> None:
        content = read(SKILLS / "research-quality-measurement.md")

        for level in (
            "EXCELLENT",
            "GOOD",
            "NEEDS_IMPROVEMENT",
            "UNRELIABLE",
        ):
            self.assertIn(level, content)
        self.assertIn("file:line", content)

    def test_first_skill_defines_every_principle(self) -> None:
        content = read(SKILLS / "unit-tests-FIRST.md")

        for principle in (
            "Fast",
            "Independent",
            "Repeatable",
            "Self-validating",
            "Timely",
        ):
            self.assertIn(principle, content)

    def test_first_skill_is_actionable_and_measurable(self) -> None:
        content = read(SKILLS / "unit-tests-FIRST.md")
        required_sections = (
            "## Acceptance Criteria",
            "## Risk-Based Test Selection",
            "## Generation Workflow",
            "## Good Example",
            "## Bad Example",
            "## Anti-Patterns",
            "## Required test-report.md Template",
            "## Completion Checklist",
            "## Stop Conditions",
        )

        for section in required_sections:
            self.assertIn(section, content)
        for term in ("boundary", "security regression", "error propagation", "RED"):
            self.assertIn(term, content)


class ExecutablePipelineTests(unittest.TestCase):
    def test_every_role_has_an_executable_custom_agent_profile(self) -> None:
        profile_names = (
            "bug-researcher",
            "research-verifier",
            "bug-planner",
            "bug-fixer",
            "security-verifier",
            "unit-test-generator",
            "pipeline-orchestrator",
        )

        for profile_name in profile_names:
            with self.subTest(profile=profile_name):
                content = read(CODEX_AGENTS / f"{profile_name}.toml")
                self.assertRegex(content, r'(?m)^name = "[a-z_-]+"$')
                self.assertRegex(content, r'(?m)^description = ".+"$')
                self.assertRegex(content, r'(?m)^model = "gpt-5\.6-(sol|terra)"$')
                self.assertRegex(
                    content,
                    r'(?m)^model_reasoning_effort = "(medium|high|xhigh)"$',
                )
                self.assertIn('developer_instructions = """', content)

    def test_report_writers_can_write_but_forbid_source_edits(self) -> None:
        for profile_name in (
            "bug-researcher",
            "research-verifier",
            "bug-planner",
            "security-verifier",
        ):
            with self.subTest(profile=profile_name):
                content = read(CODEX_AGENTS / f"{profile_name}.toml")
                self.assertIn('sandbox_mode = "workspace-write"', content)
                self.assertRegex(
                    content.lower(),
                    r"(do not|never) (edit|modify) (application |source)",
                )

    def test_runner_exposes_validation_and_one_codex_execution(self) -> None:
        content = read(ROOT / "run-pipeline.sh")

        self.assertIn("--validate-only", content)
        self.assertIn("scripts/validate_pipeline.py", content)
        self.assertIn("pipeline_orchestrator", content)
        self.assertEqual(content.count("codex exec"), 1)
        self.assertIn("--sandbox workspace-write", content)

    def test_project_config_enables_multi_agent_execution(self) -> None:
        content = read(REPOSITORY / ".codex" / "config.toml")

        self.assertIn("[agents]", content)
        self.assertIn("enabled = true", content)
        self.assertIn("max_concurrent_threads_per_session = 4", content)


class PipelineArtifactTests(unittest.TestCase):
    def test_required_pipeline_artifacts_exist_with_mandated_sections(self) -> None:
        artifacts = {
            "bug-context.md": ("Seeded Issues", "Before State", "Expected State"),
            "research/codebase-research.md": (
                "Problem Statements",
                "Root Causes",
                "References",
            ),
            "research/verified-research.md": (
                "Verification Summary",
                "Verified Claims",
                "Discrepancies Found",
                "Research Quality Assessment",
                "References",
            ),
            "implementation-plan.md": (
                "Files and Locations",
                "Test Commands",
                "Expected Results",
            ),
            "fix-summary.md": (
                "Changes Made",
                "Overall Status",
                "Manual Verification",
                "References",
            ),
            "security-report.md": (
                "Scope",
                "Checks Performed",
                "Findings",
                "Overall Status",
            ),
            "test-report.md": (
                "Changed-Code Scope",
                "Tests Generated",
                "FIRST Assessment",
                "Test Results",
            ),
        }

        for relative_path, headings in artifacts.items():
            with self.subTest(artifact=relative_path):
                content = read(BUG_CONTEXT / relative_path)
                for heading in headings:
                    self.assertIn(f"## {heading}", content)

    def test_reports_use_real_homework_source_references(self) -> None:
        reports = (
            "research/codebase-research.md",
            "research/verified-research.md",
            "implementation-plan.md",
            "fix-summary.md",
            "security-report.md",
            "test-report.md",
        )

        for report in reports:
            with self.subTest(report=report):
                content = read(BUG_CONTEXT / report)
                self.assertRegex(
                    content,
                    r"homework-4/(src|tests)/[A-Za-z0-9_./-]+:\d+",
                )


class DocumentationTests(unittest.TestCase):
    def test_readme_contains_submission_and_homework_standard_sections(self) -> None:
        content = read(ROOT / "README.md")

        for heading in (
            "Author",
            "Overview",
            "Features",
            "Tech Stack",
            "Agent Models",
            "Setup",
            "Run the Pipeline",
            "Run the Application",
            "Run Tests",
            "Coverage",
            "Project Structure",
            "Pipeline Artifacts",
            "Screenshots",
        ):
            self.assertIn(f"## {heading}", content)

    def test_required_documentation_files_exist(self) -> None:
        documents = (
            ROOT / "HOWTORUN.md",
            ROOT / "docs" / "ARCHITECTURE.md",
            ROOT / "docs" / "TESTING_GUIDE.md",
            ROOT / "docs" / "AI_USAGE.md",
        )

        for document in documents:
            with self.subTest(document=document.name):
                self.assertGreater(len(read(document)), 200)

    def test_four_png_screenshots_are_nonempty(self) -> None:
        for filename in (
            "pipeline-run.png",
            "fixes.png",
            "security-scan.png",
            "unit-tests.png",
        ):
            with self.subTest(screenshot=filename):
                data = (ROOT / "docs" / "screenshots" / filename).read_bytes()
                self.assertTrue(data.startswith(b"\x89PNG\r\n\x1a\n"))
                self.assertGreater(len(data), 10_000)


if __name__ == "__main__":
    unittest.main()
