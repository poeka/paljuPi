import RPi.GPIO as GPIO


class MagneticValve:
    def __init__(self):
        GPIO.setup(13, GPIO.OUT)
        GPIO.output(13, GPIO.HIGH)

    def open(self):
        GPIO.output(13, GPIO.LOW)  # LOW is ON
        return

    def close(self):
        GPIO.output(13, GPIO.HIGH)  # HIGH is OFF
        return
