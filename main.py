import time
import temp


temp = temp.TempSensor("12345")


while True:

    if temp.is_warm():

        #Turn the relay OFF

        print("Water has reached the target temperature.")
        
        time.sleep(10)

    else:
        print("Not warm yet.")
        time.sleep(10)
    
            
