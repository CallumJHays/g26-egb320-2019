import cv2
import numpy as np
import math
from .DetectionModel.ThreshBlob import ThreshBlob
from .DetectionModel import ColorSpaces
from multiprocessing import Pool


class VisionSystem():

    CATEGORICAL_COLORS = [
        (211, 47, 47),  # red
        (25, 118, 210),  # blue
        (56, 142, 60),  # green
        (251, 192, 45),  # yellow
        (69, 90, 100),  # bluegray
        (194, 24, 91),  # pink
        (123, 31, 162),  # purple
        (230, 74, 25),  # orange
        (0, 121, 107)  # teal
    ]

    def __init__(self, objects_to_track, resolution):
        # objects_to_track <dict<key=str, val=VisualObject>>
        # the objects that the vision system should attempt to track every time
        # update_with_frame() is called
        self.objects_to_track = objects_to_track or {}
        self.resolution = resolution

        for _, obj in self.objects_to_track.items():
            obj.resolution = resolution

        self.current_results = {}

    def update_with_frame(self, frame):
        self.current_results = {
            name: obj.update_with_frame(frame)
            for name, obj in self.objects_to_track.items()
        }

    def update_with_and_label_frame(self, frame):
        self.update_with_frame(frame)
        self.label_frame(frame)

    def label_frame(self, frame):
        img = frame.get(ColorSpaces.BGR)
        img_textboxed = None
        for obj_idx, (name, obj_type) in enumerate(self.objects_to_track.items()):
            for res_idx, (result, (bearing, distance)) in enumerate(zip(obj_type.detection_results, obj_type.bearings_distances)):
                MASK_COLOR = (1,)

                draw_color = VisionSystem.CATEGORICAL_COLORS[obj_idx]

                def draw_bounding_box(img, draw_color): return cv2.rectangle(
                    img, result.coords[0], result.coords[1], draw_color)

                def draw_text(img, draw_color): return cv2.putText(
                    img,
                    text="%s%d: %.2fcm@%.0fdeg" % (
                        name, res_idx, distance * 100, math.degrees(bearing)),
                    org=(result.coords[0][0], result.coords[0][1] - 10),
                    fontFace=cv2.FONT_HERSHEY_PLAIN,
                    fontScale=1,
                    color=draw_color
                )

                img_boxed = draw_bounding_box(img, draw_color)
                img_textboxed = draw_text(img_boxed, draw_color)
                mask_boxed = draw_bounding_box(
                    frame.mask, draw_color=MASK_COLOR)
                mask_textboxed = draw_text(mask_boxed, draw_color=MASK_COLOR)
                frame.mask = mask_textboxed

        if img_textboxed is not None:
            frame.link(img_textboxed, ColorSpaces.BGR)


def update_obj(obj, frame):
    obj.update_with_frame(frame)
