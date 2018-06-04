import threading
import time
import pool
import relay
import RPi_I2C_LCD
from datetime import datetime


class DisplayThread(threading.Thread):
    def __init__(self, pool):
        threading.Thread.__init__(self)
        self.lcd = RPi_I2C_LCD.LCD()
        self.pool = pool

    def run(self):

        self.lcd.set_backlight(True)

        while True:

            self.lcd.set_cursor(row=0)
            self.lcd.message(datetime.now().strftime('%H:%M:%S'))  # HH:MM:SS

            self.lcd.set_cursor(row=0, col=10)
            # Temperature formatted to one decimal
            self.lcd.message(format(self.pool.get_temp_high(),
                                    '.1f') + chr(223) + "C ")

            self.lcd.set_cursor(row=0, col=0)
            self.lcd.message("->" + datetime.fromtimestamp(
                int(self.pool.get_estimate())).strftime('%H:%M '))  # HH:MM
