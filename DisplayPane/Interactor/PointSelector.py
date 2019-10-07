from .Interactor import Interactor
import cv2
import ipywidgets as ipy
import bqplot as bq
import numpy as np


class PointSelector(Interactor):

    def __init__(self):
        self.bq_selection_outline = None
        self.selector_indicator = None

    def link_with(self, display_pane):
        super().link_with(display_pane)

        self.points_mark = bq.Scatter(
            x=[], y=[],
            scales=self.display_pane.image_plot_scales,
            tooltip=bq.Tooltip(fields=['x', 'y']),
            enable_move=True,
            marker='cross'
        )

        def on_img_click(_, msg):
            data = msg['data']
            self.points_mark.x = np.append(self.points_mark.x, data['click_x'])
            self.points_mark.y = np.append(self.points_mark.y, data['click_y'])

        display_pane.bq_img.on_element_click(on_img_click)

        super().set_image_plot_marks([self.points_mark])
