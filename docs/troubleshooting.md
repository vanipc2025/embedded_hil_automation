# Troubleshooting

| Symptom | Likely cause | What to check |
| --- | --- | --- |
| COM port access denied | Another process holds serial port | Close terminal, Python REPL, VS Code serial monitor |
| No firmware response | Wrong port, baud, flash image, cable | Confirm J-Link CDC UART and 115200 baud; reflash |
| Truncated JSON / invalid response | Slow UART receive loop or debug text | **Do not add `k_msleep(1)` in polling loop**; disable console logging on protocol UART |
| `Board mismatch` | Wrong firmware/board selected | Compare `IDENTITY.board` to Robot `BOARD` |
| `LED_GET` differs from physical LED | Command-state is not optical state | Visually inspect LED; check devicetree alias and polarity |
| LED alias build error | Target board lacks alias | Inspect devicetree, add overlay or board-specific driver |
| BLE tests SKIP on hardware | Firmware advertises only `gpio` | Expected until real BLE implementation exists |
| Simulator PASS, hardware FAIL | Simulation is a model, not physical evidence | Check firmware, UART, GPIO, wiring, board revision |

**Historical fixes:** the original experiment lost UART bytes when sleeping 1 ms between reads at 115200 baud; continuous `uart_poll_in()` fixed the corruption. Initial GPIO output readback was misleading; commanded state tracking fixed the API response, but physical inspection remains necessary.
