import ipywidgets as ipy
from abc import ABC, abstractmethod
import numpy as np
import bqplot as bq
from collections import OrderedDict
import re
from threading import Timer

from .Interactor import Interactor
from .DataSetBrowser import DataSetBrowser
from VisionSystem.Label import Point, BoundingBox
from VisionSystem.DetectionModel.ColorSpace import ColorSpaces


class FrameLabeller(Interactor):

    CATEGORICAL_COLORS = [
        'steelblue',  # red
        'green',  # blue
        'red',  # green
        'yellow',  # yellow
        'bluegray',  # bluegray
        'pink',  # pink
        'purple',  # purple
        'orange',  # orange
        'teal'  # teal
    ]

    is_panel = True

    def __init__(self, labels, config=None):
        self.labels = labels
        self.config = config or {}

    def link_with(self, display_pane):
        global curr_dset_idx, points_labels, label2focus_editor_fn
        super().link_with(display_pane)
        width, height, _ = display_pane.raw_frame.get(ColorSpaces.BGR).shape

        add_label_type_button = ipy.Button(description="Add New Label Type")

        curr_dset_idx = display_pane.dataset_idx
        label_accordion = ipy.Accordion(children=[])
        quick_edit = ipy.VBox([], layout=ipy.Layout(border='1px dashed'))

        frame_labels = self.labels[display_pane.dataset.filepath][curr_dset_idx]
        name2labels = frame_labels.labels

        tooltip = ipy.Box()

        points_mark = bq.Scatter(
            x=[], y=[], scales=display_pane.image_plot_scales,
            enable_move=True,
            tooltip=tooltip,
            marker='cross')
        # indexes of labels in points_labels correspond with the point in the scatter-plot above
        points_labels = []
        label2focus_editor_fn = {}

        def on_point_hovered(_, ev):
            label = points_labels[ev['data']['index']]

            tooltip.children = [
                LabelEditor(label).tooltip()
            ]

        def on_point_clicked(_, ev):
            idx = ev['data']['index']
            label = points_labels[idx]
            focus_editor = label2focus_editor_fn[label]
            editor = focus_editor()
            quick_edit.children = [
                ipy.Label(f"Quick-Edit Point {label.coords_str()}"),
                editor
            ]

        points_mark.on_hover(on_point_hovered)
        points_mark.on_element_click(on_point_clicked)

        self.set_image_plot_marks([points_mark])

        def are_labels_valid():
            for type_name, opts in self.config.items():
                labels_tup_or_none = name2labels.get(type_name)
                if labels_tup_or_none is None:
                    name2labels[type_name] = Point, []

                _, labels = name2labels[type_name]

                for tag_name, tag_opts in opts['tags'].items():
                    for label in labels:
                        for tag_opt in tag_opts:
                            tag = label.tags.get(tag_name)

                            if tag_opt == 'required':
                                if not tag:
                                    return False

                            REG_TOKEN = 'regex:'
                            if REG_TOKEN in tag_opt[:len(REG_TOKEN)]:
                                regex = tag_opt[len(REG_TOKEN):]
                                if not re.match(re.compile(regex), tag):
                                    return False

            return True

        check_complete_box = ipy.Checkbox(
            description='Mark Frame as Complete', value=frame_labels.complete, tooltip="Disabled if labels are invalid")

        def on_change_labels():
            global points_labels, label2focus_editor_fn

            check_complete_box.disabled = not are_labels_valid()

            points_mark.x, points_mark.y, colors, points_labels = [], [], [], []
            label2focus_editor_fn = {}

            # fresh instance
            if not any(name2labels):
                # do config
                for type_name, opts in self.config.items():
                    for tag_name, _ in opts['tags'].items():

                        # drunk callum programming magic ~~~
                        points = [Point((width // 2 + dx, height // 2 + dy))
                                  for dx in range(-(2 * width // 5), width // 2, width // 4)
                                  for dy in range(-(2 * height // 5), height // 2, height // 4)]

                        for point in points:
                            point.tags[tag_name] = ''

                        name2labels[type_name] = (Point, points)

            children = OrderedDict()

            for idx, (name, (label_type, labels)) in enumerate(name2labels.items()):
                # had to wrap it in a function so that the inner callbacks are binded to the correct variable for each iteration
                # (ie i need the inner function scope to store contextual state)

                def do_for_loop_iter(colors, outer_idx, name, label_type, labels):
                    global points_labels, label2focus_editor_fn
                    editors = []
                    acc = ipy.Accordion(children=editors)

                    # todo: abstract out the points-only stuff here
                    x, y = [], []
                    for inner_idx, point in enumerate(labels):
                        px, py = point.coords
                        x.append(px / width)
                        y.append(py / height)

                        def focus_editor(outer_idx, inner_idx):
                            def inner():
                                label_accordion.selected_index = outer_idx
                                acc.selected_index = inner_idx
                                # also return the editor so that it can be reused in the 'quick edit' panel
                                return editors[inner_idx]
                            return inner

                        label2focus_editor_fn[point] = focus_editor(
                            outer_idx, inner_idx)
                    editors += [LabelEditor(label).editor(display_pane, name, on_change_labels, label2focus_editor_fn[label])
                                for label in labels]
                    acc = ipy.Accordion(children=editors)

                    points_mark.x = np.append(points_mark.x, x)
                    points_mark.y = np.append(points_mark.y, y)
                    points_labels += labels
                    colors += [self.CATEGORICAL_COLORS[outer_idx]] * \
                        len(labels)

                    def on_drag_end(_, ev):
                        idx = ev['index']
                        pt = ev['point']
                        point = points_labels[idx]
                        point.coords = int(pt['x'] * width),\
                            int(pt['y'] * height)
                        tooltip.children = [
                            LabelEditor(point).tooltip()
                        ]
                        acc.set_title(idx, point.coords_str())
                        focus_editor = label2focus_editor_fn[point]
                        editor = focus_editor()
                        quick_edit.children = [
                            ipy.Label(
                                f"Quick-Edit Point {point.coords_str()}"),
                            editor
                        ]

                    points_mark.on_drag_end(on_drag_end)

                    add_label_button = ipy.Button(description="Add Label")

                    def on_add_label(_):
                        label = Point((width // 2, height // 2))
                        for opt_name, opt_val in self.config[name].items():
                            if opt_name == 'tags':
                                for tag_name, tag_opts in opt_val.items():
                                    if 'required' in tag_opts:
                                        label.tags[tag_name] = ''

                        labels.append(label)

                        on_change_labels()

                    add_label_button.on_click(on_add_label)
                    for idx, label in enumerate(labels):
                        acc.set_title(idx, label.coords_str())

                    name_textbox = ipy.Text(value=name, layout=ipy.Layout(
                        width='90%'))
                    save_name_button = ipy.Button(icon='save', disabled=True)

                    def on_name_changed(_):
                        save_name_button.disabled = False

                    name_textbox.observe(on_name_changed, 'value')

                    def on_save_name(_):
                        new_name = name_textbox.value
                        if new_name != name:
                            del name2labels[name]
                            name2labels[new_name] = (label_type, labels)
                            on_change_labels()

                    save_name_button.on_click(on_save_name)

                    children[name] = ipy.VBox([
                        ipy.HBox([
                            ipy.VBox([ipy.HBox([ipy.Label("Name", layout=ipy.Layout(
                                width='90%')), save_name_button]), name_textbox]),

                            ipy.VBox(
                                [ipy.Label("Type", layout=ipy.Layout(
                                    width='90%')), ipy.Dropdown(options=['Point'], layout=ipy.Layout(
                                        width='90%'))]),
                        ]),
                        add_label_button,
                        acc,
                    ])
                do_for_loop_iter(colors, idx, name, label_type, labels)

            points_mark.colors = colors

            label_accordion.children = list(children.values())
            for idx, name in enumerate(children):
                label_accordion.set_title(idx, name)

        def on_new_frame():
            global curr_dset_idx
            if display_pane.dataset_idx != curr_dset_idx:
                curr_dset_idx = display_pane.dataset_idx
                on_change_labels()

        display_pane.update_frame_cbs.append(on_new_frame)

        def on_add_label_type(_):
            name2labels = self.labels[display_pane.dataset.filepath][curr_dset_idx].labels
            name2labels['new_label_type'] = Point, []
            on_change_labels()

        add_label_type_button.on_click(on_add_label_type)

        def on_check_complete_change(change):
            frame_labels.complete = change['new']
            self.display_pane.dataset.n_labelled += 1 if frame_labels.complete else -1

            for interactor in display_pane.interactors:
                if isinstance(interactor, DataSetBrowser):
                    interactor.redraw()

        check_complete_box.observe(on_check_complete_change, 'value')

        self.ipy_controls = ipy.VBox([
            quick_edit,
            label_accordion,
            add_label_type_button,
            check_complete_box
        ])

        self.ipy_controls.layout.width = '50%'

        on_change_labels()


def LabelEditor(label):
    return {
        Point: PointEditor,
        BoundingBox: BoundingBoxEditor
    }[type(label)](label)


class LabelEditor_(ABC):

    def __init__(self, label):
        self.label = label

    @abstractmethod
    def editor(self, display_pane, label_type_name, redraw):
        raise NotImplementedError()

    def tooltip(self):
        return ipy.VBox([
            ipy.Label(self.label.coords_str()),
            ipy.GridBox([
                ipy.Label(text, layout=ipy.Layout(
                    border='solid 1px', margin='0', padding='2px'))
                for tag_name, tag_val in self.label.tags.items()
                for text in [tag_name, tag_val]
            ],
                layout=ipy.Layout(grid_template_columns="100px 100px"))
        ])


class PointEditor(LabelEditor_):

    def editor(self, display_pane, label_type_name, redraw, focus):

        tag_editors = []

        add_tag_button = ipy.Button(description='Add Tag', icon='plus')

        def on_add_tag(_):
            desired_tag = 'new_tag'
            desired_tag_idx = 0
            while desired_tag in self.label.tags:
                desired_tag_idx += 1
                desired_tag = f'new_tag_{desired_tag_idx}'

            self.label.tags[desired_tag] = ''
            redraw()
            focus()

        add_tag_button.on_click(on_add_tag)

        delete_point_button = ipy.Button(icon='trash')

        def on_delete_point(_):
            _, frame_points = display_pane.dataset.labels[
                display_pane.dataset.filepath][display_pane.dataset_idx].labels[label_type_name]
            if self.label not in frame_points:
                quick_edit.children = []
            else:
                frame_points.remove(self.label)
            redraw()  # cya later bois

        delete_point_button.on_click(on_delete_point)

        for name, tag in self.label.tags.items():
            # need the closure
            def loop_iter(name, tag):
                global save_change_name_debounce, save_change_val_debounce, og_tag_name

                save_change_name_debounce = None
                og_tag_name = None

                def on_change_tag_name(change):
                    global save_change_name_debounce, og_tag_name
                    if og_tag_name is None:
                        og_tag_name = change['old']
                    if save_change_name_debounce:
                        save_change_name_debounce.cancel()

                    def save_changes():
                        global og_tag_name
                        self.label.tags[change['new']] \
                            = self.label.tags[og_tag_name]
                        del self.label.tags[og_tag_name]
                        og_tag_name = None
                        redraw()
                        focus()

                    save_change_name_debounce = Timer(2.0, save_changes)
                    save_change_name_debounce.start()

                name_box = ipy.Text(value=name)
                name_box.observe(on_change_tag_name, 'value')
                name_box.layout.width = '100%'

                save_change_val_debounce = None

                def on_change_tag_val(change):
                    global save_change_val_debounce

                    if save_change_val_debounce:
                        save_change_val_debounce.cancel()

                    def save_changes():
                        self.label.tags[name] = change['new']
                        redraw()
                        focus()

                    save_change_val_debounce = Timer(2.0, save_changes)
                    save_change_val_debounce.start()

                val_box = ipy.Text(value=tag)
                val_box.observe(on_change_tag_val, 'value')
                val_box.layout.width = '100%'

                delete_tag_button = ipy.Button(icon='trash')
                delete_tag_button.layout.width = '100%'

                def on_delete_tag(_):
                    del self.label.tags[name]
                    redraw()

                delete_tag_button.on_click(on_delete_tag)

                tag_editors.append((name_box, val_box, delete_tag_button))
            loop_iter(name, tag)

        return ipy.VBox([
            ipy.HBox([add_tag_button, delete_point_button]),
            ipy.GridBox(
                [editor for name_box, val_box, del_button in tag_editors for editor in [
                    name_box, val_box, del_button]],
                layout=ipy.Layout(grid_template_columns="120px 120px 40px"))
        ])


class BoundingBoxEditor(LabelEditor_):

    def editor(self, display_pane, label_type_name, redraw):
        pass
