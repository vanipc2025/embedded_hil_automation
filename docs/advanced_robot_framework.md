# Advanced Robot Framework flow control and tags

This is an educational extension to the **previously verified** Phase 1 baseline. The six new simulator tests and their combined-runner integration **must be rerun locally** before claiming new validation totals. No firmware or Python adapter implementation was changed.

## Learning goals and examples

| Construct | Example | Design reason |
| --- | --- | --- |
| `IF/ELSE` | `Capability Branch Logs Supported Path` and `...Unsupported Path` | Exercise both capability branches; do not silently accept missing mandatory GPIO |
| `FOR` | `Simulator Buttons Press And Release`; common LED loop | Avoid repeating cases for every control; real LED count comes from firmware |
| `TRY/EXCEPT/ELSE` | Invalid LED index and recovery cases | Catch **only expected** invalid-index errors; unexpected errors still fail |
| `Skip` | `Require Device Feature` | Unsupported optional feature is SKIP, not PASS |
| Tags | All test cases | Filter by purpose and environment |

**Important:** `TRY/EXCEPT` is not a blanket instruction to swallow failures. Unexpected failures must remain FAIL; the invalid-index tests deliberately fail if the invalid request is accepted. No automatic retry is applied to LED assertions.

## Tag convention

- `smoke`: quick identity/critical hardware checks
- `regression`: repeatable behavior checks
- `firmware`: firmware status and identity
- `gpio`: LED interface
- `buttons`: simulator button behavior
- `ble`: simulated BLE behavior until hardware BLE is implemented
- `simulator`: tests that must not be used as evidence of real hardware
- `hardware`: real DK only; must provide `BACKEND:serial` and `PORT`
- `optional`: intentionally unsupported feature examples
- `conditional`: branching or capability-dependent tests
- `negative`: deliberately invalid requests whose rejection is verified

Robot tags do not use an `@` prefix.

## Targeted runs

```bash
# All simulator regression and optional tests, including advanced flow:
python -m robot --outputdir results/simulator tests/common/ tests/optional/ tests/simulator/

# Simulator-only advanced-flow lab:
python -m robot --outputdir results/learning tests/simulator/

# Only simulator negative cases:
python -m robot --include negative --outputdir results/negative tests/simulator/

# Only common GPIO tests (without simulator-only suites):
python -m robot --include gpio --outputdir results/gpio tests/common/

# Physical hardware smoke tests (requires flashed DK and actual serial port):
python -m robot --include smoke --variable BACKEND:serial --variable PORT:COM3 --outputdir results/hardware_smoke tests/platform/
```

**Safety:** Do not run `tests/common/03_ble.robot` as evidence of physical BLE, and do not pass the entire `tests/` tree with serial backend. Use the included runner, which separates simulator from hardware. The `tests/simulator/` suite refuses a non-simulator backend.

## Expected outcomes (new tests not yet locally verified)

With the nRF52840 simulator profile: existing 8 simulator cases (6 PASS, 2 SKIP) + 6 new advanced cases (expected 6 PASS) = **14 simulator cases: 12 PASS, 2 SKIP**. With the two previously verified nRF52840 hardware tests, the new combined runner is expected to produce **16 cases: 14 PASS, 2 SKIP**. These are expectations until the updated package is executed.

## Reflection

Conditional branches let one suite adapt to available functionality, while explicit skips distinguish unsupported features from failures. Loops and tags reduce duplication and allow targeted execution; precise exception patterns preserve real defects instead of masking them. Future contributors should keep tag meanings documented and add platform-specific tests only after validating real firmware support.
