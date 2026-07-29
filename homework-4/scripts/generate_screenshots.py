#!/usr/bin/env python3
"""Render reproducible terminal-style screenshots from verified local output."""

from pathlib import Path
import subprocess
import textwrap

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "screenshots"
CONTEXT = ROOT / "context" / "bugs" / "001-order-receipt"
PYTHON = "python3"


def run(command: list[str]) -> str:
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    return result.stdout


def excerpt(path: Path, heading: str) -> str:
    content = path.read_text(encoding="utf-8")
    return f"$ view {path.relative_to(ROOT)}\n\n{heading}\n\n{content}"


def font(size: int) -> ImageFont.FreeTypeFont:
    candidates = (
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Monaco.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    )
    for candidate in candidates:
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def render(filename: str, title: str, body: str) -> None:
    image = Image.new("RGB", (1500, 980), "#111827")
    draw = ImageDraw.Draw(image)
    title_font = font(29)
    body_font = font(19)

    draw.rounded_rectangle((35, 30, 1465, 950), radius=18, fill="#0b1220")
    draw.ellipse((65, 57, 83, 75), fill="#ff5f57")
    draw.ellipse((94, 57, 112, 75), fill="#febc2e")
    draw.ellipse((123, 57, 141, 75), fill="#28c840")
    draw.text((175, 50), title, fill="#f8fafc", font=title_font)
    draw.line((65, 98, 1435, 98), fill="#334155", width=2)

    wrapped: list[str] = []
    for line in body.splitlines():
        wrapped.extend(textwrap.wrap(line, width=105) or [""])

    y = 125
    for line in wrapped[:37]:
        color = "#86efac" if any(
            marker in line for marker in ("PASS", "OK", "COMPLETE", "passed")
        ) else "#dbeafe"
        draw.text((70, y), line, fill=color, font=body_font)
        y += 22

    OUTPUT.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT / filename, format="PNG", optimize=True)


def main() -> None:
    preflight = run(
        [
            PYTHON,
            "-m",
            "unittest",
            "tests.test_order",
            "tests.test_cli",
            "tests.test_pipeline_contract.AgentDefinitionTests",
            "tests.test_pipeline_contract.ExecutablePipelineTests",
            "tests.test_pipeline_contract.PipelineArtifactTests",
            "tests.test_pipeline_contract.SkillDefinitionTests",
            "-v",
        ]
    )
    tests = preflight
    render(
        "pipeline-run.png",
        "Homework 4 — Pipeline Preflight",
        "$ python3 -m unittest [application and pipeline contracts]\n\n" + preflight,
    )
    render(
        "fixes.png",
        "Homework 4 — Applied Fixes",
        excerpt(CONTEXT / "fix-summary.md", "Verified fix artifact"),
    )
    render(
        "security-scan.png",
        "Homework 4 — Security Verification",
        excerpt(CONTEXT / "security-report.md", "Read-only security artifact"),
    )
    render(
        "unit-tests.png",
        "Homework 4 — Unit Test Results",
        "$ python3 -m unittest [application and pipeline contracts] -v\n\n" + tests,
    )
    pipeline = run(["./run-pipeline.sh", "--validate-only"])
    render(
        "pipeline-run.png",
        "Homework 4 — Pipeline Validation",
        "$ ./run-pipeline.sh --validate-only\n\n" + pipeline,
    )
    print(f"Created 4 screenshots in {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
