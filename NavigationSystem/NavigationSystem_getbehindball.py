import numpy as np
import math

class NavigationSystem():

    GOAL_P = 0.5
    MAX_ROBOT_ROT = 1
    MAX_ROBOT_VEL = 0.05
    COBEARING = 1


    def __init__(self, vision_system, drive_system, kicker_dribbler, debug_print):
        self.vision_system = vision_system
        self.drive_system = drive_system
        self.headingRad = 0
        self.goal_found = False
        self.lastHeading = 0.4
        self.kicker_dribbler = kicker_dribbler
        self.debug_print = debug_print
        self.straight_steps_to_take = 0
        self.stop_and_wait_for_manual_kick = False
        self.ball_target_bear = None
        self.prepping_final_kick = False
        self.drive_straight_until_cant_see_ball = False
        self.drive_straight_n = 0
        self.behind_ball = False
        self.prev_ball_range = None
        self.cant_find_both = None
        self.count = 0


    def update(self):
        is_sane_bear = lambda bear: abs(bear) < 10
        is_straight = lambda angle: abs(angle) < 0.05 # range within which something is considered straight ahead

        ballRB, goalRB, _, _ = self.get_vision_results_vrep_format()
        if ballRB:
            if not is_sane_bear(ballRB[1]):
                ballRB = None

        if goalRB:
            if not is_sane_bear(goalRB[1]):
                goalRB = None
        print('ball', ballRB, 'goal', goalRB)

        if self.stop_and_wait_for_manual_kick:
            print('waiting for manual kick')
        elif self.drive_straight_n > 0:
            self.drive_system.set_desired_motion(0, 1, 0)
            self.drive_straight_n -= 1
        elif self.drive_straight_until_cant_see_ball:
            self.count = 0
            if ballRB:
                _, ball_bear = ballRB
                if self.ball_target_bear:
                    diff = self.ball_target_bear - ball_bear
                    if not is_straight(diff):
                        print('adjusting position while driving straight')
                        self.drive_system.set_desired_motion(0, 0, -diff)
                        return
                
                print('driving straight')
                self.drive_system.set_desired_motion(0, 1, 0)
            else:
                self.drive_straight_until_cant_see_ball = False
                if self.prepping_final_kick:
                    self.stop_and_wait_for_manual_kick = True
                else:
                    print('last seen ball range', self.prev_ball_range)
                    self.drive_straight_n = int(self.prev_ball_range / 0.01)
                    self.behind_ball = True

        elif ballRB:
            self.count = 0
            _, ball_bear = ballRB

            if self.ball_target_bear is not None:
                print('rotating untill ball is at', self.ball_target_bear, 'current:', ball_bear)
                diff = self.ball_target_bear - ball_bear
                if is_straight(diff):
                    self.ball_target_bear = None
                    if self.prepping_final_kick:
                        self.drive_straight_until_cant_see_ball = True
                    else:
                        self.drive_straight_until_cant_see_ball = True
                else:
                    self.drive_system.set_desired_motion(0, 0, -diff)

            elif goalRB == None:
                self.drive_system.set_desired_motion(0, 0, -ball_bear)

            # if we can see both the ball and the goal
            elif goalRB and goalRB[1] < 10:
                _, goal_bear = goalRB
                diff = ball_bear - goal_bear

                print('can see both the ball and the goal, angle diff:', diff)
                
                if is_straight(diff):

                    # face the ball straight on
                    self.ball_target_bear = 0
                    self.prepping_final_kick = True
                else:
                    if self.behind_ball:
                        self.ball_target_bear = 0
                    else:
                        # rotate in diff dir until ball_bear is opposite the diff
                        self.ball_target_bear = 0.5 if diff < 0 else -0.5
        else:
            print("searching for ball")
            self.drive_system.set_desired_motion(0, 0, 1)
            self.count += 1
            if self.count > 200:
                self.drive_system.set_desired_motion(0, -1, 0)
        

        if ballRB:
            self.prev_ball_range, _ = ballRB
            
        
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
            None, None
#             vrep_format(objs["yellow_goal"].bearings_distances),
#             vrep_format(objs["obstacle"].bearings_distances, multi=True),
        )