import time
import pool


while True:
    
    tub = pool.Pool()

    if tub.is_warm():

        #Turn the relay OFF

        print("Water has reached the target temperature.")
        
        time.sleep(10)

    else:
        print("Not warm yet.")
        time.sleep(10)
    
            
