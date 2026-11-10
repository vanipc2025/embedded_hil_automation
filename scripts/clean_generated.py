#!/usr/bin/env python3
"""Safely remove known generated files before preparing a Git commit.

Default: dry-run preview. Add --apply to actually delete.
Does NOT delete .git, firmware source, build directories, or user files.
Examples:
    python scripts/clean_generated.py
    python scripts/clean_generated.py --apply

The cleanup targets are deliberately fixed and constrained to the project root.
Generated reports are local evidence: archive them elsewhere before cleanup.
"""
import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
REPORT_NAMES = {"log.html", "report.html", "output.xml", "xunit.xml"}
CACHE_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
EXCLUDED = {".git", ".venv", "venv", "build", ".nrfconnect"}


def collect():
    targets = set()
    results = ROOT / "results"
    if results.exists():
        targets.add(results)
    for folder in (ROOT, ROOT / "tests", ROOT / "libraries", ROOT / "scripts"):
        if folder.is_dir():
            for name in REPORT_NAMES:
                p = folder / name
                if p.is_file():
                    targets.add(p)
    for folder in ROOT.rglob("*"):
        if any(part in EXCLUDED for part in folder.relative_to(ROOT).parts):
            continue
        if folder.is_dir() and folder.name in CACHE_DIRS:
            targets.add(folder)
        elif folder.is_file() and folder.suffix in {".pyc", ".pyo"}:
            targets.add(folder)
    # Avoid trying to delete a file after deleting its parent directory.
    return sorted((p for p in targets if not any(parent in targets for parent in p.parents)), key=str)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Actually remove targets; without this only preview")
    args = parser.parse_args()
    targets = collect()
    print("CLEANUP " + ("APPLY" if args.apply else "PREVIEW (no deletion)"))
    if not targets:
        print("Nothing to clean.")
    for p in targets:
        print("  " + str(p.relative_to(ROOT)))
        if args.apply:
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()
    if not args.apply:
        print("\nTo remove listed files: python scripts/clean_generated.py --apply")
    print("Firmware build folders and .git are never removed by this script.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
