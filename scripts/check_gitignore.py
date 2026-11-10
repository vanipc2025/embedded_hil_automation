#!/usr/bin/env python3
"""Check .gitignore behavior AND whether generated artifacts are tracked.

Run before git add/commit: python scripts/check_gitignore.py
Requires Git installed. Works before git init for ignore rules; tracking
inspection is available after git init. This script does not modify Git.
"""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
# These are representative files, including build and report locations.
SAMPLES = [
    "results/phase1/log.html", "results/phase1/report.html",
    "results/phase1/output.xml", "results/phase1/validation_summary.json",
    "firmware/nordic_zephyr/build/zephyr/zephyr.elf",
    "firmware/nordic_zephyr/build-debug/zephyr/zephyr.elf",
    "libraries/__pycache__/DeviceLibrary.cpython-314.pyc",
    ".venv/Lib/site-packages/example.py", ".env",
]


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=False)


def main():
    if not (ROOT / ".gitignore").is_file():
        print("FAIL: project root .gitignore missing")
        return 1
    if not shutil.which("git"):
        print("FAIL: Git executable unavailable; install Git for Windows")
        return 1
    ok = True
    repository = git("rev-parse", "--show-toplevel")
    # Git check-ignore requires a repository. For an uninitialized project,
    # use a disposable Git metadata directory without modifying the project.
    temp = tempfile.TemporaryDirectory() if repository.returncode != 0 else None
    if temp:
        init = subprocess.run(["git", "init", "--bare", "--quiet", temp.name], capture_output=True, text=True)
        if init.returncode:
            print("FAIL: unable to create temporary Git context:", init.stderr)
            return 1
    print("GITIGNORE RULE CHECK")
    for path in SAMPLES:
        if temp:
            result = subprocess.run(["git", "--git-dir", temp.name, "--work-tree", str(ROOT),
                                     "check-ignore", "--no-index", "-v", "--", path],
                                    cwd=ROOT, capture_output=True, text=True)
        else:
            result = git("check-ignore", "--no-index", "-v", "--", path)
        passed = result.returncode == 0
        print(f"[{'PASS' if passed else 'FAIL'}] {path}" + (f" ({result.stdout.strip()})" if passed else ""))
        ok &= passed
    if repository.returncode != 0:
        print("[INFO] No Git repository yet: cannot inspect tracked files. Run git init, then rerun this checker.")
        return 0 if ok else 1
    if Path(repository.stdout.strip()).resolve() != ROOT.resolve():
        print("FAIL: Git repository root differs from project root; inspect nested checkout")
        return 1
    tracked = git("ls-files", "-z")
    if tracked.returncode:
        print("FAIL: could not inspect Git tracked files:", tracked.stderr.strip())
        return 1
    paths = [p for p in tracked.stdout.split("\0") if p]
    generated = []
    for path in paths:
        parts = Path(path).parts
        name = Path(path).name
        if ("results" in parts or "__pycache__" in parts or ".venv" in parts
                or name in {"log.html", "report.html", "output.xml", "xunit.xml"}
                or ("firmware" in parts and any(p == "build" or p.startswith("build-") for p in parts))):
            generated.append(path)
    if generated:
        ok = False
        print("[FAIL] Already tracked generated files (ignore rules cannot untrack them):")
        for path in generated:
            print("   " + path)
        print("Remove from Git index, preserving local copies: git rm -r --cached -- results/")
        print("For other listed files, use: git rm --cached -- <path>")
    else:
        print("[PASS] No generated artifacts tracked by Git")
    print("\nRESULT:", "PASS — safe to review git status" if ok else "FAIL — resolve issues before commit")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
