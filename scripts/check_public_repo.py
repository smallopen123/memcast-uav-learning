"""Conservative pre-publication scan for common secret and local-path patterns."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {".git", ".venv", "__pycache__", ".pytest_cache"}
TEXT_SUFFIXES = {".py", ".md", ".toml", ".yml", ".yaml", ".cff", ".txt", ".example"}
PATTERNS = {
    "possible API key": re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    "Windows user path": re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}


def main() -> None:
    findings: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in SKIP_PARTS for part in path.parts):
            continue
        if path.suffix not in TEXT_SUFFIXES and path.name not in {"LICENSE", ".gitignore"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for label, pattern in PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{path.relative_to(ROOT)}: {label}")
    if findings:
        raise SystemExit("Pre-publication scan failed:\n" + "\n".join(findings))
    print("Pre-publication scan passed: no common secrets or personal absolute paths found.")


if __name__ == "__main__":
    main()

