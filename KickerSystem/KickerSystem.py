import GPIO
import time


class KickerSystem(GPIO.GPIODevice):

    KICK_ENABLE = 23
    DRIBBLE_ENABLE = 24
    LASERGATE = 25
    DRIVE_OFF =  22


    config = {
        KICK_ENABLE: GPIO.OUT,
        DRIBBLE_ENABLE: GPIO.OUT,
        LASERGATE: GPIO.IN,
        DRIVE_OFF: GPIO.OUT
    }


    def start_dribbling(self):
        GPIO.output(self.DRIBBLE_ENABLE, True)


    def stop_dribbling(self):
        GPIO.output(self.DRIBBLE_ENABLE, False)


    def start_kicking(self):
        GPIO.output(self.KICK_ENABLE, True)
        GPIO.output(self.DRIVE_OFF, True)


    def stop_kicking(self):
        GPIO.output(self.KICK_ENABLE, False)
        GPIO.output(self.DRIVE_OFF, False)
