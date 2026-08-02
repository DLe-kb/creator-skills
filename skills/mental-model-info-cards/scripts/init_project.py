#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = SKILL_ROOT / "assets" / "template"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize a six-card knowledge-card project.")
    parser.add_argument("target", type=Path, help="Project directory to create or populate")
    parser.add_argument("--force", action="store_true", help="Allow copying into a non-empty directory")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    target = args.target.expanduser().resolve()

    if target.exists() and any(target.iterdir()) and not args.force:
        raise SystemExit(f"Refusing to overwrite non-empty directory: {target}")

    target.mkdir(parents=True, exist_ok=True)
    shutil.copytree(TEMPLATE_ROOT, target, dirs_exist_ok=True)
    (target / "output").mkdir(exist_ok=True)
    (target / "archive").mkdir(exist_ok=True)
    print(f"Initialized mental-model info-card project at {target}")


if __name__ == "__main__":
    main()
