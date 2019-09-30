import math
from .DetectionModel import DetectionResult


class VisualObject():

    # camera is 62.2 degrees wide
    CAMERA_FOV = math.radians(62.2)
    FORWARD_DIRECTION = 0
    FOCAL_CONSTANT = 100

    def __init__(self, real_size=None,  detection_model=None, result_limit=None, camera_width=None):
        self.camera_pixel_width = camera_width

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

        real_x, real_y, _real_z = self.real_size
        avg_real_width = (real_x + real_y) / 2

        for result in self.detection_results:
            ((x1, y1), (x2, y2)) = result.coords
            bearing = ((x1 + x2) / 2 / self.camera_pixel_width - 0.5) \
                * self.CAMERA_FOV + self.FORWARD_DIRECTION
            pixel_width = x2 - x1
            pixel_height = y2 - y1

            # get the most likely distance as the biggest one between the width and height,
            # so that if half of the mask is blocked - it has less of an effect
            distance = self.FOCAL_CONSTANT * max(
                self.real_size[2] / pixel_height if pixel_height > 0 else 0,
                avg_real_width / pixel_width if pixel_width > 0 else 0
            )

            self.bearings_distances.append((bearing, distance))

        return self.detection_results, self.bearings_distances
