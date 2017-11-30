import os
import glob
import temp


class Pool:

    def __init__(self):
        
        self.target = 38
        self.total_temperature = 0
        self.temp1 = temp.TempSensor("12345") #Sensors ID's
        self.temp2 = temp.TempSensor("23456")
        

    def get_temp1(self):
        return self.temp1.get_temperature()
    
    def get_temp2(self):
        return self.temp2.get_temperature()
    
    
    def get_temperature(self):
        self.total_temperature = (self.temp1.get_temperature() + self.temp2.get_temperature()) / 2
        return self.total_temperature
    
    def is_warm(self):     
        if self.get_temperature() >= self.target:
            return True
        else:
            return False
        

        
        
