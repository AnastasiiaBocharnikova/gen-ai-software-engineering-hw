# Four-Agent Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a runnable Codex pipeline with four required agents, two supporting agents, a fixed Python CLI, generated reports, tests, documentation, and screenshots.

**Architecture:** A shell entry point starts one non-interactive Codex session, which delegates to a project-scoped orchestrator custom agent. The orchestrator calls six narrow custom agents sequentially and passes work through Markdown artifacts under one bug context directory. The sample Python package stays dependency-free and separates calculation, validation, receipt rendering, and CLI concerns.

**Tech Stack:** Codex CLI custom agents (TOML), Markdown skills and reports, Bash, Python 3.11+ standard library, `unittest`, `coverage.py` when available.

## Global Constraints

- Work only inside `homework-4/` except project-scoped Codex configuration under `.codex/`.
- Preserve unrelated changes outside homework 4.
- The public pipeline command is `./run-pipeline.sh`.
- Required order: Researcher → Research Verifier → Planner → Fixer → Security Verifier → Unit Test Generator.
- All agent model choices must be explicit and documented.
- Final meaningful test coverage must exceed 85 percent.
- The final runnable application must be fixed; before-state evidence belongs in bug context documentation.

---

## File Map

- `homework-4/src/order_receipt/`: fixed application package.
- `homework-4/tests/`: application, CLI, and submission-contract tests.
- `homework-4/agents/`: human-readable agent assignment files.
- `.codex/agents/`: executable project-scoped custom-agent profiles.
- `.codex/config.toml`: multi-agent limit and project configuration.
- `homework-4/skills/`: research-quality and FIRST definitions loaded by agents.
- `homework-4/context/bugs/001-order-receipt/`: seeded bug context and all pipeline handoff reports.
- `homework-4/scripts/validate_pipeline.py`: deterministic validation used before paid/non-interactive agent execution.
- `homework-4/run-pipeline.sh`: single pipeline entry point.
- `homework-4/docs/`: architecture, testing, AI usage, PR summary, and screenshots.

### Task 1: Application behavior and regression tests

**Files:**
- Create: `homework-4/tests/test_order.py`
- Create: `homework-4/tests/test_cli.py`
- Create: `homework-4/src/order_receipt/__init__.py`
- Create: `homework-4/src/order_receipt/order.py`
- Create: `homework-4/src/order_receipt/cli.py`

**Interfaces:**
- Produces: `calculate_total(unit_price: Decimal, quantity: int, discount_percent: Decimal) -> Decimal`
- Produces: `safe_customer_name(value: str) -> str`
- Produces: `render_receipt(customer_name: str, total: Decimal) -> str`
- Produces: `main(argv: Sequence[str] | None = None) -> int`

- [ ] Write failing unit tests for correct percentage calculation, currency rounding, rejected zero/negative quantities, discount bounds, and escaped hostile customer names.
- [ ] Run `python3 -m unittest tests.test_order -v`; expect import failures because the package does not exist.
- [ ] Implement `order.py` with `Decimal`, `ROUND_HALF_UP`, explicit validation, and `html.escape`.
- [ ] Run `python3 -m unittest tests.test_order -v`; expect all unit tests to pass.
- [ ] Write failing CLI integration tests for a valid receipt and friendly invalid-input errors.
- [ ] Run `python3 -m unittest tests.test_cli -v`; expect failures because `cli.py` is missing.
- [ ] Implement `argparse` parsing and return codes in `cli.py`.
- [ ] Run `python3 -m unittest tests.test_cli -v`; expect all CLI tests to pass.
- [ ] Commit the focused application and regression tests.

### Task 2: Agent and skill contract

**Files:**
- Create: `homework-4/tests/test_pipeline_contract.py`
- Create: `homework-4/skills/research-quality-measurement.md`
- Create: `homework-4/skills/unit-tests-FIRST.md`
- Create: `homework-4/agents/bug-researcher.agent.md`
- Create: `homework-4/agents/research-verifier.agent.md`
- Create: `homework-4/agents/bug-planner.agent.md`
- Create: `homework-4/agents/bug-fixer.agent.md`
- Create: `homework-4/agents/security-verifier.agent.md`
- Create: `homework-4/agents/unit-test-generator.agent.md`
- Create: `homework-4/agents/pipeline-orchestrator.agent.md`

**Interfaces:**
- Research quality levels: `EXCELLENT`, `GOOD`, `NEEDS_IMPROVEMENT`, `UNRELIABLE`.
- FIRST checks: `Fast`, `Independent`, `Repeatable`, `Self-validating`, `Timely`.
- Every agent frontmatter contains `name`, `description`, and explicit `model`.

- [ ] Write structural tests that enumerate all required agent files, required frontmatter keys, skill references, report headings, and required run order.
- [ ] Run `python3 -m unittest tests.test_pipeline_contract -v`; expect missing-file failures.
- [ ] Create the two skills with objective criteria and required report usage.
- [ ] Create seven narrow Markdown agent definitions, including six work roles and the orchestrator, with exact inputs, outputs, stop conditions, and model choices.
- [ ] Run `python3 -m unittest tests.test_pipeline_contract -v`; expect the agent/skill portion to pass.
- [ ] Commit the agent contract and skills.

### Task 3: Executable Codex subagents and one-command runner

