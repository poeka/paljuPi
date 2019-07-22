import glob
import os

import defs
from temp import TempSensor
from floatSwitch import FloatSwitch
from relay import Relay
from magneticValve import MagneticValve
from pressureSender import PressureSender


class Pool:

    def __init__(self, in_ws_q, out_ws_q, out_display_q):
        self._in_ws_q = in_ws_q
        self._out_ws_q = out_ws_q
        self._out_display_q = out_display_q
        self._target = 37.0
        self._lower_limit = 36.5
        self._water_level_target = 70  # Target in cm
        self._total_temperature = -85
        self._temp_low = TempSensor("28-0517a04776ff")  # Lower
        self._low_value = -85
        self._temp_high = TempSensor("28-000008a5dd2c")  # Upper
        self._high_value = -85
        self._temp_ambient = TempSensor("28-031724b16bff")  # Ambient
        self._ambient_value = -85
        self._estimate = 0
        self._heating_state = defs.OFF  # ON/OFF/UPKEEP/FOFF
        self._next_state = defs.OFF
        self._relay = Relay()
        self._magneticValve = MagneticValve()
        self._floatSwitch = FloatSwitch()
        self._pressureSender = PressureSender()
        self._water_level = float(-1)

    def safe_to_start_burner(self):
        return self._floatSwitch.get_state() == 1

    def handle_valve(self):
        if self.get_water_level() == -1:
            return

        if self.get_water_level() < self.get_water_level_target():
            self._magneticValve.open()
        elif self.get_water_level() >= self.get_water_level_target():
            self._magneticValve.close()

    def get_temp_low(self):
        if self._low_value is False:
            return False

        return self._low_value

    def get_temp_high(self):

        if self._high_value is False:
            return False

        return self._high_value

    def get_temp_ambient(self):

        if self._ambient_value is False:
            return False

        return self._ambient_value

    def get_temperatures(self):
        self._low_value = round(self._temp_low.get_temperature(), 1)
        self._high_value = round(self._temp_high.get_temperature(), 1)
        self._ambient_value = round(self._temp_ambient.get_temperature(), 1)

        if self._low_value == 0:
            return False

        elif self._high_value == 0:
            return False

        elif self._ambient_value == 0:
            return False

        return True

    def read_water_level(self):
        self._water_level = round(
            float(self._pressureSender.get_water_level(self._high_value)), 1)

    def get_water_level(self):
        return self._water_level

    def get_water_level_target(self):
        return self._water_level_target

    def set_water_level_target(self, target):
        self._water_level_target = int(target)
        return

    def get_state(self):
        return self._heating_state

    def set_state(self, state):

        if state == defs.OFF:
            self._relay.toggle_off()
            self._heating_state = defs.OFF
            return

        elif state == defs.FOFF:
            self._relay.toggle_off()
            self._heating_state = defs.FOFF
            return

        elif state == defs.ON:
            self._relay.toggle_on()
            self._heating_state = defs.ON
            return

        elif state == defs.UPKEEP:
            self._relay.toggle_off()
            self._heating_state = defs.UPKEEP
            return

    def get_target(self):
        return self._target

    def set_target(self, target):
        self._target = float(target)

    def get_lower_limit(self):
        return self._lower_limit

    def set_lower_limit(self, lower_limit):
        self._lower_limit = float(lower_limit)

    def get_estimate(self):
        return self._estimate

    def set_estimate(self, estimate):
        self._estimate = int(estimate)

    def get_next_state(self):
        return self._next_state

    def set_next_state(self, next_state):
        self._next_state = next_state

    def data_in(self):
        if not self._in_ws_q.empty():
            data_in = self._in_ws_q.get()

            if self.get_state() == defs.FOFF:
                if data_in["warming_phase"] == defs.ON:
                    self._next_state = defs.ON

            elif data_in["warming_phase"] == defs.FOFF:
                self._next_state = defs.FOFF

            self.set_target(data_in["target"])
            self.set_lower_limit(data_in["low_limit"])
            self.set_estimate(data_in["estimation"])
            self.set_water_level_target(data_in["water_level_target"])

    def data_out(self):
        data = {"temp_low": self.get_temp_low(),
                "temp_high": self.get_temp_high(),
                "temp_ambient": self.get_temp_ambient(),
                "warming_phase": self.get_state(),
                "target": self.get_target(),
                "low_limit": self.get_lower_limit(),
                "estimate": self.get_estimate(),
                "water_level": self.get_water_level(),
                "water_level_target": self.get_water_level_target()}

        if self._out_ws_q.empty():
            self._out_ws_q.put(data)
        if self._out_display_q.empty():
            self._out_display_q.put(data)
