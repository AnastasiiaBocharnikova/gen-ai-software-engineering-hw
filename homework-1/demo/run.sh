#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
PYTHONPATH=src uvicorn banking_api.main:app --reload --host 127.0.0.1 --port 3000
