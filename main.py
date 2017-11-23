import time
import temp


temp = temp.TempSensor("12345")


while True:
    
    temperature = temp.get_temperature()
    target = temp.get_target()
    
    if temperature < target:
    
        print("Ei ole vielä lämmintä")
        
        time.sleep(10)
        
    
            
