import RPi.GPIO as GPIO

# First parameter is input pin, second output pin (GPIO.BOARD)
# Note that GPIO.BOARD mode has been set prior to using this class


class FloatSwitch:
    def __init__(self, input_pin, output_pin):
        self.input = input_pin
        self.output = output_pin
        GPIO.setup(self.output, GPIO.OUT)
        GPIO.output(self.output, GPIO.HIGH)  # 21
        GPIO.setup(self.input, GPIO.IN,  # 22
                   pull_up_down=GPIO.PUD_DOWN)

    def get_state(self):
        return(GPIO.input(self.input))
