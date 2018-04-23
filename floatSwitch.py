import RPi.GPIO as GPIO


class FloatSwitch:
    def __init__(self):
        GPIO.setup(21, GPIO.OUT)
        GPIO.output(21, GPIO.HIGH)
        GPIO.setup(22, GPIO.IN,
                   pull_up_down=GPIO.PUD_DOWN)

    def get_state(self):
        return(GPIO.input(22))
