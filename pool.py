import glob
import os

from temp import TempSensor
from floatSwitch import FloatSwitch
from relay import Relay
from magneticValve import MagneticValve
from pressureSender import PressureSender


class Pool:
    ON = "ON"
    OFF = "OFF"
    UPKEEP = "UPKEEP"
    FOFF = "FOFF"

    def __init__(self, in_ws_q, out_ws_q, out_display_q):
        self.in_ws_q = in_ws_q
        self.out_ws_q = out_ws_q
        self.out_display_q = out_display_q
        self.target = 37.0
        self.lower_limit = 36.5
        self.water_level_target = 70  # Target in cm
        self.total_temperature = -85
        self.temp_low = TempSensor("28-0517a04776ff")  # Lower
        self.low_value = -85
        self.temp_high = TempSensor("28-000008a5dd2c")  # Upper
        self.high_value = -85
        self.temp_ambient = TempSensor("28-031724b16bff")  # Ambient
        self.ambient_value = -85
        self.estimate = 0
        self.heating_state = self.OFF  # ON/OFF/UPKEEP/FOFF
        self.relay = Relay()
        self.magneticValve = MagneticValve()
        self.floatSwitch = FloatSwitch()
        self.pressureSender = PressureSender()
        self.water_level = float(-1)

    def open_valve(self):
        self.magneticValve.open()
        return

    def close_valve(self):
        self.magneticValve.close()
        return

    def get_temp_low(self):
        if self.low_value is False:
            return False

        return self.low_value

    def get_temp_high(self):

        if self.high_value is False:
            return False

        return self.high_value

    def get_temp_ambient(self):

        if self.ambient_value is False:
            return False

        return self.ambient_value

    def get_temperatures(self):
        self.low_value = round(self.temp_low.get_temperature(), 1)
        self.high_value = round(self.temp_high.get_temperature(), 1)
        self.ambient_value = round(self.temp_ambient.get_temperature(), 1)

        if self.low_value == 0:
            return False

        elif self.high_value == 0:
            return False

        elif self.ambient_value == 0:
            return False

        return True

    def read_water_level(self):
        self.water_level = round(
            float(self.pressureSender.get_water_level(self.high_value)), 1)

    def get_water_level(self):
        return self.water_level

    def get_water_level_target(self):
        return self.water_level_target

    def set_water_level_target(self, target):
        self.water_level_target = int(target)
        return

    def get_state(self):
        return self.heating_state

    def set_state(self, state):

        if state == self.OFF:
            self.relay.toggle_off()
            self.heating_state = self.OFF
            return

        elif state == self.FOFF:
            self.relay.toggle_off()
            self.heating_state = self.FOFF
            return

        elif state == self.ON:
            self.relay.toggle_on()
            self.heating_state = self.ON
            return

        elif state == self.UPKEEP:
            self.relay.toggle_off()
            self.heating_state = self.UPKEEP
            return

    def get_target(self):
        return self.target

    def set_target(self, target):
        self.target = float(target)

    def get_lower_limit(self):
        return self.lower_limit

    def set_lower_limit(self, lower_limit):
        self.lower_limit = float(lower_limit)

    def get_estimate(self):
        return self.estimate

    def set_estimate(self, estimate):
        self.estimate = int(estimate)

    def data_in(self):
        if not self.in_ws_q.empty():
            data_in = self.in_ws_q.get()

            if self.get_state() == self.FOFF:
                if data_in["warming_phase"] == self.ON:
                    self.set_state(self.ON)

            elif data_in["warming_phase"] == self.FOFF:
                self.set_state(self.FOFF)

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

        if self.out_ws_q.empty():
            self.out_ws_q.put(data)
        if self.out_display_q.empty():
            self.out_display_q.put(data)
