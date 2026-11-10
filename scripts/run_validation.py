#!/usr/bin/env python3
"""Run Phase 1 simulator + nRF52840 DK tests and produce ONE combined Robot report.

WHY: Engineers should not need to remember several commands or manually merge
Robot Framework output.xml files. The runner keeps the simulation and hardware
runs isolated (different BACKEND settings), then combines their XML results.

WHAT THIS DOES NOT DO: Build/flash Zephyr firmware or independently sense light.
The board must already run compatible test firmware; LED illumination still
requires a human observer or a future optical/electrical measurement fixture.

Examples (from any working directory):
    python scripts/run_validation.py --port COM3
    python scripts/run_validation.py --sim-only
    python scripts/run_validation.py --port COM3 --board nrf52840dk
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def run_command(arguments):
    """Use this Python interpreter, so venv-installed Robot is found reliably."""
    print("\n$ " + " ".join(str(item) for item in arguments), flush=True)
    return subprocess.run(arguments, cwd=ROOT, check=False).returncode


def probe_hardware(port, board):
    """Fail early if the wrong board/firmware is connected to the serial port."""
    sys.path.insert(0, str(ROOT / "libraries"))
    from serial_adapter import SerialDevice

    device = SerialDevice(port)
    try:
        status = device.request("STATUS")
        identity = device.request("IDENTITY")
        capabilities = device.request("CAPABILITIES")
    finally:
        device.close()  # Critical on Windows: release COM port before Robot opens it.

    if status.get("status") != "READY":
        raise RuntimeError(f"Unexpected firmware status: {status}")
    if identity.get("board") != board or identity.get("backend") != "serial":
        raise RuntimeError(f"Wrong firmware/board for {board}: {identity}")
    if "gpio" not in capabilities.get("features", []):
        raise RuntimeError(f"GPIO capability not advertised: {capabilities}")
    if not isinstance(capabilities.get("led_count"), int) or capabilities["led_count"] < 1:
        raise RuntimeError(f"Invalid LED count: {capabilities}")
    print(f"Hardware ready: {identity}; {capabilities}", flush=True)
    return {"status": status, "identity": identity, "capabilities": capabilities}


def robot_counts(xml_path):
    """Read actual Robot test-case statuses, not suite statuses or exit codes."""
    if not xml_path.is_file():
        return None
    try:
        root = ET.parse(xml_path).getroot()
        counts = {"PASS": 0, "FAIL": 0, "SKIP": 0}
        for test in root.iter("test"):
            status = test.find("status")
            if status is None or status.get("status") not in counts:
                raise ValueError("Robot test has no recognized status")
            counts[status.get("status")] += 1
        return {"total": sum(counts.values()), **counts}
    except (OSError, ET.ParseError, ValueError) as exc:
        print(f"Could not read Robot results from {xml_path}: {exc}", file=sys.stderr, flush=True)
        return None


def print_final_summary(record, output):
    print("\n" + "=" * 62)
    print("             PHASE 1 VALIDATION - FINAL SUMMARY")
    print("=" * 62)
    for stage, label in (("simulator", "SIMULATOR"), ("hardware", "HARDWARE")):
        data = record["stages"].get(stage, {})
        counts = data.get("counts")
        if counts:
            print(f"{label:10} {counts['total']:2} tests | {counts['PASS']:2} PASS | "
                  f"{counts['FAIL']:2} FAIL | {counts['SKIP']:2} SKIP | "
                  f"{'OK' if data.get('return_code') == 0 else 'FAILED'}")
        else:
            print(f"{label:10} NOT RUN / NO RESULTS: "
                  f"{data.get('skipped') or data.get('error') or 'no valid test XML'}")
    counts = record.get("totals", {})
    print("-" * 62)
    print(f"TOTAL      {counts.get('total', 0):2} tests | {counts.get('PASS', 0):2} PASS | "
          f"{counts.get('FAIL', 0):2} FAIL | {counts.get('SKIP', 0):2} SKIP")
    print(f"OVERALL    {record['result']}")
    if record['mode'] != 'sim-only':
        print(f"LED VISUAL {record['physical_led_observation']} (operator-reported)")
    print(f"REPORT     {output / 'report.html'}")
    print(f"LOG        {output / 'log.html'}")
    print(f"JSON       {output / 'validation_summary.json'}")
    print("=" * 62, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", help="DK serial port, e.g. COM3 (required unless --sim-only)")
    parser.add_argument("--board", default="nrf52840dk", choices=["nrf52840dk"],
                        help="Phase 1 hardware target; add others after validation")
    parser.add_argument("--sim-only", action="store_true", help="Run without a connected DK")
    parser.add_argument("--outputdir", default="results/phase1", help="Report directory")
    parser.add_argument("--led-observation", choices=["confirmed", "not-confirmed", "not-observed"],
                        default="not-observed", help="Operator observation of LED1-LED4 during THIS run; not sensor evidence")
    args = parser.parse_args()
    if not args.sim_only and not args.port:
        parser.error("--port is required for full Phase 1 validation; or use --sim-only")

    output = Path(args.outputdir)
    if not output.is_absolute():
        output = ROOT / output
    output.mkdir(parents=True, exist_ok=True)
    parts = output / "parts"
    parts.mkdir(exist_ok=True)
    record = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "board": args.board,
        "mode": "sim-only" if args.sim_only else "sim-and-hardware",
        "port": args.port,
        "stages": {},
        "physical_led_observation": "Not observed or not recorded",
    }
    xml_files = []

    sim_dir = parts / "simulator"
    sim_dir.mkdir(exist_ok=True)
    # Prevent stale output.xml from a previous run from entering the combined report.
    for previous in (sim_dir / "output.xml",):
        previous.unlink(missing_ok=True)
    sim_rc = run_command([
        sys.executable, "-m", "robot", "--name", "Simulator",
        "--variable", f"BOARD:{args.board}", "--variable", "BACKEND:sim",
        "--outputdir", str(sim_dir), "tests/common", "tests/optional", "tests/simulator",
    ])
    record["stages"]["simulator"] = {"return_code": sim_rc, "counts": robot_counts(sim_dir / "output.xml")}
    if (sim_dir / "output.xml").exists():
        xml_files.append(sim_dir / "output.xml")

    # Do not run physical tests if simulator regression fails. This prevents a
    # broken Python facade from being mistaken for a firmware/hardware problem.
    if sim_rc == 0 and not args.sim_only:
        try:
            record["hardware_probe"] = probe_hardware(args.port, args.board)
            record["stages"]["hardware_probe"] = {"return_code": 0}
        except Exception as exc:
            print(f"HARDWARE PREFLIGHT FAILED: {exc}", file=sys.stderr, flush=True)
            record["stages"]["hardware_probe"] = {"return_code": 1, "error": str(exc)}
        else:
            hw_dir = parts / "hardware"
            hw_dir.mkdir(exist_ok=True)
            (hw_dir / "output.xml").unlink(missing_ok=True)
            hw_rc = run_command([
                sys.executable, "-m", "robot", "--name", "Hardware nRF52840",
                "--variable", f"BOARD:{args.board}", "--variable", "BACKEND:serial",
                "--variable", f"PORT:{args.port}",
                "--outputdir", str(hw_dir), "tests/platform/01_nrf52840_hardware.robot",
            ])
            record["stages"]["hardware"] = {"return_code": hw_rc, "counts": robot_counts(hw_dir / "output.xml")}
            if (hw_dir / "output.xml").exists():
                xml_files.append(hw_dir / "output.xml")
    elif sim_rc != 0:
        record["stages"]["hardware"] = {"skipped": "Simulator regression failed"}

    if args.sim_only:
        record["stages"]["hardware"] = {"skipped": "sim-only mode selected"}
    elif "hardware" not in record["stages"]:
        reason = record["stages"].get("hardware_probe", {}).get("error", "hardware probe did not pass")
        record["stages"]["hardware"] = {"skipped": reason}

    # Remove any old combined report before generating a fresh one. Otherwise
    # an earlier PASS report might be mistaken for this run's evidence.
    for name in ("output.xml", "log.html", "report.html"):
        (output / name).unlink(missing_ok=True)
    if xml_files:
        # rebot combines separate Robot runs into a single navigable HTML log.
        # No --merge: these are DIFFERENT top-level suites, not reruns of one suite.
        report_rc = run_command([
            sys.executable, "-m", "robot.rebot", "--name", "Phase 1 Validation",
            "--outputdir", str(output), *map(str, xml_files),
        ])
        record["stages"]["combined_report"] = {"return_code": report_rc}
    else:
        record["stages"]["combined_report"] = {"error": "No Robot XML generated"}

    # Guard against partial/incorrect test selection being reported as success.
    sim_counts = record["stages"]["simulator"].get("counts")
    hw_counts = record["stages"].get("hardware", {}).get("counts")
    expected_sim = 14  # 6 common + 6 advanced + 2 optional
    expected_hw = 2    # identity + physical LED sequence
    if sim_counts and sim_counts["total"] != expected_sim:
        print(f"ERROR: Expected {expected_sim} simulator tests, found {sim_counts['total']}", flush=True)
    if not args.sim_only and hw_counts and hw_counts["total"] != expected_hw:
        print(f"ERROR: Expected {expected_hw} hardware tests, found {hw_counts['total']}", flush=True)
    totals = {key: sum((stage.get("counts") or {}).get(key, 0)
                       for stage in (record["stages"].get("simulator", {}),
                                     record["stages"].get("hardware", {})))
              for key in ("total", "PASS", "FAIL", "SKIP")}
    record["totals"] = totals
    all_ok = bool(sim_counts and sim_counts["total"] == expected_sim and
                  sim_counts["FAIL"] == 0 and
                  (args.sim_only or (hw_counts and hw_counts["total"] == expected_hw and
                                     hw_counts["FAIL"] == 0))) and sim_rc == 0 and (args.sim_only or (
        record["stages"].get("hardware_probe", {}).get("return_code") == 0 and
        record["stages"].get("hardware", {}).get("return_code") == 0
    )) and record["stages"]["combined_report"].get("return_code") == 0
    record["result"] = "PASS" if all_ok else "FAIL"
    # This is a human-reported observation, never inferred from LED_GET.
    if not args.sim_only and record["stages"].get("hardware", {}).get("return_code") == 0:
        record["physical_led_observation"] = args.led_observation
    record["physical_validation"] = (
        "CONFIRMED_BY_OPERATOR" if all_ok and not args.sim_only and args.led_observation == "confirmed"
        else "NOT_CONFIRMED" if not args.sim_only else "NOT_APPLICABLE"
    )
    (output / "validation_summary.json").write_text(
        json.dumps(record, indent=2) + "\n", encoding="utf-8"
    )
    print_final_summary(record, output)
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
