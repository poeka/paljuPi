import RPi.GPIO as GPIO


class Filter:
    def __init__(self):
        GPIO.setup(18, GPIO.OUT)
        GPIO.output(18, GPIO.HIGH)

    def toggle_on(self):
        GPIO.output(18, GPIO.LOW)  # LOW is ON
        return

    def toggle_off(self):
        GPIO.output(18, GPIO.HIGH)  # HIGH is OFF
        return
