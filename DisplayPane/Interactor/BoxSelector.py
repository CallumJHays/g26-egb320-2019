from .Interactor import Interactor
import cv2
import ipywidgets as ipy
import bqplot as bq
import numpy as np


class BoxSelector(Interactor):

    def __init__(self):
        self.bq_selection_outline = None
        self.selector_indicator = None

    def link_with(self, display_pane):
        super().link_with(display_pane)

        self.box_mark = bq.Scatter(
            x=[], y=[],
            scales=self.display_pane.image_plot_scales,
            tooltip=bq.Tooltip(fields=['x', 'y']),
            enable_move=True,
            marker='cross'
        )

        display_pane.bq_img.on_element_click(on_img_click)

        super().set_image_plot_marks([self.points_mark])
