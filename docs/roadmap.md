# Extension roadmap

## Verified before this refactor

- Python + Robot Framework simulator integration.
- nRF52840 DK JSON-lines serial communications at 115200 baud.
- Firmware identity checks and LED1 on/off control (visually observed).

## Phase 1 — revalidate reorganized nRF52840 firmware

1. Simulator regression (8 tests, expected 6 PASS / 2 SKIP).
2. Compile and flash refactored firmware.
3. Confirm `CAPABILITIES.led_count` matches available Zephyr aliases.
4. Run physical LED1–LED4 test; inspect each LED and capture results.
5. Preserve logs and note actual board/SDK version.

## Phase 2 — nRF54L15 DK

Verify the exact DK revision, board target, UART routing, LED aliases, and supported GPIO features. Add only board-specific configuration or overlay where possible. Do **not** assume it has the same number of LEDs or buttons as nRF52840 DK. Build and test independently before marking supported.

## Phase 3 — richer capabilities and interfaces

Versioned capability discovery (LED count, button count, BLE roles, sensors); physical button reads; BLE advertising/scanning with an independent BLE peer; negative/error-path tests; UART interrupts/ring buffer; robust JSON parser.

## Phase 4 — Silicon Labs EFR32BG22

Implement the same wire protocol and `led_control` interface using Silicon Labs SDK GPIO APIs (or Zephyr if chosen). Document the exact development board, USB-UART route, pin mappings, and flash tooling. Reuse Robot/Python layers.

## Phase 5 — automation infrastructure

CI simulator workflow, hardware self-hosted runner, programmable power/reset, optical/electrical LED sensing, automated button actuator, artifacts and trend dashboards.
