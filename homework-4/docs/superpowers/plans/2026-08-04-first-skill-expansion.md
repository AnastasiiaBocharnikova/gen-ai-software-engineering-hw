# FIRST Skill Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the FIRST testing skill into a practical, measurable guide that produces stronger changed-code tests and complete reports.

**Architecture:** Keep the assignment-required single Markdown skill and strengthen its contract through the existing pipeline structural tests. Validate the documentation change with a RED-GREEN cycle, the full test suite, and pipeline preflight.

**Tech Stack:** Markdown, Python 3 `unittest`, Codex agent contracts.

## Global Constraints

- Modify only the FIRST skill and its structural contract test.
- Keep the skill in English and in `homework-4/skills/unit-tests-FIRST.md`.
- Keep the expanded skill below 500 lines.
- Do not change application behavior, pipeline order, or agent model selection.
- Preserve unrelated working-tree changes.

---

### Task 1: Strengthen the FIRST skill contract

**Files:**
- Modify: `homework-4/tests/test_pipeline_contract.py`
- Modify: `homework-4/skills/unit-tests-FIRST.md`

**Interfaces:**
- Consumes: the Unit Test Generator's changed-code scope and `fix-summary.md`.
- Produces: measurable FIRST criteria, risk matrix, workflow, examples, anti-patterns, report template, and completion gates.

- [ ] **Step 1: Add a failing structural test**

Extend `SkillDefinitionTests` with assertions requiring:

```python
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
```

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```bash
python3 -m unittest \
  tests.test_pipeline_contract.SkillDefinitionTests.test_first_skill_is_actionable_and_measurable -v
```

Expected: FAIL because the current 25-line skill lacks the required sections.

- [ ] **Step 3: Expand the skill**

Write the approved maximal design into `unit-tests-FIRST.md`: measurable criteria, risk-selection matrix, ordered workflow, one complete good Python example, one bad example with analysis, anti-pattern corrections, exact report template, completion checklist, and stop conditions.

- [ ] **Step 4: Run focused and full verification**

Run:

```bash
python3 -m unittest \
  tests.test_pipeline_contract.SkillDefinitionTests -v
python3 -m unittest discover -s tests -v
./run-pipeline.sh --validate-only
git diff --check
```

Expected: all commands exit 0 and the suite reports 27 passing tests.

- [ ] **Step 5: Commit the review fix**

```bash
git add homework-4/skills/unit-tests-FIRST.md \
  homework-4/tests/test_pipeline_contract.py \
  homework-4/docs/superpowers/plans/2026-08-04-first-skill-expansion.md
git commit -m "Expand FIRST unit testing skill"
```
