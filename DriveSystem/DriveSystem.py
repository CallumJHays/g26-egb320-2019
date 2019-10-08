import math
import GPIO
import numpy as np


class MotorDriver(GPIO.PWM):

    @GPIO.dynamic_config
    def __init__(self, enable, dir1, dir2, frequency=50):
        GPIO.setup(dir1, GPIO.OUT)
        self.dir1_pin = dir1
        GPIO.setup(dir2, GPIO.OUT)
        self.dir2_pin = dir2

        super().__init__(enable, frequency)

    def drive(self, speed):
        """
        Generic drive function that will power a motor at variable voltage modulation and therefore speed via PWM

        args:
            - speed: (float) from -1.0 (full speed backwards) to 1.0 (full speed forwards)
        """
        dir = speed >= 0
        GPIO.output(self.dir1_pin, dir)
        GPIO.output(self.dir2_pin, not dir)
        self.ChangeDutyCycle(abs(speed) * 100)


class DriveSystem(GPIO.GPIODevice):

    BACK = MotorDriver(enable=19, dir1=13, dir2=26)
    FRONT_LEFT = MotorDriver(enable=6, dir1=5, dir2=12)
    FRONT_RIGHT = MotorDriver(enable=20, dir1=21, dir2=16)

    config = {
        'FRONT_LEFT': FRONT_LEFT,
        'FRONT_RIGHT': FRONT_RIGHT,
        'BACK': BACK
    }

    def set_desired_motion(self, x, y, omega):
        "Power the motors in such a way that theoretically we achieve the desired translational acceleration and rotational velocity (omega)"
        # copying http://mate.tue.nl/mate/pdfs/7566.pdf
        DIST_WHEEL_2_CENTER = 0.09
        WHEEL_RADIUS = 0.04
        A1, A2, A3 = 20, 160, 270

        # only using local frame, therefore local-global translation angle (theta) is 0

        def wheel_omega(wheel_angle):
            radians = math.pi * wheel_angle / 180
            return (
                math.sin(radians) * x +
                math.cos(radians) * y +
                DIST_WHEEL_2_CENTER * omega
            ) / WHEEL_RADIUS

        print('set desired motion', x, y, omega)

        self.drive_motors(
            wheel_omega(A1),
            wheel_omega(A2),
            wheel_omega(A3)
        )

    def drive_motors(self, a, b, c):
        """
        Drives the motors using PWM and toggling the enable pins

        """
        abss = (abs(a), abs(b), abs(c))
        # rescale by the maximum allowable pwm
        if abss[0] > 1 or abss[1] > 1 or abss[2] > 1:
            max_ = max(abss)
            a /= max_
            b /= max_
            c /= max_

        print(a, b, c)

        self.FRONT_LEFT.drive(a)
        self.FRONT_RIGHT.drive(b)
        self.BACK.drive(c)
