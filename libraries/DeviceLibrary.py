"""Stable Robot Framework keyword facade over simulation and serial hardware.

Keep test cases unaware of vendor SDKs and COM-port implementation details.
New boards usually need a board profile and compatible firmware, not new tests.
"""
import json
from pathlib import Path

from robot.api.deco import keyword, library
from robot.libraries.BuiltIn import BuiltIn
from simulator import SimulatedDevice
from serial_adapter import SerialDevice


@library(scope="SUITE")
class DeviceLibrary:
    def __init__(self, board="nrf52840dk", backend="sim", port=""):
        self.board = board.lower()
        self.backend = backend.lower()
        self.port = port
        self.device = None
        profiles_path = Path(__file__).resolve().parents[1] / "config" / "boards.json"
        profiles = json.loads(profiles_path.read_text(encoding="utf-8"))
        if self.board not in profiles:
            raise ValueError(f"Unknown board {board!r}; valid choices: {list(profiles)}")
        self.profile = profiles[self.board]

    @keyword("Connect To Device")
    def connect_to_device(self):
        if self.backend == "sim":
            self.device = SimulatedDevice(self.profile, self.board)
        elif self.backend == "serial":
            self.device = SerialDevice(self.port)
            # Prevent false-positive tests against a different attached board.
            try:
                identity = self.device.request("IDENTITY")
                if identity.get("board") != self.board:
                    raise RuntimeError(
                        f"Board mismatch: selected {self.board!r}, firmware reports {identity.get('board')!r}"
                    )
            except Exception:
                self.device.close()
                self.device = None
                raise
        else:
            raise ValueError(f"Unsupported backend: {self.backend}")
        BuiltIn().log(f"Connected backend={self.backend} board={self.board}", console=True)

    @keyword("Disconnect From Device")
    def disconnect_from_device(self):
        if self.device is not None and hasattr(self.device, "close"):
            self.device.close()
        self.device = None

    def _request(self, command, **args):
        if self.device is None:
            raise RuntimeError("Device is not connected; check Suite Setup")
        return self.device.request(command, **args)

    @keyword("Get Device Status")
    def get_device_status(self):
        return self._request("STATUS")["status"]

    @keyword("Get Firmware Identity")
    def get_firmware_identity(self):
        return self._request("IDENTITY", board=self.board)

    @keyword("Device Supports")
    def device_supports(self, feature):
        # Simple v1 capabilities; future discovery can extend this shape.
        return feature in self._request("CAPABILITIES").get("features", [])

    @keyword("Get LED Count")
    def get_led_count(self):
        return int(self._request("CAPABILITIES")["led_count"])

    @keyword("Set LED State")
    def set_led_state(self, index, on):
        self._request("LED_SET", index=int(index), on=bool(on))

    @keyword("Get LED State")
    def get_led_state(self, index):
        return bool(self._request("LED_GET", index=int(index))["on"])

    @keyword("Inject Button Press")
    def inject_button_press(self, index, pressed=True):
        if self.backend != "sim":
            raise RuntimeError("Physical button injection requires an external fixture")
        self._request("BUTTON_INJECT", index=int(index), pressed=bool(pressed))

    @keyword("Get Button State")
    def get_button_state(self, index):
        return bool(self._request("BUTTON_GET", index=int(index))["pressed"])

    @keyword("Find BLE Device")
    def find_ble_device(self, name):
        return bool(self._request("BLE_SCAN", name=name)["found"])

    @keyword("Read BLE RSSI")
    def read_ble_rssi(self):
        return int(self._request("BLE_RSSI")["rssi"])
