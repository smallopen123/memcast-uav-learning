"""Validate and execute every tutorial notebook without modifying committed files."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = ROOT / "notebooks"
RUNTIME_DIR = ROOT / ".notebook_runtime"


def main() -> None:
    RUNTIME_DIR.mkdir(exist_ok=True)
    tempfile.tempdir = str(RUNTIME_DIR)
    os.environ["IPYTHONDIR"] = str(RUNTIME_DIR / "ipython")
    os.environ["JUPYTER_RUNTIME_DIR"] = str(RUNTIME_DIR / "jupyter")
    os.environ["PYTHONNOUSERSITE"] = "1"

    paths = sorted(NOTEBOOK_DIR.glob("[0-9][0-9]_*.ipynb"))
    if len(paths) != 9:
        raise SystemExit(f"Expected 9 lesson notebooks, found {len(paths)}")

    for path in paths:
        document = nbformat.read(path, as_version=4)
        nbformat.validate(document)
        client = NotebookClient(
            document,
            timeout=120,
            kernel_name="python3",
            resources={"metadata": {"path": str(ROOT)}},
        )
        client.execute()
        print(f"executed {path.relative_to(ROOT)} ({len(document.cells)} cells)")


if __name__ == "__main__":
    main()
