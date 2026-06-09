#!/usr/bin/env python3
"""Render every Mermaid diagram in the docs to standalone PNG + SVG images.

The Markdown is the single source of truth (GitHub renders ```mermaid blocks
inline). This script extracts each block, names it after its section heading, and
renders an image so the diagrams are also viewable offline / in a PDF / as a
supporting attachment. Re-run after editing any diagram.

Prereqs: Node + npx on PATH (uses @mermaid-js/mermaid-cli via `npx`, no global install).
Usage:   python tools/render_diagrams.py
Output:  docs/architecture/diagrams/<nn>-<slug>.png and .svg
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "architecture" / "diagrams"

# Source Markdown files, in gallery order.
SOURCES = [
    ROOT / "docs" / "architecture" / "uml.md",
    ROOT / "docs" / "architecture" / "overview.md",
    ROOT / "docs" / "security" / "threat-model.md",
    ROOT / "docs" / "planning" / "waterfall-gantt.md",
]

HEADING_RE = re.compile(r"^#{1,6}\s+(.*)")
OPEN_RE = re.compile(r"^```mermaid\s*$")
CLOSE_RE = re.compile(r"^```\s*$")


def slugify(text: str) -> str:
    text = re.sub(r"[`*_]", "", text)
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text or "diagram"


def extract(md_path: Path):
    """Yield (heading, mermaid_source) for each fenced mermaid block."""
    heading = md_path.stem
    lines = md_path.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        h = HEADING_RE.match(lines[i])
        if h:
            heading = h.group(1).strip()
        if OPEN_RE.match(lines[i]):
            body: list[str] = []
            i += 1
            while i < len(lines) and not CLOSE_RE.match(lines[i]):
                body.append(lines[i])
                i += 1
            yield heading, "\n".join(body)
        i += 1


def run_mmdc(inp: str, outp: str) -> None:
    cmd = (
        f'npx -y -p @mermaid-js/mermaid-cli mmdc -i "{inp}" -o "{outp}" '
        f"-b white -t default --scale 2"
    )
    subprocess.run(cmd, check=True, shell=True)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    n = 0
    for src in SOURCES:
        if not src.exists():
            print("skip (missing):", src)
            continue
        for heading, body in extract(src):
            n += 1
            name = f"{n:02d}-{slugify(heading)}"
            print(f"render {name}  <- {src.name} :: {heading}")
            with tempfile.NamedTemporaryFile(
                "w", suffix=".mmd", delete=False, encoding="utf-8"
            ) as f:
                f.write(body + "\n")
                tmp = f.name
            try:
                for ext in ("png", "svg"):
                    run_mmdc(tmp, str(OUT / f"{name}.{ext}"))
            finally:
                Path(tmp).unlink(missing_ok=True)
    print(f"\nDone: rendered {n} diagrams to {OUT.relative_to(ROOT).as_posix()}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
