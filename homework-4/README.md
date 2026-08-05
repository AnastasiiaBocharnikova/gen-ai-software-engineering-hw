# Homework 4 — Multi-Agent Bug-Fix Pipeline

## Author

**Anastasiia Bocharnikova**  
AI-Assisted Development Course

## Overview

This submission implements a real Codex multi-agent workflow around a small
Python order-receipt CLI. One command validates the repository and starts an
orchestrator that delegates research, verification, planning, fixing, security
review, and unit-test generation to specialized custom subagents.

The final application is safe and fully tested. The three seeded before-state
issues remain documented in `context/bugs/001-order-receipt/bug-context.md` so
the pipeline is reproducible without submitting vulnerable runnable code.

## Features

- Four required agents plus supporting Researcher, Planner, and Orchestrator.
- Strict sequential handoffs through checked-in Markdown reports.
- Automatic use of research-quality and FIRST skills.
- Explicit model and reasoning selection for every agent.
- One-command real Codex execution and a free `--validate-only` mode.
- Dependency-free Python CLI with validation, safe rendering, and friendly
  errors.
- Unit, negative, integration, pipeline-contract, and documentation tests.

## Tech Stack

- Codex CLI custom agents in repository-scoped TOML profiles
- Bash pipeline entry point
- Python 3.9+ standard library
- `unittest`
- `coverage.py` for coverage measurement
- Markdown and Mermaid documentation

## Agent Models

| Agent | Model | Reasoning | Rationale |
| --- | --- | --- | --- |
| Bug Researcher | `gpt-5.6-terra` | high | Efficient repository inspection with enough reasoning for evidence gathering. |
| Bug Research Verifier | `gpt-5.6-sol` | high | Stronger reasoning for exhaustive fact-checking and quality grading. |
| Bug Planner | `gpt-5.6-sol` | high | Strong planning model for exact, test-first implementation steps. |
| Bug Fixer | `gpt-5.6-terra` | high | Balanced implementation speed and code-change reliability. |
| Security Verifier | `gpt-5.6-sol` | xhigh | Deep reasoning for vulnerability review and severity decisions. |
| Unit Test Generator | `gpt-5.6-terra` | medium | Fast, bounded generation using the existing framework. |
| Pipeline Orchestrator | `gpt-5.6-sol` | high | Reliable multi-step delegation and artifact validation. |

## Setup

Requirements: Python 3.9+, Codex CLI authenticated for a real pipeline run, and
optionally `coverage.py`.

```bash
cd homework-4
python3 -m pip install -r requirements.txt
```

The application itself has no third-party runtime dependency. Installing the
requirements adds only the coverage tool.

## Run the Pipeline

From `homework-4`:

```bash
./run-pipeline.sh
```

This performs local validation, then uses one `codex exec` invocation to start
the custom `pipeline_orchestrator`, which delegates every stage in order.

Validate files and tests without starting paid/model work:

```bash
./run-pipeline.sh --validate-only
```

## Run the Application

```bash
PYTHONPATH=src python3 -m order_receipt.cli \
  --customer "Ada & Co" \
  --price 19.99 \
  --quantity 2 \
  --discount 10
```

Expected result:

```text
Customer: Ada &amp; Co
Total: $35.98
```

## Run Tests

```bash
python3 -m unittest discover -s tests -v
```

Focused application tests:

```bash
python3 -m unittest tests.test_order tests.test_cli -v
```

## Coverage

```bash
python3 -m coverage run --source=src -m unittest discover -s tests
python3 -m coverage report --fail-under=86
```

The submission target is greater than 85% source coverage.

## Project Structure

```text
homework-4/
├── agents/                    # Human-readable agent contracts
├── context/bugs/001-order-receipt/
│   ├── research/              # Research and verification
│   ├── implementation-plan.md
│   ├── fix-summary.md
│   ├── security-report.md
│   └── test-report.md
├── docs/                      # Architecture, testing, AI use, screenshots
├── scripts/validate_pipeline.py
├── skills/                    # Research quality and FIRST
├── src/order_receipt/         # Fixed CLI application
├── tests/                     # Unit, integration, and contract tests
├── run-pipeline.sh
└── requirements.txt
```

Executable agent profiles are in the repository root `.codex/agents/`, where
Codex discovers project-scoped custom agents.

The app accepts command-line values rather than files, so separate
`sample_data/valid` and `sample_data/invalid` fixtures are not applicable.
Repeatable valid and invalid inputs are encoded directly in `tests/`.

## Pipeline Artifacts

The completed pipeline output is under
`context/bugs/001-order-receipt/`. It includes verified research, an
implementation plan, fix summary, security report, and generated-test report.
Every report points to real source or test lines.

## Screenshots

- `docs/screenshots/pipeline-run.png`
- `docs/screenshots/fixes.png`
- `docs/screenshots/security-scan.png`
- `docs/screenshots/unit-tests.png`

See [HOWTORUN.md](HOWTORUN.md) for step-by-step verification.
