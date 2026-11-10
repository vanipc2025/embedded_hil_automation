# Silicon Labs EFR32BG22 — planned integration

This directory intentionally contains **no working BG22 firmware**. Do not claim hardware support until the chosen Silicon Labs board, SDK, pin mappings, UART, and flashing workflow are tested.

Implementation contract: return `STATUS`, `IDENTITY`, `CAPABILITIES`, `LED_SET`, and `LED_GET` JSON-lines responses at 115200 baud; implement LED control with Silicon Labs GPIO APIs; keep `IDENTITY.board` as `silabs_bg22`. Python and Robot Framework can then be reused unchanged.


**License:** Original example code is covered by the repository [MIT License](../../LICENSE); third-party SDKs and tools retain their own licenses.
