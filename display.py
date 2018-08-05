from datetime import datetime
import threading
import time
import RPi_I2C_LCD
import queue
import serial


class DisplayThread(threading.Thread):
    def __init__(self, out_display_q):
        threading.Thread.__init__(self)
        self.lcd = RPi_I2C_LCD.LCD()
        self.lcd.set_backlight(True)
        self.data_q = out_display_q
        self.data = 0
        self.ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=5)
        self.ser.reset_input_buffer()
        self.ser.readline()

    def draw(self):
        try:
            if not self.data_q.empty():
                self.data = self.data_q.get()

        except:
            print("Can't get the data from queue. (display)")

        self.lcd.set_cursor(row=0, col=0)
        #self.lcd.message(datetime.now().strftime('%H:%M'))  # HH:MM
        self.lcd.message(str(self.waterLevel()))
        #print(self.waterLevel())

        self.lcd.set_cursor(row=0, col=10)
        # Temperature formatted to one decimal
        self.lcd.message(format(self.data["temp_high"],
                                '.1f') + chr(223) + "C ")

       # self.lcd.set_cursor(row=1, col=0)
       # self.lcd.message("->" + datetime.fromtimestamp(
       #     int(self.data["estimate"])).strftime('%H:%M '))  # HH:MM

        self.lcd.set_cursor(row=1, col=0)
        self.lcd.message(self.data["warming_phase"] + "    ")

        self.lcd.set_cursor(row=1, col=10)
        self.lcd.message(format(self.data["target"], '.1f') + chr(223) + "C ")

    def waterLevel(self):
        value = float(self.ser.readline().decode().strip('\r\n'))
        if(value < 0.5):
            value = 0.5
        psi = 5*(value-0.5)/(5-0.5)
        pa = psi*6894.76
        height_cm = 100*(pa / (1000*9.81)) + 5 # offset
        print(height_cm)
        return format(height_cm, '.1f')
        

    def run(self):

        self.lcd.clear()
        self.lcd.set_cursor(row=0, col=0)
        self.lcd.message("PaljuPi Beta")
        time.sleep(1)
        self.lcd.clear()

        while True:
            try:
                self.draw()
            except:
                continue
