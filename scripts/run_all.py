#!/usr/bin/env python3
"""Single entry point for Phase 1 validation on Windows or another host.

Run from any directory:
    python scripts/run_all.py --port COM3
    python scripts/run_all.py --sim-only
    python scripts/run_all.py --port COM3 --led-observation confirmed

WHY: Preflight is performed before running the simulator and HIL suites. The
existing runner creates a combined log.html/report.html; no duplicate test
logic is maintained here. An already-flashed board is required for HIL.
VS Code and Nordic SDK are required only for the documented build workflow.
"""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def invoke(*args):
    print("\n$ " + " ".join(map(str, args)), flush=True)
    return subprocess.run([sys.executable, *map(str, args)], cwd=ROOT, check=False).returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", help="Serial port of already-flashed board, e.g. COM3")
    parser.add_argument("--sim-only", action="store_true", help="No DK required")
    parser.add_argument("--board", default="nrf52840dk", choices=["nrf52840dk"])
    parser.add_argument("--outputdir", default="results/phase1")
    parser.add_argument("--led-observation", choices=["confirmed", "not-confirmed", "not-observed"], default="not-observed")
    parser.add_argument("--check-development", action="store_true", help="Also check documented VS Code/NCS development environment (optional for testing flashed hardware)")
    args = parser.parse_args()
    if not args.sim_only and not args.port:
        parser.error("--port COM3 required, or select --sim-only")
    checks = [("simulator", [])]
    if args.check_development:
        checks.append(("development", []))
    if not args.sim_only:
        checks.append(("hardware", ["--port", args.port]))
    for mode, extra in checks:
        rc = invoke(ROOT / "scripts/check_environment.py", "--mode", mode, *extra)
        if rc:
            print(f"\n{'=' * 62}")
            print("PHASE 1 VALIDATION - FINAL SUMMARY")
            print(f"OVERALL    FAIL - {mode} preflight failed")
            print("SIMULATOR  NOT RUN")
            print("HARDWARE   NOT RUN")
            print("TOTAL       0 tests | 0 PASS | 0 FAIL | 0 SKIP")
            print("Fix readiness checks above, then rerun the command.")
            print(f"{'=' * 62}", flush=True)
            return rc
    command = [ROOT / "scripts/run_validation.py", "--board", args.board, "--outputdir", args.outputdir]
    if args.sim_only:
        command.append("--sim-only")
    else:
        command.extend(["--port", args.port, "--led-observation", args.led_observation])
    return invoke(*command)


if __name__ == "__main__":
    raise SystemExit(main())
