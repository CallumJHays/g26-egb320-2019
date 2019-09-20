import math
import GPIO

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

    BACK = MotorDriver(enable=19, dir1=13, dir2 =26)
    FRONT_LEFT = MotorDriver(enable=6, dir1 = 5, dir2 = 12)
    FRONT_RIGHT = MotorDriver(enable=20, dir1=16, dir2 = 21)
    
    
    config = {
        'FRONT_LEFT': FRONT_LEFT,
        'FRONT_RIGHT': FRONT_RIGHT,
        'BACK': BACK
    }
    

    def set_desired_motion(self, x, y, omega):
        "Power the motors in such a way that theoretically we achieve the desired translational acceleration and rotational velocity (omega)"
        FWD_SPEED = 90
        ROT_SPEED = 25

        # if omega != 0:
        #     speedFR = ROT_SPEED / 255
        #     speedFL = ROT_SPEED / 255
        #     speedB = ROT_SPEED / 255
        #     if omega < 0:
        #         speedFR = -speedFR
        #         speedFL = -speedFL
        #         speedB = -speedB
        # else:
        #     if x == 0:
        #         if y > 0:
        #             print("go right")
        #             dir_angle = 1.57
        #         elif y < 0:
        #             print("go left")
        #             dir_angle = 4.71
        #         else:
        #             dir_angle = 0
        #     else:
        #         dir_angle = math.atan(y/x)
        #     #print(dir_angle)
            
        #     theta1 = math.pi / 9
        #     theta2 = 8 * math.pi / 9
        #     theta3 = 3 * math.pi / 2
            
        #     FR = math.cos(theta1 - dir_angle)
        #     FL = math.cos(theta2 - dir_angle)
        #     B = math.cos(theta3 - dir_angle)
        #     #print("front right   " , FR)
        #     #print("front left   " , FL)
        #     #print("front back   " , B)
            
        #     #pwmfloor = 127;
        #     speedFR = abs(FR * 255 * 0.5) / 255#+ pwmfloor
        #     speedFL = abs(FL * 255 * 0.5) / 255#+ pwmfloor
        #     speedB = abs(B * 255 * 0.5) / 255 #+ pwmfloor
        
        if y != 0:
            speedB = 0
            speedFL = FWD_SPEED / 255
            speedFR = -1 * ( FWD_SPEED / 255 )
            if y < 0:
                speedB = 0
                speedFL = -1 * (FWD_SPEED / 255)
                speedFR = ( FWD_SPEED / 255 )
        elif omega != 0:
            speedFR = ROT_SPEED / 255
            speedFL = ROT_SPEED / 255
            speedB = ROT_SPEED / 255
            if omega < 0:
                speedFR = -speedFR
                speedFL = -speedFL
                speedB = -speedB
        else:
            speedFR = 0
            speedFL = 0
            speedB = 0

        # 40 slow
        self.drive_motors(speedFL, speedFR, speedB)

    
    def drive_motors(self, a, b, c):
        """
        Drives the motors using PWM and toggling the enable pins
        
        """
        # obviously, this is not correct
        self.FRONT_LEFT.drive(a)
        self.FRONT_RIGHT.drive(b)
        self.BACK.drive(c)
