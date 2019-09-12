import math
from GPIO import GPIODevice, GPIO

class MotorDriver(GPIODevice, GPIO.PWM):

    def __init__(self, enable, dir, frequency=50):
        self.config = {
            'enable': (enable, GPIO.OUT),
            'dir': (dir, GPIO.OUT)
        }

        super().__init__(self.enable, frequency)


class DriveSystem(GPIODevice):

    SPEED_TUNER_CONSTANT = 1
    ROTATION_VEL_2_ACC_TUNER_CONSTANT = 5
    LENGTH_CENTER_2_WHEEL = 0.08 # m

    config = {
        # motor
        'MotorA': MotorDriver(enable=13, dir=6),
        'MotorB': MotorDriver(enable=5, dir=12),
        'MotorC': MotorDriver(enable=19, dir=26)
    }
    

    def set_desired_motion(self, accel, omega, speed_modifier=1):
        "Converts accel"
        self.drive_motors(0, 0, 0)

    
    def drive_motors(self, a, b, c, speed_modifier=1):
        """
        Drives the motors using PWM and toggling the enable pins
        
        """
        pass