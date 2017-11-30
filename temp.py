import os
import glob
import time

#os.system('modprobe w1-gpio')
#os.system('modprobe w1-therm')

class TempSensor:
    
    def __init__(self, sensor_id):
        self.sensor_id = sensor_id
        self.temperature = -100
        
    def get_temperature(self):
        #tmp_file = open("/sys/bus/w1/" + self.sensor_id + "/w1_slave")
        #tmp_text = tmp_file.read()
        #tmp_file.close()
        
        #tmp_data = tmp_text.split("\n")[1].split(" ")[9]
        #temperature = float(tmp_data[2:])
        #temperature = temperature / 1000
        print("Succesfully read the temperature from the sensor.")
        return self.temperature

        
    
    
    
