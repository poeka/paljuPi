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
        self.lastChange = int(time.time())
        self.view = 0

    def draw(self):
        try:
            if not self.data_q.empty():
                self.data = self.data_q.get()

        except:
            print("Can't get the data from queue. (display)")

        if self.lastChange + 5 <= int(time.time()):

            self.lastChange = int(time.time())
            self.lcd.clear()

            if self.view == 0:
                self.view = 1
            else:
                self.view = 0

        elif self.view == 0:

            self.lcd.set_cursor(row=0, col=0)
            self.lcd.message(datetime.now().strftime('%H:%M'))  # HH:MM

            self.lcd.set_cursor(row=0, col=11)
            self.lcd.message(self.data["warming_phase"] + "  ")

            self.lcd.set_cursor(row=1, col=0)
            self.lcd.message(format(self.data["temp_high"],
                                    '.1f') + chr(223) + "C ")

            self.lcd.set_cursor(row=1, col=10)
            self.lcd.message(
                format(self.data["target"], '.1f') + chr(223) + "C ")

        elif self.view == 1:

            self.lcd.set_cursor(row=0, col=0)
            self.lcd.message(datetime.now().strftime('%H:%M'))  # HH:MM

            self.lcd.set_cursor(row=0, col=11)
            self.lcd.message(self.data["warming_phase"] + "  ")

            self.lcd.set_cursor(row=1, col=0)
            self.lcd.message(str(self.data["water_level"]) + "cm")

            self.lcd.set_cursor(row=1, col=10)
            self.lcd.message(str(self.data["water_level_target"]) + "cm")

    def run(self):

        self.lcd.clear()
        self.lcd.set_cursor(row=0, col=0)
        self.lcd.message("PaljuPi RC-1")
        time.sleep(5)
        self.lcd.clear()

        while True:
            try:
                self.draw()
            except:
                continue
