# How to Run Homework 4

## Prerequisites

- Python 3.9 or newer
- Codex CLI with an authenticated session for the real multi-agent run
- A terminal opened at the repository root

## Validate Without Starting Agents

```bash
cd homework-4
./run-pipeline.sh --validate-only
```

This checks required profiles and skills, then runs the complete test suite. It
does not call a model.

## Run the Complete Pipeline

```bash
cd homework-4
./run-pipeline.sh
```

The script validates first and then starts one non-interactive Codex parent. The
parent spawns the Pipeline Orchestrator, which runs all six work roles
sequentially. A failed prerequisite stops later stages.

## Run the Application

```bash
cd homework-4
PYTHONPATH=src python3 -m order_receipt.cli \
  --customer "Ada & Co" --price 19.99 --quantity 2 --discount 10
```

The expected total is `$35.98`; the ampersand is safely encoded.

## Run Tests and Coverage

```bash
cd homework-4
python3 -m pip install -r requirements.txt
python3 -m unittest discover -s tests -v
python3 -m coverage run --source=src -m unittest discover -s tests
python3 -m coverage report --fail-under=86
```

Review generated reports under
`context/bugs/001-order-receipt/` and screenshots under `docs/screenshots/`.
