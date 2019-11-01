import math
from .DetectionModel import DetectionResult


class VisualObject():

    # camera is 62.2 degrees wide
    CAMERA_FOV = math.radians(62.2)
    FORWARD_DIRECTION = 0
    FOCAL_CONSTANT = 100

    def __init__(self, real_size=None, detection_model=None, result_limit=None, resolution=None):
        self.resolution = resolution

        # real_size <tupe<float, float, float>>
        # real size of object needing detection in metres
        self.real_size = real_size or (1, 1, 1)

        # detection_model <DetectionModel>
        # the model to be used by the vision system for detection of this object
        self.detection_model = detection_model

        # bearings_distances <[tuple<float, float>]>
        # the bearings, and distances respectively of the detected objects
        # in radians estimated from the camera's center of translation (for convenience),
        # with the center of vision located at pi radians.
        # listed in order of likelihood to be the correct object
        self.bearings_distances = []

        # detection_results <[DetectionResult]>
        # the raw detection results that were returned from the model
        self.detection_results = []

        self.result_limit = result_limit

    def update_with_frame(self, frame):
        self.detection_results = self.detection_model.apply(frame)
        self.detection_results = sorted(
            self.detection_results, key=lambda result: -result.area())
        if self.result_limit is not None:
            self.detection_results = self.detection_results[0:self.result_limit]
        self.bearings_distances = []

        real_x, real_y, real_z = self.real_size
        avg_real_width = (real_x + real_y) / 2

        for result in self.detection_results:
            if len(result.coords) == 2:
                ((x1, y1), (x2, y2)) = result.coords
                x, y = (x1 + x2) / 2, (y1 + y2) / 2

                x = x / self.resolution[0] - 0.5
                y = y / self.resolution[1] - 0.5
                # front-facing cam
                # bearing = ((x1 + x2) / 2 / self.resolution[0] - 0.5) \
                #     * self.CAMERA_FOV + self.FORWARD_DIRECTION

                # omni-cam
                bearing = math.atan2(y, x)
                pixel_width = x2 - x1
                pixel_height = y2 - y1

                # get the most likely distance as the biggest one between the width and height,
                # so that if half of the mask is blocked - it has less of an effect
                distance = self.FOCAL_CONSTANT * max(
                    real_z / pixel_height if pixel_height > 0 else 0,
                    avg_real_width / pixel_width if pixel_width > 0 else 0
                )

                self.bearings_distances.append((bearing, distance))
            elif len(result.coords) == 4:  # TODO: redo this especially WTF
                bearing = result.bearing
                # bearing = math.pi - result.bearing
                # bearing = result.bearing + math.pi / 2
                # bearing = 2 * math.pi + bearing if bearing < -math.pi else bearing
                # bearing = bearing - 2 * math.pi if bearing > math.pi else bearing
                self.bearings_distances.append(
                    (bearing, result.distance + avg_real_width / 2))
            else:
                raise Exception("result type not supported")

        return self.detection_results, self.bearings_distances
