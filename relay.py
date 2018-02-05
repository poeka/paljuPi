import RPi.GPIO as GPIO


class Relay:
    def __init__(self):

        GPIO.setup(11, GPIO.OUT)
        GPIO.output(11, GPIO.HIGH)

    def toggle_on(self):
        GPIO.output(11, GPIO.LOW) # LOW is ON
        return

    def toggle_off(self):
        GPIO.output(11, GPIO.HIGH) # HIGH is OFF
        return

