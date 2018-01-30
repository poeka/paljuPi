import os
import glob
import temp


class Pool:

    def __init__(self):
        
        self.target = 38
        self.lower_limit = 36
        self.total_temperature = -85
        self.temp_low = temp.TempSensor("28-0517a04776ff") # Lower
        self.low_value = -85
        self.temp_high = temp.TempSensor("28-000008a5dd2c")  # Upper
        self.high_value = -85
        self.temp_ambient = temp.TempSensor("28-031724b16bff")  # Ambient
        self.ambient_value = -85
        self.heating_state = "ON"  # ON/OFF/UPKEEP/FORCEOFF

    def get_temp_low(self):

        if self.low_value is False:
            return False

        else:
            return self.low_value

    def get_temp_high(self):

        if self.high_value is False:
            return False

        else:
            return self.high_value

    def get_ambient(self):

        if self.ambient_value is False:
            return False

        else:
            return self.ambient_value
    
    def get_temperatures(self):

        self.low_value = self.temp_low.get_temperature()
        self.high_value = self.temp_high.get_temperature()
        self.ambient_value = self.temp_ambient.get_temperature()

        if self.low_value is False:
            return False

        elif self.high_value is False:
            return False

        elif self.ambient_value is False:
            return False

        return True

    def set_target(self, target):
        self.target = target

    def get_target(self):
        return self.target

    def set_state(self, state):
        self.heating_state = state

    def get_state(self):
        return self.heating_state