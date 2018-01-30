import threading
import time
import pool
import relay


class DisplayThread(threading.Thread):
    def __init__(self, pool, relay, floatswitch):
        threading.Thread.__init__(self)
        self.pool = pool
        self.relay = relay
        self.floatswitch = floatswitch

    def run(self):

        while True:
            # Draw to display
            # Remember to use get_temp1 and get_temp2
            print("Drawing to display")
            time.sleep(1)



