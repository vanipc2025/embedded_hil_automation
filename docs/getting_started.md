# Reproduce the demo — phased guide

## 0. Save your working baseline

If you have already flashed a known-good nRF52840 firmware, copy its `main.c`, `prj.conf`, and `CMakeLists.txt` elsewhere before replacing them. This archive is a **refactor reconstructed from previously demonstrated behavior**, not a byte-for-byte copy of the working firmware.

## Tooling policy and readiness

For the **documented firmware build/flash workflow**, VS Code with the Nordic nRF Connect extension and nRF Connect SDK v3.2.0 are **mandatory prerequisites**. That requirement describes the workflow actually validated by the project, **not** a universal requirement to execute Python or Robot Framework. VS Code is **optional** for simulator-only execution and for running tests against a previously flashed board. Alternative Zephyr command-line builds are possible but not validated here.

| Goal | Required | Not required |
| --- | --- | --- |
| Simulator | Python 3.12+, pip, Robot Framework, PySerial | VS Code, SDK, DK |
| Build/flash Nordic firmware (verified route) | VS Code, Nordic extension, SDK 3.2.0, matching toolchain, nRF52840 DK | Physical LED sensor |
| Test flashed DK | Python, Robot Framework, PySerial, DK with compatible firmware, serial port | VS Code, SDK, build tools |

Before proceeding, run the appropriate read-only preflight command:

```bash
python scripts/check_environment.py --mode simulator
python scripts/check_environment.py --mode development
python scripts/check_environment.py --mode hardware --port COM3
```

Development mode checks IDE and extension detection but **cannot certify** the SDK/toolchain selection, a current build, or a successful flash; confirm these in VS Code. Hardware mode probes a board that must already be flashed. None of the modes observes LED light. See the root README for the full dependency matrix and verified environment.

## 1. Install Python dependencies

```bash
cd /c/embedded_hil_automation   # Windows Git Bash example
python --version
python -m pip install -r requirements.txt
python -m robot --version
```

Run commands from the **project root**. A virtual environment is recommended for repeatability.

## 2. Run simulator

```bash
python -m robot --outputdir results/simulator tests/common/ tests/optional/
```

Expected: **8 total, 6 PASS, 0 FAIL, 2 SKIP**. Optional-feature skips are intentional.

## 3. Build and flash Nordic firmware

- Install nRF Connect for VS Code and the Nordic nRF Connect SDK toolchain (initial experiment: SDK 3.2.0).
- Open `firmware/nordic_zephyr` as an application.
- Choose board target `nrf52840dk/nrf52840` (or the corresponding board selector in your SDK).
- Build. If Zephyr reports a missing LED alias, inspect your board's devicetree and adapt the LED module or overlay.
- Flash the connected nRF52840 DK.

## 4. Locate serial port

On Windows, use Device Manager > Ports > J-Link CDC UART Port. On Linux, inspect `/dev/ttyACM*` and serial access permissions. Set baud **115200**. Close serial terminals before running Robot.

## 5. Run hardware smoke suite

```bash
python -m robot --variable BOARD:nrf52840dk --variable BACKEND:serial \
  --variable PORT:COM3 --outputdir results/hardware_nrf52840 \
  tests/platform/01_nrf52840_hardware.robot
```

Replace `COM3` with your actual port. The test checks the firmware identity and cycles each advertised LED. **Visually confirm LED1, LED2, LED3, and LED4**; command-state assertions alone cannot prove the LED emitted light.

## 6. Run common hardware-compatible tests

```bash
python -m robot --variable BOARD:nrf52840dk --variable BACKEND:serial \
  --variable PORT:COM3 --outputdir results/hardware_common tests/common/
```

Expected behavior: boot and GPIO tests run; BLE tests skip until implemented in firmware. Counts depend on the connected firmware's reported capabilities.

## 7. Review reports

Open `results/.../report.html` and `log.html`. Keep reports locally; do not commit generated reports by default. Record the SDK version, board revision, serial port, and observed LED behavior in test notes.


## One-command validation, cleanup and Git publication checks

All commands below run from the repository root. The three scripts have distinct jobs:

```bash
# Run automated readiness checks, then simulator and physical HIL tests.
python scripts/run_all.py --port COM3

# No hardware available? Simulator-only preflight + tests.
python scripts/run_all.py --sim-only

# Optional: include VS Code / nRF Connect development preflight.
python scripts/run_all.py --port COM3 --check-development

# Preview what would be deleted; does NOT delete anything.
python scripts/clean_generated.py

# Delete only known generated reports and Python caches.
python scripts/clean_generated.py --apply

# Verify .gitignore rules and look for previously tracked artifacts.
python scripts/check_gitignore.py
```

**Recommended order before GitHub:** run tests → inspect `results/phase1/log.html` and
`report.html` → confirm the four LEDs physically illuminate in order → archive any
reports you need outside the project → preview and apply cleanup → run the Git
ignore checker → `git status` → commit. The cleanup intentionally leaves Zephyr
`build/` folders intact (they are ignored by Git), so you can rebuild or flash
without reconfiguring. `check_gitignore.py` requires Git and checks both ignore
rules and already-tracked files; `.gitignore` does not untrack committed files.

**Run expectations:** the simulator should report 6 PASS and 2 SKIP; the
nRF52840 DK hardware suite should report 2 PASS. During the physical suite,
LED1–LED4 should turn on one at a time for about two seconds and then turn off.
`log.html` records software assertions, not optical measurements. To record a
human observation for this run, pass `--led-observation confirmed` only if you
actually watched the LEDs. The combined report and summary live in
`results/phase1/` and are intentionally excluded from GitHub.

**Scope:** `run_all.py` checks the existing test environment and firmware
communication; it does not build or flash firmware. `--check-development`
checks the documented VS Code development workflow separately.
