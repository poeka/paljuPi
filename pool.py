import glob
import os
import temp
import floatSwitch
import relay
import queue


class Pool:

    def __init__(self, in_ws_q, out_ws_q, out_display_q):
        self.in_ws_q = in_ws_q
        self.out_ws_q = out_ws_q
        self.out_display_q = out_display_q
        self.target = 38.0
        self.lower_limit = 36.0
        self.total_temperature = -85
        self.temp_low = temp.TempSensor("28-0517a04776ff")  # Lower
        self.low_value = -85
        self.temp_high = temp.TempSensor("28-000008a5dd2c")  # Upper
        self.high_value = -85
        self.temp_ambient = temp.TempSensor("28-031724b16bff")  # Ambient
        self.ambient_value = -85
        self.estimate = 0
        self.heating_state = "OFF"  # ON/OFF/UPKEEP/FOFF
        self.relay = relay.Relay()
        self.floatSwitch = floatSwitch.FloatSwitch()

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

    def get_state(self):
        return self.heating_state

    def set_state(self, state):

        if state == "OFF":
            self.relay.toggle_off()
            self.heating_state = state
            return

        elif state == "FOFF":
            self.relay.toggle_off()
            self.heating_state = state
            return

        elif state == "ON":
            self.relay.toggle_on()
            self.heating_state = state
            return

        elif state == "UPKEEP":
            self.relay.toggle_off()
            self.heating_state = state
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
        self.estimate = estimate

    def data_in(self):
        if not self.in_ws_q.empty():
            data_in = self.in_ws_q.get()

        if self.get_state() == "FOFF":
            if data_in["warming_phase"] == "ON":
                self.set_state("ON")

        elif data_in["warming_phase"] == "FOFF":
            self.set_state("FOFF")

        self.set_target(data_in["target"])
        self.set_lower_limit(data_in["low_limit"])
        self.set_estimate(data_in["estimation"])

    def data_out(self):
        data = {"temp_low": self.get_temp_low(),
                "temp_high": self.get_temp_high(),
                "temp_ambient": self.get_temp_ambient(),
                "warming_phase": self.get_state(),
                "target": self.get_target(),
                "low_limit": self.get_lower_limit(),
                "estimate": self.get_estimate()}

        if self.out_ws_q.empty():
            self.out_ws_q.put(data)
        if self.out_display_q.empty():
            self.out_display_q.put(data)
