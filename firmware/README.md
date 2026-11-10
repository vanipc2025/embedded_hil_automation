# Firmware implementations

- `nordic_zephyr/`: **Phase 1** Zephyr UART agent, modular LED control, JSON-lines protocol. nRF52840 DK is the first target.
- `silabs_bg22/`: future Silicon Labs EFR32BG22 implementation placeholder; **not operational**.

The firmware agent is a test endpoint, not an application for production deployment. See `../docs/architecture.md` and `../docs/serial_protocol.md`.

## Licensing and hardware independence

Original firmware code in this repository is distributed under the root
[MIT License](../LICENSE). The example Zephyr implementation is one hardware
backend of a broader educational test automation architecture; the repository
license is not restricted to Nordic hardware. Silicon Labs integration is
planned, not validated. Nordic, Zephyr, Silicon Labs and other external SDKs
and tools have their own licenses and trademarks. Users must follow those
licenses when obtaining, building, or redistributing vendor components.