**Files:**
- Replace: `.codex/config.toml`
- Delete: `.codex/agents/summarizer.toml`
- Delete: `.codex/agents/summary-orchestrator.toml`
- Create: `.codex/agents/bug-researcher.toml`
- Create: `.codex/agents/research-verifier.toml`
- Create: `.codex/agents/bug-planner.toml`
- Create: `.codex/agents/bug-fixer.toml`
- Create: `.codex/agents/security-verifier.toml`
- Create: `.codex/agents/unit-test-generator.toml`
- Create: `.codex/agents/pipeline-orchestrator.toml`
- Create: `homework-4/scripts/validate_pipeline.py`
- Create: `homework-4/run-pipeline.sh`

**Interfaces:**
- `validate_pipeline.py` exits `0` only when configuration, inputs, skills, and tests are valid.
- `run-pipeline.sh` accepts `--validate-only`; normal mode runs validation and then one `codex exec` command.
- Normal execution tells the primary session to spawn `pipeline_orchestrator`, wait for it, and return its final status.

- [ ] Extend contract tests for seven executable TOML profiles, explicit `model` and `model_reasoning_effort`, safe sandbox modes, a single `codex exec`, and ordered orchestration.
- [ ] Run the contract tests; expect failures for missing executable profiles and runner.
- [ ] Add Codex profiles using `gpt-5.6-sol` for verification/planning/security and `gpt-5.6-terra` for bounded research/fixing/testing, with read-only sandboxes for non-editing roles.
- [ ] Add validation script that runs the complete `unittest` suite and checks required pipeline inputs.
- [ ] Add the strict Bash runner with repository-root resolution, Codex availability check, `--validate-only`, and `codex exec --sandbox workspace-write`.
- [ ] Run `./run-pipeline.sh --validate-only`; expect all validation and tests to pass.
- [ ] Commit executable multi-agent configuration and runner.

### Task 4: Seeded bug context and completed pipeline artifacts

**Files:**
- Create: `homework-4/context/bugs/001-order-receipt/bug-context.md`
- Create: `homework-4/context/bugs/001-order-receipt/research/codebase-research.md`
- Create: `homework-4/context/bugs/001-order-receipt/research/verified-research.md`
- Create: `homework-4/context/bugs/001-order-receipt/implementation-plan.md`
- Create: `homework-4/context/bugs/001-order-receipt/fix-summary.md`
- Create: `homework-4/context/bugs/001-order-receipt/security-report.md`
- Create: `homework-4/context/bugs/001-order-receipt/test-report.md`
- Delete: `homework-4/artifacts/`

**Interfaces:**
- Reports use repository-relative `file:line` references.
- Verification report headings: `Verification Summary`, `Verified Claims`, `Discrepancies Found`, `Research Quality Assessment`, `References`.
- Fix summary headings: `Changes Made`, `Overall Status`, `Manual Verification`, `References`.
- Security report findings include severity, reference, evidence, and remediation; it edits no source.
- Test report documents changed-code scope, FIRST assessment, command, and result.

- [ ] Extend contract tests to require every artifact and mandated section.
- [ ] Run contract tests; expect artifact failures.
- [ ] Record three seeded before-state defects with exact unsafe/corrected examples in `bug-context.md`.
- [ ] Write realistic completed handoff artifacts that agree with the final source and actual test commands.
- [ ] Verify every reported `file:line` reference against current numbered source.
- [ ] Run all tests; expect them to pass.
- [ ] Commit bug context and pipeline output artifacts.

### Task 5: Documentation and submission evidence

**Files:**
- Create: `homework-4/README.md`
- Create: `homework-4/HOWTORUN.md`
- Create: `homework-4/docs/ARCHITECTURE.md`
- Create: `homework-4/docs/TESTING_GUIDE.md`
- Create: `homework-4/docs/AI_USAGE.md`
- Create: `homework-4/docs/PR_SUMMARY.md`
- Create: `homework-4/docs/screenshots/pipeline-run.png`
- Create: `homework-4/docs/screenshots/fixes.png`
- Create: `homework-4/docs/screenshots/security-scan.png`
- Create: `homework-4/docs/screenshots/unit-tests.png`
- Create: `homework-4/requirements.txt`

**Interfaces:**
- README includes author, overview, features, stack, model rationale, setup, run, test, coverage, structure, context, and screenshot locations.
- PR summary includes what changed, why, verification, limitations, and `<img>` tags pointing to committed GitHub paths with `?raw=true`.

- [ ] Extend contract tests for required documentation sections and four non-empty PNG files.
- [ ] Run contract tests; expect documentation/evidence failures.
- [ ] Write all documentation with exact verified commands and Mermaid architecture/test diagrams.
- [ ] Run the application and tests while capturing representative output.
- [ ] Render four legible terminal-style PNG screenshots from the captured real output.
- [ ] Run contract tests; expect all documentation checks to pass.
- [ ] Commit documentation and screenshots.

### Task 6: Final verification

**Files:**
- Modify only files whose verification reveals a concrete defect.

**Interfaces:**
- Full suite: `python3 -m unittest discover -s tests -v`
- App smoke test: `python3 -m order_receipt.cli --customer "Ada" --price 19.99 --quantity 2 --discount 10`
- Pipeline validation: `./run-pipeline.sh --validate-only`
- Coverage: `python3 -m coverage run --source=src -m unittest discover -s tests && python3 -m coverage report --fail-under=86`

- [ ] Run the full unit/integration/contract suite from `homework-4`.
- [ ] Run the application smoke test and verify a safe receipt with total `35.98`.
- [ ] Run the pipeline validation command.
- [ ] Run coverage and confirm at least 86 percent.
- [ ] Inspect every screenshot for readability and accurate content.
- [ ] Search for cache/build artifacts and remove only generated homework-4 files that should not be submitted.
- [ ] Review `git diff --check`, `git status`, and the final file list.
- [ ] Commit any verification fixes with a focused message.
