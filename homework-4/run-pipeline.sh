#!/usr/bin/env bash
set -euo pipefail

homework_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repository_dir="$(cd "${homework_dir}/.." && pwd)"

python3 "${homework_dir}/scripts/validate_pipeline.py"

if [[ "${1:-}" == "--validate-only" ]]; then
  exit 0
fi

if [[ $# -gt 0 ]]; then
  echo "Usage: ./run-pipeline.sh [--validate-only]" >&2
  exit 2
fi

if ! command -v codex >/dev/null 2>&1; then
  echo "Codex CLI is required. Install it or run --validate-only." >&2
  exit 127
fi

codex exec --cd "${repository_dir}" --sandbox workspace-write \
  "Spawn the custom agent pipeline_orchestrator for homework-4. Wait for it to run every required stage, then return its verified final status. Do not perform the specialist stages in this parent session."
