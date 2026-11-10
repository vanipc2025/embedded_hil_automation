"""Deterministic simulator for protocol-level development without a board.

Simulation is deliberately *not* evidence that BLE or GPIO work on real hardware.
The simulator uses the same request(command, **args) API as the serial adapter.
"""

class SimulatedDevice:
    def __init__(self, profile, board="nrf52840dk"):
        self.profile = profile
        self.board = board
        self.leds = [False] * int(profile["sim_led_count"])
        self.buttons = [False] * int(profile["sim_button_count"])

    @staticmethod
    def _index(index, values):
        # External protocol is 1-based; Python arrays are 0-based.
        number = int(index)
        if not 1 <= number <= len(values):
            raise ValueError(f"Index {number} outside 1..{len(values)}")
        return number - 1

    def request(self, command, **args):
        if command == "STATUS":
            return {"status": "READY"}
        if command == "IDENTITY":
            return {"board": self.board, "firmware": "hil-simulator-v1", "backend": "sim"}
        if command == "CAPABILITIES":
            return {"led_count": len(self.leds), "features": list(self.profile["sim_features"])}
        if command == "LED_SET":
            self.leds[self._index(args["index"], self.leds)] = bool(args["on"])
            return {"ok": True}
        if command == "LED_GET":
            return {"on": self.leds[self._index(args["index"], self.leds)]}
        if command == "BUTTON_INJECT":
            self.buttons[self._index(args["index"], self.buttons)] = bool(args.get("pressed", True))
            return {"ok": True}
        if command == "BUTTON_GET":
            return {"pressed": self.buttons[self._index(args["index"], self.buttons)]}
        if command == "BLE_SCAN":
            return {"found": args.get("name") == "HIL_SIM_DEVICE"}
        if command == "BLE_RSSI":
            return {"rssi": -55}
        raise ValueError(f"Simulator does not implement {command}")

    def close(self):
        """Parity with SerialDevice.close(); no OS resource to release."""
