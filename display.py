from datetime import datetime
import threading
import time
import RPi_I2C_LCD
import queue


class DisplayThread(threading.Thread):
    def __init__(self, out_display_q):
        threading.Thread.__init__(self)
        self._lcd = RPi_I2C_LCD.LCD()
        self._lcd.set_backlight(True)
        self._data_q = out_display_q
        self._data = 0
        self._lastChange = int(time.time())
        self._view = 0

    def draw(self):
        try:
            if not self._data_q.empty():
                self._data = self._data_q.get()

        except:
            print("Can't get the data from queue. (display)")

        if self._lastChange + 5 <= int(time.time()):

            self._lastChange = int(time.time())
            self._lcd.clear()

            if self._view == 0:
                self._view = 1
            else:
                self._view = 0

        elif self._view == 0:

            self._lcd.set_cursor(row=0, col=0)
            self._lcd.message(datetime.now().strftime('%H:%M'))  # HH:MM

            self._lcd.set_cursor(row=0, col=10)
            self._lcd.message(self._data["warming_phase"] + "  ")

            self._lcd.set_cursor(row=1, col=0)
            self._lcd.message(format(self._data["temp_high"],
                                     '.1f') + chr(223) + "C ")

            self._lcd.set_cursor(row=1, col=10)
            self._lcd.message(
                format(self._data["target"], '.1f') + chr(223) + "C ")

        elif self._view == 1:

            self._lcd.set_cursor(row=0, col=0)
            self._lcd.message(datetime.now().strftime('%H:%M'))  # HH:MM

            self._lcd.set_cursor(row=0, col=11)
            self._lcd.message(self._data["warming_phase"] + "  ")

            self._lcd.set_cursor(row=1, col=0)
            self._lcd.message(str(self._data["water_level"]) + "cm")

            self._lcd.set_cursor(row=1, col=10)
            self._lcd.message(str(self._data["water_level_target"]) + "cm")

    def run(self):

        self._lcd.clear()
        self._lcd.set_cursor(row=0, col=0)
        self._lcd.message("PaljuPi RC-1")
        time.sleep(5)
        self._lcd.clear()

        while True:
            try:
                self.draw()
            except:
                continue
