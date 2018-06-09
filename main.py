import RPi.GPIO as GPIO
import time
import datetime
import os
import configparser
import queue
import pool
import display
import socketClient


config = configparser.ConfigParser()
config.read('/home/pi/Documents/PaljuPi/config.ini')
url = config['server']['url']

date = datetime.datetime.now().strftime("%Y-%m-%d")
path = config['logfile']['path'] + '/' + \
    date + "/log.txt"  # Path for a log file
os.makedirs(os.path.dirname(path), exist_ok=True)

# Using GPIO.BOARD pin numbering
GPIO.setmode(GPIO.BOARD)

# Queue which inholds the messages that are coming from websocket
in_ws_q = queue.Queue(5)
# Queue which inholds the messages that are going out through websocket
out_display_q = queue.Queue(1)
# Queue which inholds the messages that are going for display(s)
out_ws_q = queue.Queue(1)

pool = pool.Pool(in_ws_q, out_ws_q, out_display_q)

socket = socketClient.SocketThread(url, in_ws_q, out_ws_q)
socket.start()

display = display.DisplayThread(out_display_q)
display.start()


def data_in_handler():

    # WIP: How to handle the data from websocket cleanly?
    data_in = 0

    if not in_ws_q.empty():
        data_in = in_ws_q.get()

        if pool.get_state() == "FOFF":
            if data_in["warming_phase"] == "ON":
                pool.set_state("ON")

        elif data_in["warming_phase"] == "FOFF":
            pool.set_state("FOFF")

        pool.set_target(data_in["target"])
        pool.set_lower_limit(data_in["low_limit"])
        pool.set_estimate(data_in["estimation"])


while True:

    try:
        data_in_handler()
    except:
        print("Error while handling the websocket data")

    if pool.floatSwitch.get_state() == 0:
        pool.get_temperatures()
        pool.data_out()  # Tell the pool to fill the outgoing queues with new data (if empty)

        if pool.get_state() != "FOFF":
            pool.set_state("OFF")

        continue

    elif pool.floatSwitch.get_state() == 1:
        pool.data_out()  # Tell the pool to fill the outgoing queues with new data (if empty)

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
