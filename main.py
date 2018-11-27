import RPi.GPIO as GPIO
import time
import datetime
import os
import configparser
import queue

from pool import Pool
from display import DisplayThread
from socketClient import SocketThread


config = configparser.ConfigParser()
config.read('/home/pi/Documents/PaljuPi/config.ini')
url = config['server']['url']

#date = datetime.datetime.now().strftime("%Y-%m-%d")
# path = config['logfile']['path'] + '/' + \
#    date + "/log.txt"  # Path for a log file
#os.makedirs(os.path.dirname(path), exist_ok=True)

# Using GPIO.BOARD pin numbering
GPIO.setmode(GPIO.BOARD)

# Queue which inholds the messages that are coming from websocket
in_ws_q = queue.Queue(5)
# Queue which inholds the messages that are going out through websocket
out_display_q = queue.Queue(1)
# Queue which inholds the messages that are going for display(s)
out_ws_q = queue.Queue(1)

pool = Pool(in_ws_q, out_ws_q, out_display_q)

socket = SocketThread(url, in_ws_q, out_ws_q)
socket.start()

display = DisplayThread(out_display_q)
display.start()

while True:

    try:
        pool.data_in()   # Handle the incoming data
        pool.data_out()  # Fill the outgoing queues with new data (if empty)
    except:
        print("Error while handling the websocket data")

    if pool.get_water_level() != -1:

        if pool.get_water_level() < pool.get_water_level_target():
            pool.open_valve()

        elif pool.get_water_level() >= pool.get_water_level_target():
            pool.close_valve()

    if pool.floatSwitch.get_state() == 0:
        pool.get_temperatures()
        pool.read_water_level()

        if pool.get_state() != pool.FOFF:
            pool.set_state(pool.OFF)

        continue

    elif pool.floatSwitch.get_state() == 1:
        pool.read_water_level()

        if pool.get_state() == pool.FOFF:
            pool.get_temperatures()
            continue

        elif pool.get_state() == pool.ON:

            if pool.get_temperatures() is False:
                print("Error reading the temperatures")
                continue

            elif pool.get_temp_high() < pool.get_target():
                pool.set_state(pool.ON)
                continue

            elif pool.get_temp_high() >= pool.get_target():
                pool.set_state(pool.UPKEEP)
                continue

        elif pool.get_state() == pool.UPKEEP:

            if pool.get_temperatures() is False:
                print("Error reading the temperatures")
                continue

            elif pool.get_temp_high() <= pool.get_lower_limit():
                pool.set_state(pool.ON)
                continue

        elif pool.get_state() == pool.OFF:

            if pool.get_temperatures() is False:
                print("Error reading the temperatures")
                continue

            elif pool.get_temp_high() <= pool.get_lower_limit():
                pool.set_state(pool.ON)
                continue
