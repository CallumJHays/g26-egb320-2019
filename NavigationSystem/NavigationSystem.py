import numpy as np
import math
from time import sleep


FORWARD_DIR = -np.pi / 2


class NavigationSystem():

    def __init__(self, vision_system, drive_system, kicker_dribbler):
        self.vision_system = vision_system
        self.drive_system = drive_system
        self.kick = kicker_dribbler
        self.goal = 'blue'
        self.state = None
        self.state_params = (),

    def update(self, ball_rb, yellow_rb, blue_rb, obstacles_rb):

        ranges_bearings = {
            'ball': ball_rb,
            'yellow': yellow_rb,
            'blue': blue_rb,
            'obstacle': obstacles_rb
        }
        ranges_bearings['goal'] = ranges_bearings[self.goal]
        # range within which something is considered straight ahead

        def set_state(fun, *args):
            if fun is None:
                self.drive_system.set_desired_motion(0, 0, 0)
            self.state = fun
            self.state_params = args

        if self.state is None:
            if ball_rb:
                def go_to_ball(_rbs):
                    return set_state(goto_object_at_range,
                                     go_around_ball, 'ball', 0.3)

                def go_around_ball(_rbs):
                    return set_state(translate_around_obj_at_range_lining_up_objects,
                                     line_up_shot, 'ball', 0.3, 'goal')

                def line_up_shot(rbs):
                    if rbs['ball'] is not None:
                        obj_range, obj_bear = rbs['ball']
                        diff = reorient(obj_bear - FORWARD_DIR)
                        if not is_straight(diff):
                            return set_state(rotate_towards_obj, line_up_shot, 'ball')

                        if obj_range > 0.2:
                            return set_state(goto_object_at_range, line_up_shot, 'ball', 0.2)

                        self.kick.start_dribbling()
                        return set_state(motion_until_object_visibility_change, kick_ball, (0, 0.1, 0), 'ball', False)

                def kick_ball(_rbs):
                    self.kick.start_kicking()
                    return set_state(motion_until_object_visibility_change, stop_kicking, (0, 0, 0), 'ball', True)

                def stop_kicking(_rbs):
                    self.kick.stop_dribbling()
                    self.kick.stop_kicking()
                    return set_state(None)

                go_to_ball(ranges_bearings)

        if self.state:
            desired_motion = self.state(ranges_bearings, *self.state_params)
            self.drive_system.set_desired_motion(*desired_motion)


def goto_object_at_range(rbs, on_done, obj, range):
    if rbs[obj] is not None:
        obj_range, obj_bear = rbs[obj]

        if obj_range <= range:
            return on_done(rbs)

        speed = 1 if obj_range > (range + 0.3) else (obj_range / (range + 0.3))

        x = -np.cos(obj_bear) * speed
        y = -np.sin(obj_bear) * speed

        return x, y, 0
    else:
        return 0, 0, 0


def translate_around_obj_at_range_lining_up_objects(rbs, on_done, obj, range, lineup):
    print("Translating to align ball with goal")
    if rbs[obj] is not None and rbs[lineup] is not None:
        _, obj_bear = rbs[obj]

        _, lineup_bear = rbs[lineup]
        diff = reorient(lineup_bear - obj_bear)

        # travel_angle = 0
        # # if diff < 0 and obj_bear >= math.pi / 2 and obj_bear <= 0.999 * math.pi and lineup_bear < math.pi / 2:
        # #     travel_angle = obj_bear - 0.57
        # # elif diff > 0 and lineup_bear >= math.pi / 2 and lineup_bear <= 0.999 * math.pi and obj_bear < math.pi / 2:
        # #     travel_angle = obj_bear + 0.57
        # if diff < 0:
        #     travel_angle = obj_bear + 0.57
        # else:
        #     travel_angle = obj_bear - 0.57

        travel_angle = obj_bear + (np.pi if diff > 0 else -np.pi) / 2

        if is_straight(diff):
            return on_done(rbs)

        x = -np.cos(travel_angle) * abs(diff) * 0.2
        y = -np.sin(travel_angle) * abs(diff) * 0.2

        return x, y, 0
    else:
        return 0, 0, 0


def rotate_towards_obj(rbs, on_done, obj):
    print("Aligning robot with ball")
    if rbs[obj] is not None:
        _obj_range, obj_bear = rbs[obj]

        diff = reorient(obj_bear - FORWARD_DIR)

        if is_straight(diff):
            return on_done(rbs)
        else:
            return 0, 0, 0.02 * diff
    #     diff = obj_bear - FORWARD_DIR
    #     # if abs(diff) > np.pi:
    #     #     diff -= 2 * np.pi

    #     print('rotate on diff', diff)

    #     if is_straight(diff):
    #         on_done()

    #     sign = -1 if diff < 0 else 1

    #     omega = sign * max(0.02 * abs(diff), 0.07)

    #     print('omega', omega)

    return 0, 0, 0


def motion_until_object_visibility_change(rbs, on_done, motion, obj, target_visibility):
    if (rbs[obj] is not None) == target_visibility:
        return on_done()
    return motion


def is_straight(angle):
    return abs(angle) < 0.1


def reorient(angle):
    return angle % (2 * np.pi) - np.pi
