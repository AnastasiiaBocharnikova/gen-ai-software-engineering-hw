#!/usr/bin/env python3
"""Validate the pipeline contract and run the complete homework test suite."""

from pathlib import Path
import subprocess
import sys


HOMEWORK = Path(__file__).resolve().parents[1]
REPOSITORY = HOMEWORK.parent


def main() -> int:
    required = (
        HOMEWORK / "agents" / "pipeline-orchestrator.agent.md",
        HOMEWORK / "skills" / "research-quality-measurement.md",
        HOMEWORK / "skills" / "unit-tests-FIRST.md",
        REPOSITORY / ".codex" / "agents" / "pipeline-orchestrator.toml",
    )
    missing = [str(path.relative_to(REPOSITORY)) for path in required if not path.is_file()]
    if missing:
        print(f"Pipeline validation failed: missing {', '.join(missing)}", file=sys.stderr)
        return 1

    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=HOMEWORK,
        check=False,
    )
    if result.returncode:
        print("Pipeline validation failed: tests did not pass.", file=sys.stderr)
        return result.returncode

    print("Pipeline validation passed: configuration, skills, and tests are ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
