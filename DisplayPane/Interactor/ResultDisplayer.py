from .Interactor import Interactor
import bqplot as bq
import ipywidgets as ipy
import numpy as np
import math

from VisionSystem import VisionSystem


class ResultDisplayer(Interactor):

    def __init__(self):
        self.name2color = {}

    def link_with(self, display_pane):
        super().link_with(display_pane)

        self.bounding_boxes = bq.Lines(
            stroke_width=2,
            close_path=True,
            scales=display_pane.image_plot_scales)

        self.labels = bq.Label(scales=display_pane.image_plot_scales)

        def on_result_change():
            boxes_x = []
            boxes_y = []
            colors = []
            labels_x = []
            labels_y = []
            labels_text = []

            width, height = display_pane.raw_frame.resolution()

            for (name, (detection_results, bearings_distances)) in display_pane.vision_system.current_results.items():
                if name in self.name2color:
                    color = self.name2color[name]
                else:
                    color = display_pane.vision_system.CATEGORICAL_COLORS[len(
                        self.name2color)]
                    self.name2color[name] = color

                for idx, (result, (bearing, distance)) in enumerate(zip(detection_results, bearings_distances)):
                    ((x1, y1), (x2, y2)) = result.coords
                    x1 /= width
                    x2 /= width
                    y1 = 1 - y1 / height
                    y2 = 1 - y2 / height
                    boxes_x.append([x1, x1, x2, x2])
                    boxes_y.append([y1, y2, y2, y1])
                    # format colour as hex
                    colors.append('#%02x%02x%02x' % color)
                    labels_x.append(x1)
                    labels_y.append(y1 - 0.05)
                    labels_text.append(
                        f'{name}{idx}: {round(distance * 100)}@{round(math.degrees(bearing))}')

            self.bounding_boxes.x = boxes_x
            self.bounding_boxes.y = boxes_y
            self.bounding_boxes.colors = colors

            self.labels.x = labels_x
            self.labels.y = labels_y
            self.labels.text = labels_text
            self.labels.colors = colors

        display_pane.update_frame_cbs.append(on_result_change)

        super().set_image_plot_marks([self.bounding_boxes, self.labels])
