import os
import glob
import time

#os.system('modprobe w1-gpio')
#os.system('modprobe w1-therm')

class TempSensor:
    
    def __init__(self, sensor_id):
        self.sensor_id = sensor_id
        self.temperature = -100
        self.target = 38
        
    def get_temperature(self):
        #tmp_file = open("/sys/bus/w1/" + self.sensor_id + "/w1_slave")
        #tmp_text = tmp_file.read()
        #tmp_file.close()
        
        #tmp_data = tmp_text.split("\n")[1].split(" ")[9]
        #temperature = float(tmp_data[2:])
        #temperature = temperature / 1000
        print("Succesfully read the temperature from the sensor.")
        return self.temperature
    
    def set_target(self, target_temperature):
        self.target = target_temperature
        return
    
    def get_target(self):
        return self.target

    def is_warm(self):
        self.get_temperature()
        if self.temperature < self.target:
            return False
        else:
            return True
        
    
    
    
