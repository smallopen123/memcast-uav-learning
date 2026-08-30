"""Check that every relative Markdown link points to an existing repository file."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {".git", ".venv", "__pycache__", ".pytest_cache"}
LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "#")


def markdown_sources(document: Path) -> list[str]:
    if document.suffix == ".md":
        return [document.read_text(encoding="utf-8")]
    notebook = json.loads(document.read_text(encoding="utf-8"))
    return [
        "".join(cell.get("source", []))
        for cell in notebook.get("cells", [])
        if cell.get("cell_type") == "markdown"
    ]


def relative_targets(document: Path) -> list[Path]:
    targets: list[Path] = []
    for text in markdown_sources(document):
        for match in LINK_PATTERN.finditer(text):
            raw_target = match.group(1).strip()
            if raw_target.startswith(EXTERNAL_PREFIXES):
                continue
            target_without_anchor = raw_target.split("#", maxsplit=1)[0].strip()
            if not target_without_anchor:
                continue
            if target_without_anchor.startswith("<") and target_without_anchor.endswith(">"):
                target_without_anchor = target_without_anchor[1:-1]
            targets.append((document.parent / target_without_anchor).resolve())
    return targets


def main() -> None:
    documents = []
    for suffix in ("*.md", "*.ipynb"):
        documents.extend(
            path
            for path in ROOT.rglob(suffix)
            if not any(part in SKIP_PARTS for part in path.parts)
        )
    missing: list[str] = []
    checked = 0
    for document in documents:
        for target in relative_targets(document):
            checked += 1
            if not target.exists():
                missing.append(f"{document.relative_to(ROOT)} -> {target}")
    if missing:
        raise SystemExit("Broken relative Markdown links:\n" + "\n".join(missing))
    print(f"Markdown link check passed: {checked} relative links across {len(documents)} files.")


if __name__ == "__main__":
    main()
