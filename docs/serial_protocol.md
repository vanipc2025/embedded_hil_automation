# Serial test protocol v1 (simple capability schema)

**Transport:** 115200 baud, 8N1, UTF-8 JSON object per line (`\n`). One request produces one JSON response. No console logs or Zephyr boot banners on the same UART. `serial_adapter.py` expects one response line within 3 seconds.

| Request | Successful response | Notes |
| --- | --- | --- |
| `{"cmd":"STATUS"}` | `{"status":"READY"}` | Smoke check |
| `{"cmd":"IDENTITY"}` | `{"board":"nrf52840dk","firmware":"hil-serial-v2","backend":"serial"}` | Board name must match Python selection |
| `{"cmd":"CAPABILITIES"}` | `{"led_count":4,"features":["gpio"]}` | **Example**; count depends on compiled aliases |
| `{"cmd":"LED_SET","index":1,"on":true}` | `{"ok":true}` | Logical LED number is 1-based |
| `{"cmd":"LED_GET","index":1}` | `{"on":true}` | Returns last successfully commanded state |

Errors return `{"error":"explanation"}`. The Python serial adapter raises an exception on an error response or malformed JSON. Unsupported commands must **not** pretend to succeed.

## Compatibility and limits

The current firmware accepts a deliberately narrow subset of JSON (simple scalar keys and values). It is meant for the included Python adapter, not arbitrary client input. Add a real JSON parser, request IDs, explicit protocol versioning, timeouts, and recovery logic before using this as a generalized production transport.

`CAPABILITIES` currently uses the simple schema expected by `DeviceLibrary.py`. A richer nested capability model should be added as a **versioned** protocol extension, not by silently replacing existing fields.
