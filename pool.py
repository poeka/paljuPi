import glob
import os
import temp
import floatSwitch
import relay
import RPi.GPIO as GPIO
from max31855 import MAX31855, MAX31855Error


class Pool:

    def __init__(self):
        self.target = 38.0
        self.lower_limit = 36.0
        self.total_temperature = -85
        self.temp_low = temp.TempSensor("28-0517a04776ff")  # Lower
        self.low_value = -85
        self.temp_high = temp.TempSensor("28-000008a5dd2c")  # Upper
        self.high_value = -85
        self.temp_ambient = temp.TempSensor("28-031724b16bff")  # Ambient
        self.ambient_value = -85
        self.heating_state = "OFF"  # ON/OFF/UPKEEP/FOFF
        self.relay = relay.Relay()  # Relay that controls the oil burner
        # GPIO.BOARD pin numbers, (input, output)
        self.floatSwitch = floatSwitch.FloatSwitch(22, 21)
        self.egt = MAX31855(29, 31, 37, GPIO.BOARD)  # Exhaust Gas Temperature
        self.egt_value = -85

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
        self.egt_value = round(self.egt.get(), 1)

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
        self.target = target

    def get_lower_limit(self):
        return self.lower_limit

    def set_lower_limit(self, lower_limit):
        self.lower_limit = lower_limit

    def get_egt(self):
        return self.egt_value
