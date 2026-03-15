import RPi.GPIO as GPIO


class Filter:
    def __init__(self):
        GPIO.setup(13, GPIO.OUT)
        GPIO.output(13, GPIO.HIGH)

    def toggle_on(self):
        GPIO.output(13, GPIO.LOW)  # LOW is ON
        return

    def toggle_off(self):
        GPIO.output(13, GPIO.HIGH)  # HIGH is OFF
        return
