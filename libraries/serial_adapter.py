"""JSON-lines transport to compatible test firmware over a USB virtual COM port.

One request line -> one response line at 115200 baud. Firmware must emit NO
unrelated text on the protocol UART, or JSON decoding will fail. Keep this
adapter board-independent; hardware differences belong in firmware drivers.
"""
import json


class SerialDevice:
    def __init__(self, port, baudrate=115200, timeout=3):
        try:
            import serial
        except ImportError as exc:
            raise RuntimeError("Install dependencies: python -m pip install -r requirements.txt") from exc
        if not port:
            raise ValueError("Provide PORT (for example COM3 on Windows or /dev/ttyACM0 on Linux)")
        self.conn = serial.Serial(port=port, baudrate=int(baudrate), timeout=float(timeout))

    def request(self, command, **args):
        payload = json.dumps({"cmd": command, **args}, separators=(",", ":")) + "\n"
        # Drop stale bytes from previous sessions. Do not flush after sending.
        self.conn.reset_input_buffer()
        self.conn.write(payload.encode("utf-8"))
        self.conn.flush()
        response = self.conn.readline()
        if not response:
            raise TimeoutError(f"No firmware response to {command}; check port, firmware, and baud rate")
        try:
            data = json.loads(response.decode("utf-8"))
        except (ValueError, UnicodeDecodeError) as exc:
            raise RuntimeError(f"Non-JSON response to {command}: {response!r}") from exc
        if not isinstance(data, dict) or data.get("error"):
            raise RuntimeError(f"Firmware rejected {command}: {data!r}")
        return data

    def close(self):
        self.conn.close()
