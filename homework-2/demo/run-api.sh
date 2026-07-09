#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

PYTHONPATH=src .venv/bin/uvicorn support_tickets.main:app --host 127.0.0.1 --port 3000
