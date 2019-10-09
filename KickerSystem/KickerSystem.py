import GPIO
import time


class KickerSystem(GPIO.GPIODevice):

    KICK_ENABLE = 23
    DRIBBLE_ENABLE = 22
    LASERGATE = 25

    config = {
        KICK_ENABLE: GPIO.OUT,
        DRIBBLE_ENABLE: GPIO.OUT,
        LASERGATE: GPIO.IN
    }

    def __init__(self):
        self.is_kicking = False

    def start_dribbling(self):
        GPIO.output(self.DRIBBLE_ENABLE, True)

    def stop_dribbling(self):
        GPIO.output(self.DRIBBLE_ENABLE, False)

    def start_kicking(self):
        self.is_kicking = True
        GPIO.output(self.KICK_ENABLE, True)

    def stop_kicking(self):
        self.is_kicking = False
        GPIO.output(self.KICK_ENABLE, False)
