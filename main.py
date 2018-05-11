import pool
import RPi.GPIO as GPIO
import socketClient
import time
import datetime
import os
import configparser


config = configparser.ConfigParser()
config.read('config.ini')

date = datetime.datetime.now().strftime("%Y-%m-%d")
path = config['logfile']['path'] + '/' + \
    date + "/log.txt"  # Path for a log file
os.makedirs(os.path.dirname(path), exist_ok=True)

url = config['server']['url']

GPIO.setmode(GPIO.BOARD)
pool = pool.Pool()
socket = socketClient.SocketThread(pool, path, url)
socket.start()

while True:
    if pool.floatSwitch.get_state() == 0:

        if pool.get_state() != "FOFF":
            pool.set_state("OFF")

        pool.get_temperatures()
        continue

    elif pool.floatSwitch.get_state() == 1:

        if pool.get_state() == "FOFF":
            continue

        elif pool.get_state() == "ON":

            if pool.get_temperatures() is False:
                print("Error reading the temperatures")
                continue

            elif pool.get_temp_high() < pool.get_target():
                pool.set_state("ON")
                continue

            elif pool.get_temp_high() >= pool.get_target():
                pool.set_state("UPKEEP")
                continue

        elif pool.get_state() == "UPKEEP":

            if pool.get_temperatures() is False:
                print("Error reading the temperatures")
                continue

            elif pool.get_temp_high() <= pool.get_lower_limit():
                pool.set_state("ON")
                continue

        elif pool.get_state() == "OFF":

            if pool.get_temperatures() is False:
                print("Error reading the temperatures")
                continue

            elif pool.get_temp_high() <= pool.get_lower_limit():
                pool.set_state("ON")
                continue
