import floatSwitch
import pool
import relay
import RPi.GPIO as GPIO
import socketClient

GPIO.setmode(GPIO.BOARD)
relay = relay.Relay()
floatSwitch = floatSwitch.FloatSwitch()
pool = pool.Pool()

socket = socketClient.SocketThread(pool)
socket.start()

while True:

    if floatSwitch.get_state() == 0:

        relay.toggle_off()

        pool.set_state("OFF")

        pool.get_temperatures()

        continue

    elif floatSwitch.get_state() == 1:

        if pool.get_state() == "FORCEOFF":
            continue

        elif pool.get_state() == "ON" or "OFF":

            if pool.get_temperatures() is False:

                print("Error reading the temperatures")
                continue

            elif pool.get_temp_high() < pool.get_target():

                relay.toggle_on()
                pool.set_state("ON")
                continue

            elif pool.get_temp_high() >= pool.get_target():

                relay.toggle_off()
                pool.set_state("UPKEEP")
                continue

        elif pool.get_state() == "UPKEEP":
            if pool.get_temperatures() is False:

                print("Error reading the temperatures")
                continue

            elif pool.get_temp_high() <= pool.lower_limit:

                relay.toggle_on()
                pool.set_state("ON")
                continue
