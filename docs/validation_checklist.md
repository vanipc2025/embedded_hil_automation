## Environment readiness (before testing)

- [ ] Simulator mode: `python scripts/check_environment.py --mode simulator` reports READY.
- [ ] If building firmware: `python scripts/check_environment.py --mode development` reports READY for detectable prerequisites; manually verify VS Code, Nordic extension, SDK v3.2.0, board target, build, and flash.
- [ ] If testing a flashed DK: `python scripts/check_environment.py --mode hardware --port COM3` reports READY; VS Code is not required for this mode.
- [ ] Confirm COM port is free, board powered, and visual LED inspection is possible.

# Phase 1 validation checklist — nRF52840 DK

Use this checklist when running the **new combined runner**. The underlying
simulator and hardware suites were previously verified on 10 November 2026;
the combined runner itself requires a separate execution and confirmation.

## Before running

- [ ] nRF52840 DK is connected by USB and powered.
- [ ] Zephyr firmware `hil-serial-v2` is already built and flashed.
- [ ] J-Link CDC UART port is identified (COM3 in the verified setup).
- [ ] No serial monitor or other Python process has the COM port open.
- [ ] Python dependencies installed: `python -m pip install -r requirements.txt`.

## Run

```bash
python scripts/run_validation.py --port COM3
```

## Terminal and `log.html` observations

- [ ] Simulator: 6 PASS, 2 SKIP, 0 FAIL.
- [ ] Hardware preflight: `READY`, correct board identity, four advertised LEDs.
- [ ] Hardware identity test: PASS.
- [ ] Hardware LED-loop test: PASS.
- [ ] LED1 ON for ~2 seconds, then OFF (look at the physical board).
- [ ] LED2 ON for ~2 seconds, then OFF.
- [ ] LED3 ON for ~2 seconds, then OFF.
- [ ] LED4 ON for ~2 seconds, then OFF.
- [ ] No LEDs remain lit at the end of the test.
- [ ] Combined `results/phase1/report.html`: 10 total, 8 PASS, 0 FAIL, 2 SKIP.
- [ ] `results/phase1/validation_summary.json`: simulator, hardware preflight,
      hardware, and combined-report stages successful.

## Recording observations

The HTML log documents **software commands and assertions**, not independent
optical measurements. For a run where the engineer actually observed the four
LEDs, the optional `--led-observation confirmed` argument writes that manual
attestation into `validation_summary.json`. It does not add sensor evidence.
If visual observation differs from the software result, record the discrepancy
and do not mark physical validation complete.

## If something fails

See [troubleshooting.md](troubleshooting.md). The runner will not attempt
hardware tests if simulator regression or serial preflight fails. In such
cases `log.html` can contain only simulator tests: read the summary JSON.


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
