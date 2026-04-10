# tests/update_golden.py
"""Helper to refresh golden files from current pipeline output.

Usage: python -m tests.update_golden olmo-3
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

GOLDEN_DIR = Path(__file__).parent / "golden"
# Map slug to current output path (v2.1 P2 layout)
PAPER_PATHS = {
    "olmo-3": "papers/llm/pretraining/olmo-3/olmo-3.md",
}
# Fallback: v2 flat layout
PAPER_PATHS_V2 = {
    "olmo-3": "papers/llm/pretraining/olmo-3.md",
}


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: python -m tests.update_golden <slug>")
        print(f"Available: {', '.join(PAPER_PATHS)}")
        sys.exit(1)

    slug = sys.argv[1]
    source = Path(PAPER_PATHS.get(slug, ""))
    if not source.exists():
        source = Path(PAPER_PATHS_V2.get(slug, ""))
    if not source.exists():
        print(f"Error: no output found for {slug}")
        sys.exit(1)

    dest = GOLDEN_DIR / f"{slug}.md"
    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
    print(f"Updated golden: {dest}")


if __name__ == "__main__":
    main()
