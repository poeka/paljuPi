import RPi.GPIO as GPIO
import time
import datetime
import os
import configparser
import queue

from pool import Pool
from display import DisplayThread
from socketClient import SocketThread
from statePattern import Context, On, Off, Upkeep, Foff

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

context = Context()

while True:

    try:
        context.work(pool)
        pool.get_temperatures()
        pool.read_water_level()
        pool.filter_anti_freeze()

        pool.data_in()   # Handle the incoming data
        pool.data_out()  # Fill the outgoing queues with new data (if empty)

    except:
        print("Something went wrong.")
