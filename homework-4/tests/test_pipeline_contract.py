from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parent
AGENTS = ROOT / "agents"
SKILLS = ROOT / "skills"
CODEX_AGENTS = REPOSITORY / ".codex" / "agents"

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

    def test_non_editing_profiles_are_read_only(self) -> None:
        for profile_name in (
            "bug-researcher",
            "research-verifier",
            "bug-planner",
            "security-verifier",
        ):
            with self.subTest(profile=profile_name):
                content = read(CODEX_AGENTS / f"{profile_name}.toml")
                self.assertIn('sandbox_mode = "read-only"', content)

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


if __name__ == "__main__":
    unittest.main()
