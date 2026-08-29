from __future__ import annotations

import subprocess
import sys

LESSONS = [f"lessons.lesson_{index:02d}_{name}" for index, name in [
    (1, "windowing"),
    (2, "features"),
    (3, "retrieval"),
    (4, "memory"),
    (5, "reflection"),
    (6, "confidence"),
    (7, "end_to_end"),
    (8, "intent"),
]]


def main() -> None:
    for module in LESSONS:
        print(f"\n{'=' * 72}\n运行 {module}\n{'=' * 72}", flush=True)
        subprocess.run([sys.executable, "-m", module], check=True)


if __name__ == "__main__":
    main()
