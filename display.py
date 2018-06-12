from datetime import datetime
import threading
import time
import RPi_I2C_LCD
import queue


class DisplayThread(threading.Thread):
    def __init__(self, out_display_q):
        threading.Thread.__init__(self)
        self.lcd = RPi_I2C_LCD.LCD()
        self.lcd.set_backlight(True)
        self.data_q = out_display_q
        self.data = 0

    def draw(self):
        try:
            if not self.data_q.empty():
                self.data = self.data_q.get()

        except:
            print("Can't get the data from queue. (display)")

        self.lcd.set_cursor(row=0, col=0)
        self.lcd.message(datetime.now().strftime('%H:%M'))  # HH:MM

        self.lcd.set_cursor(row=0, col=10)
        # Temperature formatted to one decimal
        self.lcd.message(format(self.data["temp_high"],
                                '.1f') + chr(223) + "C ")

       # self.lcd.set_cursor(row=1, col=0)
       # self.lcd.message("->" + datetime.fromtimestamp(
       #     int(self.data["estimate"])).strftime('%H:%M '))  # HH:MM

        self.lcd.set_cursor(row=1, col=0)
        self.lcd.message(self.data["warming_phase"] + "  ")

        self.lcd.set_cursor(row=1, col=6)
        self.lcd.message(
            "TGT:" + format(self.data["target"], '.1f') + chr(223) + "C ")

    def run(self):

        while True:
            try:
                self.draw()
            except:
                continue
