import serial


class PressureSender:
    def __init__(self):
        self.water_level = 0
        self.set = False
        self.ser = -1

    def get_state(self):
        return self.set

    def get_water_level(self):

        if self.set == False:
            try:
                self.ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=5)
                self.ser.reset_input_buffer()
                self.ser.readline()
                self.set = True
            except:
                self.set = False
                self.water_level = -1
                return self.water_level

        offset = 5
        try:
            value = float(self.ser.readline().decode().strip('\r\n'))
            if value == 0:
                return self.water_level
        except:
            return self.water_level

        if(value < 0.5):
            value = 0.5
            offset = 0
        psi = 5*(value-0.5)/(4.5-0.5)
        pa = psi*6894.76  # 1 psi is 6894.76 pascals
        h_cm = 100*(pa / (997*9.81)) + offset
        print(h_cm)
        self.water_level = format(h_cm, '.1f')
        return self.water_level
