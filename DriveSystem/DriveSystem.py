import math
import GPIO

class MotorDriver(GPIO.GPIODevice, GPIO.PWM):

    @GPIO.dynamic_config
    def __init__(self, enable, dir, frequency=50):
        GPIO.setup(dir, GPIO.OUT)
        self.dir_pin = dir

        super().__init__(enable, frequency)


    def drive(self, speed):
        """
        Generic drive function that will power a motor at variable voltage modulation and therefore speed via PWM

        args:
            - speed: (float) from -1.0 (full speed backwards) to 1.0 (full speed forwards)
        """
        GPIO.output(self.dir_pin, speed >= 0)
        self.ChangeDutyCycle(abs(speed) * 100)
            


class DriveSystem(GPIO.GPIODevice):

    SPEED_TUNER_CONSTANT = 1
    ROTATION_VEL_2_ACC_TUNER_CONSTANT = 5
    LENGTH_CENTER_2_WHEEL = 0.08 # m

    FRONT_LEFT = MotorDriver(enable=13, dir=6)
    FRONT_RIGHT = MotorDriver(enable=5, dir=12)
    BACK = MotorDriver(enable=19, dir=26)

    config = {
        'FRONT_LEFT': FRONT_LEFT,
        'FRONT_RIGHT': FRONT_RIGHT,
        'BACK': BACK
    }
    

    def set_desired_motion(self, accel, omega):
        "Power the motors in such a way that theoretically we achieve the desired translational acceleration and rotational velocity (omega)"
        self.drive_motors(0, 0, 0)

    
    def drive_motors(self, a, b, c):
        """
        Drives the motors using PWM and toggling the enable pins
        
        """
        # obviously, this is not correct
        self.FRONT_LEFT.drive(a)
        self.FRONT_RIGHT.drive(b)
        self.BACK.drive(c)

if __name__ == "__main__":
    import signal

    # shut up and drive
    drive_system = DriveSystem()
    drive_system.drive_motors(1, 1, 1)

    # PWM stops when the program ends - so lets just let the OS know
    # we're waiting until we die (from a Ctrl+C keyboard event)
    signal.pause()
    