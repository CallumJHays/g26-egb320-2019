from ..DetectionModel import DetectionModel
from ..DetectionResult import DetectionResult
from .Thresholder import Thresholder
import cv2
import pickle
import numpy as np
import os
from numpy import *

# point of the center of the camera in the image at full resolution (1664, 1232) with crop=((0.13, 0), (.9, 1))
CX, CY = (637, 639)
MAX_X, MAX_Y = int(1664 * (0.9 - 0.13)), 1232

IGNORE_MASK = cv2.imread(os.path.join(
    os.path.dirname(__file__), 'ignore_mask.png'))[:, :, 0]


def convert_img_dist_to_real_dist(img_dist, frac_of_full_res):
    RESCALE = 1e2
    DIST_PER_POINT = 0.1  # 10 cm per square

    return (0.1407675 * np.exp(0.85425173 * img_dist / RESCALE / frac_of_full_res) + 0.79365708) * DIST_PER_POINT


class ThreshBlob(DetectionModel):

    def __init__(self, thresholder=None, blob_detector_params=None):

        # thresholder <Thresholder>
        # the thresholder to be applied to the image before finding blobs
        self.thresholder = thresholder or Thresholder()

        if blob_detector_params is None:
            self.blob_detector_params = {}

            self.blob_detector_params["minArea"] = 1
            # overwritten by tuner to be number of pixels in the image. ie 640 * 480
            self.blob_detector_params["maxArea"] = 0
            self.blob_detector_params["minCircularity"] = 0.0
            self.blob_detector_params["maxCircularity"] = 1.0
            self.blob_detector_params["minInertiaRatio"] = 0.0
            self.blob_detector_params["maxInertiaRatio"] = 1.0
            self.blob_detector_params["minConvexity"] = 0.0
            self.blob_detector_params["maxConvexity"] = 1.0
        else:
            self.blob_detector_params = blob_detector_params

        self.blob_detector_params["blobColor"] = 255
        self.blob_detector_params["filterByInertia"] = True
        self.blob_detector_params["filterByConvexity"] = True
        self.blob_detector_params["filterByColor"] = True
        self.blob_detector_params["filterByArea"] = True
        self.blob_detector_params["filterByCircularity"] = True

    def apply(self, frame):
        mask = self.thresholder.apply(frame)
        height, width = mask.shape
        ignore_mask = cv2.resize(
            IGNORE_MASK, (width, height), interpolation=cv2.INTER_NEAREST) > 0

        mask[ignore_mask] = 0

        params = cv2.SimpleBlobDetector_Params()
        for name, val in self.blob_detector_params.items():
            setattr(params, name, val)
        blob_detector = cv2.SimpleBlobDetector_create(params)

        self.cx, self.cy = CX * width / MAX_X, CY * height / MAX_Y

        results = []
        for keypoint in blob_detector.detect(mask):
            x, y = keypoint.pt
            x, y = int(x), int(y)

            # detect contours to find the true bounding rect
            contour_padding = int(keypoint.size * 0.75)
            (roi_x1, roi_y1), (roi_x2, roi_y2) = (
                (max(x - contour_padding, 0), max(y - contour_padding, 0)),
                (min(x + contour_padding, width), min(y + contour_padding, height))
            )

            _, contours, _ = cv2.findContours(
                mask[roi_y1:roi_y2, roi_x1:roi_x2].copy(),
                cv2.RETR_TREE,
                cv2.CHAIN_APPROX_SIMPLE
            )
            theta = arctan2(y - self.cy, x - self.cx)
            img_dist, ((x1, y1), (x2, y2), (x3, y3), (x4, y4)) =\
                self.find_radial_bounding_box(
                    contours, theta, (roi_x1, roi_y1))

            coords = \
                (int(x1 + self.cx), int(y1 + self.cy)),\
                (int(x2 + self.cx), int(y2 + self.cy)),\
                (int(x3 + self.cx), int(y3 + self.cy)),\
                (int(x4 + self.cx), int(y4 + self.cy))

            result = DetectionResult(
                coords=coords,
                bitmask=mask
            )
            result.bearing = theta
            result.distance = convert_img_dist_to_real_dist(
                img_dist, width / MAX_X)
            results.append(result)

        return results

    def find_radial_bounding_box(self, contours, theta, roi_offset):
        rx, ry = roi_offset

        min_dist_1, min_dist_2 = 99999999, 999999999
        max_dist_1, max_dist_2 = -99999999, -999999999

        for contour in contours:
            for [[x, y]] in contour:
                # relative to camera point (0, 0)
                x += rx - self.cx
                y += ry - self.cy

                # okay so how this algorithm works is best explained by
                # a geometry picture which i will put in the report
                a = sqrt(pow(x, 2) + pow(y, 2))
                phi = arctan2(y, x) - theta

                dist_1 = a * cos(phi)
                dist_2 = a * tan(phi)

                if dist_1 > max_dist_1:
                    max_dist_1 = dist_1
                elif dist_1 < min_dist_1:
                    min_dist_1 = dist_1

                if dist_2 > max_dist_2:
                    max_dist_2 = dist_2
                elif dist_2 < min_dist_2:
                    min_dist_2 = dist_2

        # G E O M E T R Y
        dirx, diry = cos(theta), sin(theta)
        rect_inner_midpoint = (min_dist_1 * dirx), (min_dist_1 * diry)
        mx, my = rect_inner_midpoint

        d90 = pi / 2

        left_x, right_x = abs(min_dist_2) * cos(theta + d90), \
            max_dist_2 * cos(theta - d90)
        left_y, right_y = abs(min_dist_2) * sin(theta + d90), \
            max_dist_2 * sin(theta - d90)

        bottom_left_corner = (mx + left_x), (my + left_y)
        bottom_right_corner = (mx + right_x), (my + right_y)

        rect_outer_midpoint = (max_dist_1 * dirx), (max_dist_1 * diry)
        mx, my = rect_outer_midpoint

        top_left_corner = (mx + left_x), (my + left_y)
        top_right_corner = (mx + right_x), (my + right_y)

        return min_dist_1, (top_left_corner, top_right_corner, bottom_right_corner, bottom_left_corner)
