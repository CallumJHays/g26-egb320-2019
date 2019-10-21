import numpy as np
import math


class NavigationSystem():

    def __init__(self, vision_system, drive_system, kicker_dribbler):
        self.drive = drive_system
        self.kicker = kicker_dribbler

    def update(self):
        # range within which something is considered straight ahead
        def is_straight(angle): return abs(angle) < 0.05

        ballRB, blueBR, yellowBR, obsBRs = self.get_vision_results_vrep_format()

        # if we can see both the ball and the goal
        if goalRB and goalRB[1] < 10:
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
        objs = self.vision.objects_to_track  # for shorthand

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
