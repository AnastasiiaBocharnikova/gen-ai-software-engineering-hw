# Four-Agent Pipeline Design

## Goal

Build a demonstrable Codex multi-agent pipeline for a small Python application.
One command must start every stage in the required order, load the relevant
skills, and produce verified research, fix, security, and unit-test reports.

## Scope

The pipeline contains the four required agents:

1. Bug Research Verifier
2. Bug Fixer
3. Security Vulnerabilities Verifier
4. Unit Test Generator

It also contains two supporting agents required by the documented run order:

1. Bug Researcher
2. Bug Planner

An orchestrator coordinates these agents. The unrelated summarizer and summary
orchestrator files currently in the homework folder and root Codex configuration
will be removed.

## Application

The sample application is a dependency-light Python CLI for calculating a
discounted order total and producing a safe customer-facing receipt.

The documented initial state contains at least:

- an incorrect percentage calculation;
- incorrect handling of invalid or negative quantities;
- unsafe rendering of untrusted customer input.

The submitted application contains the corrected implementation. Before-state
examples and bug context preserve evidence of what the pipeline investigated and
fixed without leaving a vulnerable runnable application in the final branch.

## Agent Architecture

Repository-facing Markdown definitions live in `homework-4/agents/`. Executable
Codex profiles live in the repository root `.codex/agents/`, because that is
where Codex discovers custom agents.

Each agent definition declares an explicit model and reasoning level:

- stronger reasoning for research verification, planning, and security review;
- a balanced model for research and fixes;
- a faster model for focused unit-test generation.

The README explains each selection. Agent prompts restrict every role to its
assigned inputs, outputs, and permissions.

## Pipeline Execution

`homework-4/run-pipeline.sh` is the public entry point. It validates that the
Codex CLI is available, then starts the orchestrator with the homework directory
as its scope.

The orchestrator delegates sequentially:

1. Bug Researcher writes `codebase-research.md`.
2. Research Verifier checks all source references and writes
   `verified-research.md` using the research-quality skill.
3. Bug Planner writes `implementation-plan.md` from verified research.
4. Bug Fixer applies the plan, runs tests after changes, and writes
   `fix-summary.md`.
5. Security Verifier reviews changed code without editing it and writes
   `security-report.md`.
6. Unit Test Generator loads the FIRST skill, adds tests only for changed
   behavior, runs them, and writes `test-report.md`.

A checked-in completed artifact set demonstrates the expected output of a
successful run. Re-running the pipeline must be safe when the fixes are already
present: agents record that the target state is satisfied instead of undoing
fixes or inventing changes.

## Skills

`research-quality-measurement.md` defines objective quality levels and the
required evidence for each level. The Research Verifier must cite the applied
level and reasoning in its report.

`unit-tests-FIRST.md` defines Fast, Independent, Repeatable, Self-validating, and
Timely criteria. The Unit Test Generator must assess generated tests against
each criterion in its report.

## Artifacts and Data Flow

All bug-specific inputs and reports live under one stable context directory:

`homework-4/context/bugs/001-order-receipt/`

Each stage reads source code plus the preceding report. Reports use real
repository-relative `file:line` references. The security agent reports findings
only and never edits code.

## Error Handling

The shell entry point exits with a clear message when Codex is unavailable or an
agent run fails. The orchestrator stops dependent work when research
verification or fixing fails. Reports explicitly record failed commands,
unresolved findings, and manual verification steps rather than claiming
success.

The application validates numeric and text input and emits actionable CLI
errors without exposing stack traces for expected user mistakes.

## Testing

Testing uses Python's standard-library `unittest` framework to avoid installation
friction.

Coverage includes:

- unit tests for calculations, validation, and safe receipt rendering;
- negative tests for malformed and hostile input;
- CLI integration tests;
- structural tests for required agents, explicit models, skills, run order, and
  report sections;
- a coverage run targeting more than 85 percent when the available coverage
  tool is installed.

Before completion, the app run command, full test suite, pipeline validation,
and coverage command will be executed. Representative terminal evidence will be
saved in `docs/screenshots/`.

## Documentation

The homework includes:

- `README.md` with author information, overview, features, model rationale,
  setup, run, test, coverage, structure, artifacts, and screenshots;
- `HOWTORUN.md`;
- architecture, testing, and AI-usage documentation;
- a detailed PR summary with committed screenshot links;
- screenshots for the pipeline, fixes, security report, and unit tests.

Documentation and artifact examples must match the final implementation and
commands exactly.

## Acceptance Criteria

- The four required agents and two supporting agents are present.
- Every agent has an explicit appropriate model selection.
- One command launches the ordered Codex workflow and loads related skills.
- Both required skills exist and are referenced by the correct agents.
- The fixed Python application runs successfully.
- Tests pass and meaningful coverage exceeds 85 percent.
- All required reports contain the specified sections and real references.
- Documentation and screenshots satisfy `HOMEWORK_STANDARDS.md` and root
  `AGENTS.md`.
- No unrelated summarizer workflow remains in the homework submission.
