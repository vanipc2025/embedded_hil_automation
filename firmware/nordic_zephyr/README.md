# Nordic Zephyr test firmware

`src/main.c` owns UART reception, minimal JSON parsing, command dispatch, and responses. `src/led_control.c` owns GPIO initialization, logical LED control, and last-commanded state; `src/led_control.h` defines the interface. `CMakeLists.txt` compiles both.

**Original proven fix:** continuous `uart_poll_in()` is essential to avoid dropped bytes observed when `k_msleep(1)` was used at 115200 baud. This busy loop is a deliberate first-phase compromise.

**Portability:** Zephyr `led0` to `led3` aliases supply GPIO pins and active-low polarity. The number of compiled LED aliases determines `CAPABILITIES.led_count`. Alias gaps should be avoided; the next iteration should explicitly validate contiguous aliases. A board without `led0` will fail the build rather than falsely advertise GPIO.

**Build:** open this directory in nRF Connect for VS Code, select `nrf52840dk/nrf52840`, build, and flash. Confirm serial port, run the simulator first, then run the physical suite. **Phase 1 verification (10 November 2026):** this refactored firmware built, flashed, returned `hil-serial-v2` and `led_count: 4`, and passed the two nRF52840 DK Robot hardware tests; LED1–LED4 were visually confirmed by the operator. VS Code + Nordic nRF Connect extension + SDK v3.2.0 are required for the *documented* build workflow, but are not runtime dependencies for Robot tests on a preflashed DK.


**License:** Original example code is covered by the repository [MIT License](../../LICENSE); third-party SDKs and tools retain their own licenses.
