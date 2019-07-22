import os

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')


class TempSensor:
    def __init__(self, sensor_id):
        self._sensor_id = sensor_id
        self._temperature = -85

    def get_temperature(self):
        try:
            tmp_file = open("/sys/bus/w1/devices/" +
                            self._sensor_id + "/w1_slave")
            tmp_text = tmp_file.read()
            tmp_file.close()
            tmp_data = tmp_text.split("\n")[1].split(" ")[9]
            temperature = float(tmp_data[2:])
            self._temperature = temperature / 1000
            return self._temperature

        except IOError:
            return False
