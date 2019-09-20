import numpy as np
import math


class NavigationSystem():

    GOAL_P = 0.5
    MAX_ROBOT_ROT = 1
    MAX_ROBOT_VEL = 0.05
    COBEARING = 1
    blueRange = 0


    def __init__(self, vision_system, drive_system, kicker_dribbler, debug_print):
        self.vision_system = vision_system
        self.drive_system = drive_system
        self.headingRad = 0
        self.goal_found = False
        self.lastHeading = 0.4
        self.kicker_dribbler = kicker_dribbler
        self.debug_print = debug_print


    def update(self):
        ballRB, blueRB, yellowRB, obstaclesRB = self.get_vision_results_vrep_format()
        BALL_IN_DRIBBLER_RB = (0.03, 0.3)
        ball_in_dribbler = ballRB and ballRB[0] < BALL_IN_DRIBBLER_RB and abs(ballRB) < BALL_IN_DRIBBLER_RB[1]
        ball_in_dribbler = False
        
        yellowRB = [0.5, 0.1]
        ballRB = [0.6, 0.3]

        if ball_in_dribbler == False: # or !ball_in_dribbler
            if yellowRB != None:
                yellowRange = yellowRB[0]
                yellowBear = yellowRB[1]
                print(yellowRange)
                print(yellowBear)
                
                # Check to see if the ball is within the camera's FOV
                if ballRB != None:
                    ballRange = ballRB[0]
                    ballBearing = ballRB[1]
                    print("\nBall (range, bearing): %0.4f"%ballBearing)
                    
                    if ballBearing > 0.4:
                        self.drive_system.set_desired_motion(0, 0.1, yellowBear * self.COBEARING)
                        print("go left")
                    elif ballBearing <= 0.4 and ballBearing > 0.2:
                        self.drive_system.set_desired_motion(0.1, 0.1, yellowBear * self.COBEARING)
                        print("go up and left")
                    elif ballBearing <= 0.2 and ballBearing > 0:
                        self.drive_system.set_desired_motion(0.1, 0, yellowBear * self.COBEARING)
                        print("go straight")
                    elif ballBearing <= 0 and ballBearing > -0.2:
                        self.drive_system.set_desired_motion(0.1, 0, yellowBear * self.COBEARING)
                        print("go straight")
                    elif ballBearing <= -0.2 and ballBearing > -0.4:
                        self.drive_system.set_desired_motion(0.1, -0.1, yellowBear * self.COBEARING)
                        print("go up and right")
                    elif ballBearing <= -0.4:
                        self.drive_system.set_desired_motion(0, -0.1, yellowBear * self.COBEARING)
                        print("go right")
                    else:
                        self.drive_system.set_desired_motion(0, 0, 0.5)
                        print("rotate")
                else:
                    self.drive_system.set_desired_motion(0, 0, 0.5)
        #
        
    def get_vision_results_vrep_format(self):
        objs = self.vision_system.objects_to_track # for shorthand

        def vrep_format(bearings_distances, multi=False):
            if any(bearings_distances):
                if multi:
                    return bearings_distances[::-1]
                else:
                    return bearings_distances[0][::-1]
            else:
                return None

        return (
            vrep_format(objs["ball"].bearings_distances),
            vrep_format(objs["blue_goal"].bearings_distances),
            vrep_format(objs["yellow_goal"].bearings_distances),
            vrep_format(objs["obstacle"].bearings_distances, multi=True),
        )