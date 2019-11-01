import bqplot as bq
import ipywidgets as ipy
import cv2
import numpy as np
from threading import Thread

from VisionSystem.DetectionModel import Frame, ColorSpaces
from .Interactor.ResultDisplayer import ResultDisplayer
from .Interactor.DataSetBrowser import DataSetBrowser
from .Interactor.FrameLabeller import FrameLabeller


class DisplayPane(ipy.VBox):

    FULL_EXTERNAL_WIDTH = 983
    FULL_INTERNAL_WIDTH = 745
    FULL_OFFSET = 240

    def __init__(self, video_stream=None, img_path=None, img=None, interactors=None, size=0.5, vision_system=None, frame=None,
                 filter_fn=None, apply_filter_to_vision_system_input=False, update_frame_cbs=None, display_colorspace=ColorSpaces.BGR,
                 available_space=1, apply_mask=False, dataset=None, **kwargs):

        if not (video_stream is not None) ^ (img is not None) ^ (frame is not None) ^ (img_path is not None) ^ (dataset is not None):
            raise Exception(
                "either path, img or frame must be defined, and not both")

        self.bq_img = None
        self.raw_frame = None
        self.size = size
        self.available_space = available_space
        self.video_stream = video_stream
        self.dataset = dataset
        self.togglebutton_group = []
        self.interactors = interactors or []
        self.vision_system = vision_system
        self.filter_fn = filter_fn
        self.apply_filter_to_vision_system_input = apply_filter_to_vision_system_input
        self.image_plot_scales = {'x': bq.LinearScale(), 'y': bq.LinearScale()}
        self.hidden = False
        self.display_colorspace = display_colorspace
        self.apply_mask = apply_mask
        self.dataset_idx = 0

        self.update_frame_cbs = update_frame_cbs or []

        # read the data from a file to display
        if img is None:
            if dataset is not None:
                bgr, _ = next(iter(dataset))
                self.raw_frame = Frame(bgr, ColorSpaces.BGR)
            elif frame is not None and type(frame is Frame):
                self.raw_frame = frame
            elif img_path is not None:
                bgr = cv2.imread(img_path)
                if bgr is None:
                    raise Exception("Failed to read image at img_path")
                self.raw_frame = Frame(bgr, ColorSpaces.BGR)
            else:
                self.raw_frame = next(iter(self.video_stream))
        else:
            self.raw_frame = Frame(img, ColorSpaces.BGR)

        self.filtered_frame = Frame.copy_of(self.raw_frame)
        self.labelled_frame = Frame.copy_of(self.filtered_frame)

        self.update_data_and_display()

        if self.dataset is not None:
            self.interactors.insert(0, DataSetBrowser(self.dataset))

            if not any(isinstance(inter, FrameLabeller) for inter in self.interactors):
                self.interactors.append(FrameLabeller(self.dataset.labels))

        if self.vision_system is not None:
            self.interactors.append(ResultDisplayer(self.vision_system))

        # link all required interactors
        for interactor in self.interactors:
            interactor.link_with(self)

        self.image_plot = self.make_image_plot()

        interactors_with_controls = [
            interactor for interactor in self.interactors if interactor.ipy_controls is not None]
        panel_controls = [
            interactor.ipy_controls for interactor in interactors_with_controls if interactor.is_panel]
        toolbar_controls = [
            interactor.ipy_controls for interactor in interactors_with_controls if not interactor.is_panel]

        display_pane = ipy.VBox([
            self.image_plot,
            self.make_image_tools(self.image_plot)
        ] + toolbar_controls)

        display_pane.layout.width = str(
            size * available_space * self.FULL_EXTERNAL_WIDTH) + 'px'

        # fill accross 1/size times before filling downwards
        hbox_list = [display_pane]
        vbox_list = []

        for controls in (c for c in panel_controls if c is not None):
            hbox_list.append(controls)

            if len(hbox_list) == int(1 / size):
                vbox_list.append(ipy.HBox(hbox_list))
                hbox_list = []

        # add the remainder
        vbox_list += hbox_list

        super().__init__(vbox_list, **kwargs)

    def make_image_plot(self):

        marks = [self.bq_img]
        for interactor in self.interactors:
            marks += interactor.image_plot_marks

        image_plot = bq.Figure(
            marks=marks,
            padding_y=0
        )

        height, width, _ = self.raw_frame.get(ColorSpaces.BGR).shape
        # make sure the image is displayed with the correct aspect ratio
        # TODO: is this broken?
        image_plot.layout.width = '100%'
        image_plot.layout.margin = '0'
        image_plot.layout.height = str(
            (self.FULL_INTERNAL_WIDTH * height / width + self.FULL_OFFSET) * self.size * self.available_space) + 'px'

        return image_plot

    def make_image_tools(self, image_plot):
        widget_list = [
            self.make_toggle_panzoom_button(image_plot),
            self.make_reset_zoom_button(),
            self.make_toggle_apply_mask_button()
        ]

        if self.video_stream is not None:
            if self.video_stream.on_disk:
                widget_list.append(self.make_video_controller())
            else:
                # start the livestream pipe to this displaypane on a separate thread
                Thread(target=self.pipe_livestream).start()

        if self.dataset is not None:
            if self.dataset.type_str in ["img-dir", "vid"]:
                widget_list.append(self.make_dataset_frame_browser())

        return ipy.HBox(widget_list)

    def pipe_livestream(self):
        for frame in self.video_stream:
            self.raw_frame = frame
            self.update_data_and_display()

    def make_toggle_apply_mask_button(self):

        button = ipy.ToggleButton(
            value=False,
            tooltip='Toggle Mask',
            icon='eye-slash'
        )
        button.layout.width = '60px'

        def on_toggle(change):
            self.apply_mask = not self.apply_mask
            self.update_data_and_display()

        button.observe(on_toggle, 'value')

        return button

    def make_toggle_panzoom_button(self, image_plot):
        self.image_plot_panzoom = bq.interacts.PanZoom(
            scales={'x': [self.image_plot_scales['x']],
                    'y': [self.image_plot_scales['y']]},
        )

        button = ipy.ToggleButton(
            value=False,
            tooltip='Toggle Pan / Zoom',
            icon='arrows'
        )
        button.layout.width = '60px'

        def on_toggle(change):
            if change['new']:
                image_plot.interaction = self.image_plot_panzoom
            else:
                image_plot.interaction = None

        button.observe(on_toggle, 'value')
        self.add_to_togglebutton_group(button)

        return button

    def make_reset_zoom_button(self):
        button = ipy.Button(
            disabled=False,
            tooltip='Reset zoom',
            icon='refresh'
        )
        button.layout.width = '60px'

        def on_click(_change):
            self.image_plot_panzoom.scales['x'][0].min = None
            self.image_plot_panzoom.scales['x'][0].max = None
            self.image_plot_panzoom.scales['y'][0].min = None
            self.image_plot_panzoom.scales['y'][0].max = None

        button.on_click(on_click)

        return button

    def make_dataset_frame_browser(self):
        if self.dataset.type_str == "vid":
            cap = cv2.VideoCapture(self.dataset.filepath)
            fps = cap.get(cv2.CAP_PROP_FPS)
        if self.dataset.type_str == "img-dir":
            fps = 2
        last_frame = len(self.dataset) - 1

        player = ipy.Play(
            interval=1000 / fps,
            max=last_frame
        )
        slider = ipy.IntSlider(max=last_frame,
                               continuous_update=False)
        ipy.link((player, 'value'), (slider, 'value'))

        def on_framechange(change):
            self.dataset_idx = change['new']
            self.raw_frame = self.dataset.read_frame(self.dataset_idx)
            self.update_data_and_display()

        player.observe(on_framechange, 'value')
        slider.observe(on_framechange, 'value')

        def change_slider(amount):
            def cb(_change):
                slider.value += amount
                if slider.value > last_frame:
                    slider.value = last_frame
                elif slider.value < 0:
                    slider.value = 0
            return cb

        prev_frame_button = ipy.Button(
            icon='step-backward',
            tooltip='Previous Frame'
        )
        prev_frame_button.layout.width = '60px'
        prev_frame_button.on_click(change_slider(-1))

        next_frame_button = ipy.Button(
            icon='step-forward',
            tooltip='Next Frame'
        )
        next_frame_button.layout.width = '60px'
        next_frame_button.on_click(change_slider(+1))

        controller = ipy.HBox(
            [prev_frame_button, player, next_frame_button, slider])
        return controller

    def make_video_controller(self):
        last_frame = self.video_stream.cap.get(cv2.CAP_PROP_FRAME_COUNT) - 1

        player = ipy.Play(
            interval=1000 / self.video_stream.cap.get(cv2.CAP_PROP_FPS),
            max=last_frame
        )

        slider = ipy.IntSlider(max=last_frame)
        ipy.link((player, 'value'), (slider, 'value'))

        def on_framechange(change):
            frame_idx = change['new']
            self.raw_frame = self.video_stream.read_frame(frame_idx)
            self.update_data_and_display()

        player.observe(on_framechange, 'value')
        slider.observe(on_framechange, 'value')

        def change_slider(amount):
            def cb(_change):
                slider.value += amount
                if slider.value > last_frame:
                    slider.value = last_frame
                elif slider.value < 0:
                    slider.value = 0
            return cb

        prev_frame_button = ipy.Button(
            icon='step-backward',
            tooltip='Previous Frame'
        )
        prev_frame_button.layout.width = '60px'
        prev_frame_button.on_click(change_slider(-1))

        next_frame_button = ipy.Button(
            icon='step-forward',
            tooltip='Next Frame'
        )
        next_frame_button.layout.width = '60px'
        next_frame_button.on_click(change_slider(+1))

        controller = ipy.HBox(
            [prev_frame_button, player, next_frame_button, slider])
        return controller

    def update_data_and_display(self):
        if not self.hidden:
            # filter the image if need be
            self.filtered_frame.link(self.raw_frame, ColorSpaces.BGR)
            if self.filter_fn is not None:
                self.filtered_frame.copy(self.filter_fn(
                    self.filtered_frame), ColorSpaces.BGR)

            self.labelled_frame.copy(self.filtered_frame, ColorSpaces.BGR)
            if self.vision_system is not None:
                self.vision_system.update_with_frame(self.labelled_frame)

            for cb in self.update_frame_cbs:
                cb()

            bgr_img = self.labelled_frame.get(self.display_colorspace)

            # apply the mask here for view purposes
            if self.apply_mask and self.labelled_frame.mask is not None:
                bgr_img = cv2.bitwise_and(
                    bgr_img, bgr_img, mask=self.labelled_frame.mask)
            ipy_img = ipy.Image(value=cv2.imencode('.jpg', bgr_img)[
                                1].tostring(), format='jpg')

            if self.bq_img is None:
                self.bq_img = bq.Image(
                    image=ipy_img, scales=self.image_plot_scales)
            else:
                self.bq_img.image = ipy_img

    def link_frame(self, master_pane):
        def on_update_frame():
            self.raw_frame = master_pane.raw_frame
            self.update_data_and_display()

        master_pane.update_frame_cbs.append(on_update_frame)

    def add_interactor(self, display_pane_interactor):
        display_pane_interactor.link_with(self)
        self.interactors.append(display_pane_interactor)

    def set_interaction(self, interaction):
        self.image_plot.interaction = interaction

    def clear_interaction(self):
        self.image_plot.interaction = None

    def add_to_togglebutton_group(self, togglebutton):
        self.togglebutton_group.append(togglebutton)

        def on_toggle(change):
            if change['new'] is True:
                for button in self.togglebutton_group:
                    if button is not togglebutton:
                        button.value = False

        togglebutton.observe(on_toggle, 'value')

    def show(self):
        self.hidden = False
        self.update_data_and_display()

    def hide(self):
        self.hidden = True
