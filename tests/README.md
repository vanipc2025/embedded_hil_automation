# Robot Framework test suites

- `common/`: portable tests for boot identity, LED count/toggling, and BLE (simulated BLE passes; hardware BLE skips unless advertised).
- `optional/`: demonstrations of intentional SKIP for unimplemented capabilities.
- `platform/`: physical nRF52840 DK identity and visually observed LED1..N sequence.

Run from repository root. Each suite owns its own serial connection via `Suite Setup` and `Suite Teardown`; do not keep the COM port open in another program. Never confuse `LED_GET` command-state readback with independent physical measurement.


## What to observe during hardware tests

The nRF52840 DK hardware suite logs `Firmware advertises 4 LED(s)` and
`Visually inspect LED1` through `LED4`. Watch the DK: each numbered LED
should illuminate for about two seconds, then switch off before the next.
The test checks the firmware's last commanded state; visual confirmation
is a separate human observation, not an automated measurement.

Use `python scripts/run_validation.py --port COM3` to run simulator and hardware
suites and combine results in `results/phase1/log.html`. Expect **10 total:
8 PASS, 0 FAIL, 2 SKIP** for a full run. Inspect `validation_summary.json`
to confirm that the hardware stage actually ran before interpreting the report.

## Advanced flow-control learning suite (new; requires local validation)

`tests/simulator/05_advanced_flow.robot` contains six simulator-only tests covering
IF/ELSE (both branches), FOR loops, TRY/EXCEPT/ELSE negative tests, recovery,
button injection, and negative BLE scanning. See
[advanced Robot Framework guide](../docs/advanced_robot_framework.md) for tags,
selective execution, and expected results. These are **not physical button/BLE tests**.

The updated one-command runner includes this suite automatically. The expected
new combined count is **16 cases: 14 PASS, 0 FAIL, 2 SKIP**, pending local
execution; the historical verified Phase 1 result was 10 cases.
