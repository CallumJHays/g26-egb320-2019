from .Interactor import Interactor
from .SegmentSelector import SegmentSelector
import ipywidgets as ipy
import bqplot as bq
import numpy as np
import math


class PixelValueSegmentInspector(Interactor):

    is_panel = True

    def __init__(self, vision_system=None):
        self.segment_selector = SegmentSelector()
        self.enabled = True
        self.vision_system = vision_system

    def link_with(self, display_pane):
        super().link_with(display_pane)
        self.segment_selector.link_with(display_pane)
        self.segment_selector.observe(self.update_pixel_intensities_mark)
        self.display_pane.bq_img.observe(
            lambda _change: self.update_pixel_intensities_mark())

        self.ipy_controls = ipy.VBox([
            self.segment_selector.ipy_controls,
            self.make_pixel_intensities_pane()
        ])

        super().set_image_plot_marks(self.segment_selector.image_plot_marks)

    def make_pixel_intensities_pane(self):
        FULL_HEIGHT = 800

        scales = {
            'x': bq.LinearScale(min=0),
            'y': bq.LinearScale(min=0, max=255)
        }

        self.pixel_intensities_mark = bq.Lines(
            scales=scales,
            colors=['blue', 'green', 'red'],
            line_style='solid',
            display_legend=True
        )

        self.pixel_thresholds_mark = bq.Lines(
            scales=scales,
            colors=['blue', 'green', 'red', 'blue', 'green', 'red'],
            line_style='dashed',
            opacities=[0.7] * 3
        )

        axes = [
            bq.Axis(scale=scales['y'], orientation='vertical')
        ]

        self.pixel_intensities_fig = bq.Figure(
            marks=[self.pixel_intensities_mark, self.pixel_thresholds_mark], axes=axes)
        self.pixel_intensities_fig.layout.width = '100%'
        self.pixel_intensities_fig.layout.height = str(
            self.display_pane.size * self.display_pane.available_space * FULL_HEIGHT) + 'px'
        self.pixel_intensities_fig.layout.margin = '0'

        self.update_pixel_intensities_mark()

        minimizeable = ipy.Accordion(children=[self.pixel_intensities_fig])
        minimizeable.set_title(0, 'Pixel Values Along Segment')

        def on_change(change):
            self.enabled = change['new'] == 0

        minimizeable.observe(on_change, 'selected_index')

        return ipy.VBox([
            minimizeable,
            bq.toolbar.Toolbar(figure=self.pixel_intensities_fig)
        ])

    def update_pixel_intensities_mark(self):
        if self.enabled:
            ys = []

            if len(self.segment_selector.segment_mark.y) == 2 and len(self.segment_selector.segment_mark.x) == 2:

                img = self.display_pane.filtered_frame.get(
                    self.display_pane.display_colorspace)
                height, width, _ = img.shape

                [init_x, final_x] = (
                    self.segment_selector.segment_mark.x * width).astype(int)
                init_x = max(init_x, 0)
                final_x = min(final_x, width)

                [init_y, final_y] = (
                    self.segment_selector.segment_mark.y * height).astype(int)
                init_y = max(init_y, 0)
                final_y = min(final_y, height)

                den = (final_x - init_x)
                if den == 0:
                    self.pixel_intensities_mark.x = np.empty(shape=(0,))
                    self.pixel_intensities_mark.y = np.empty(shape=(0,))
                    return

                def pos_neg(val):
                    return -1 if val < 0 else 1

                num = final_y - init_y
                gradient = num / den

                direction = pos_neg(gradient) if math.isnan(
                    gradient) else pos_neg(num)
                curr_y = init_y

                for x in range(init_x, final_x):
                    next_y = init_y + int(gradient * (x - init_x))

                    # TODO: this can probably be more efficient but I CBF rn:
                    for y in range(curr_y, next_y + direction, direction):
                        ys.append(img[height - y - 1, x])

                    curr_y = next_y

            y_arr = np.array(ys)
            self.pixel_intensities_mark.y = y_arr.T

            length = y_arr.shape[0]
            self.pixel_intensities_mark.x = np.repeat(
                np.arange(0, length).reshape((1, -1)),
                repeats=3, axis=0)

            for obj in self.vision_system.objects_to_track.values():
                # thank you python for making this disgusting reflection possible
                if hasattr(obj.detection_model, 'thresholder'):
                    if len(self.pixel_intensities_mark.x.shape) == 2 and len(self.pixel_intensities_mark.x[0]) >= 2:
                        min_x, max_x = tuple(self.pixel_intensities_mark.x[0][idx]
                                             for idx in (0, -1))
                        thresholder = obj.detection_model.thresholder

                        self.pixel_thresholds_mark.x = np.repeat(
                            [[min_x, max_x]], repeats=6, axis=0)
                        self.pixel_thresholds_mark.y = list([thresh] * 2 for thresh in thresholder.lower +
                                                            thresholder.upper)
                        self.pixel_intensities_mark.labels = thresholder.colorspace.channel_labels
