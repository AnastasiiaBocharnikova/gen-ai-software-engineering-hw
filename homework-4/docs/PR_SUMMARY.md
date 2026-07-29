# Pull Request Summary

## What Changed

- Added four required agents, two supporting agents, and a sequential pipeline
  orchestrator.
- Added executable project-scoped Codex profiles with explicit model and
  reasoning selections.
- Added research-quality and FIRST skills.
- Added a fixed Python order-receipt CLI with three documented seeded issues.
- Added verified research, implementation, fix, security, and unit-test reports.
- Added unit, negative, integration, pipeline-contract, and documentation tests.
- Added complete run, architecture, testing, AI-usage, and screenshot evidence.

## Why

The assignment requires a concrete application and a one-command pipeline that
loads specialized roles and skills automatically. The submitted source stays
safe while the bug context preserves an auditable before-state.

## Verification

```bash
cd homework-4
./run-pipeline.sh --validate-only
PYTHONPATH=src python3 -m order_receipt.cli \
  --customer "Ada & Co" --price 19.99 --quantity 2 --discount 10
python3 -m coverage run --source=src -m unittest discover -s tests
python3 -m coverage report --fail-under=86
```

## Known Limitations

A real `./run-pipeline.sh` execution requires an installed, authenticated Codex
CLI and consumes model usage. `--validate-only` is deterministic and free.

## Screenshots

<img width="1000" alt="pipeline run" src="https://github.com/AnastasiiaBocharnikova/gen-ai-software-engineering-hw/blob/homework-4-submission/homework-4/docs/screenshots/pipeline-run.png?raw=true" />

<img width="1000" alt="fix summary" src="https://github.com/AnastasiiaBocharnikova/gen-ai-software-engineering-hw/blob/homework-4-submission/homework-4/docs/screenshots/fixes.png?raw=true" />

<img width="1000" alt="security scan" src="https://github.com/AnastasiiaBocharnikova/gen-ai-software-engineering-hw/blob/homework-4-submission/homework-4/docs/screenshots/security-scan.png?raw=true" />

<img width="1000" alt="unit tests" src="https://github.com/AnastasiiaBocharnikova/gen-ai-software-engineering-hw/blob/homework-4-submission/homework-4/docs/screenshots/unit-tests.png?raw=true" />
