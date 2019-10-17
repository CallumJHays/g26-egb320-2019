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
from ..Widgets.LabelEditor import LabelEditor


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
        self.dset_browser = None

    def link_with(self, display_pane):
        global curr_dset_idx, frame_labels, name2labels, label2focus_editor_fn, points_labels, label2type_name
        super().link_with(display_pane)
        height, width, _ = display_pane.raw_frame.get(ColorSpaces.BGR).shape

        for interactor in display_pane.interactors:
            if isinstance(interactor, DataSetBrowser):
                self.dset_browser = interactor

        add_label_type_button = ipy.Button(description="Add New Label Type")

        curr_dset_idx = display_pane.dataset_idx
        label_accordion = ipy.Accordion(children=[])
        quick_edit = ipy.VBox([])
        quick_fix = ipy.VBox([])

        frame_labels = self.labels[display_pane.dataset.filepath][curr_dset_idx]
        name2labels = frame_labels.labels

        check_complete_box = ipy.Checkbox(
            description='Mark Frame as Complete',
            value=frame_labels.complete,
            tooltip="Disabled if labels are invalid")

        tooltip = ipy.Box()

        points_mark = bq.Scatter(
            x=[], y=[], scales=display_pane.image_plot_scales,
            enable_move=True,
            tooltip=tooltip,
            marker='cross')
        # indexes of labels in points_labels correspond with the point in the scatter-plot above
        points_labels = []
        label2focus_editor_fn = {}
        label2type_name = {}

        def on_point_hovered(_, ev):
            label = points_labels[ev['data']['index']]

            editor = LabelEditor(label)
            name = label2type_name[label]
            tooltip.children = [
                editor.tooltip()
            ]
            quick_edit.children = [ipy.VBox([
                ipy.Label(f"Quick-Edit Point {label.coords_str()}"),
                editor.editor(display_pane, name, on_change_labels,
                              label2focus_editor_fn[label], verify_labels)
            ], layout=ipy.Layout(border='1px dashed'))]

        def on_point_clicked(_, ev):
            idx = ev['data']['index']
            label = points_labels[idx]
            focus_editor = label2focus_editor_fn[label]
            editor = focus_editor()
            quick_edit.children = [ipy.VBox([
                ipy.Label(f"Quick-Edit Point {label.coords_str()}"),
                editor
            ], layout=ipy.Layout(border='1px dashed'))]

        points_mark.on_hover(on_point_hovered)
        points_mark.on_element_click(on_point_clicked)

        self.set_image_plot_marks([points_mark])

        def quick_fix_err(err, label, type_name):
            err_label = ipy.HTML(
                value=f'<p style="color: red; line-height: 1">{err}</p>')
            err_label.style.color = 'red'
            err_label.style.white_space = ''

            quick_fix.children = [ipy.VBox([
                ipy.Label(f"Error with label: {label.coords_str()}"),
                err_label,
                LabelEditor(label).editor(
                    display_pane, type_name, on_change_labels, label2focus_editor_fn[label], verify_labels)
            ], layout=ipy.Layout(border='1px dashed red'))]

        def verify_labels():
            def is_valid():
                unique_tags = {}
                for type_name, opts in self.config.items():
                    labels_tup_or_none = name2labels.get(type_name)
                    unique_tags[type_name] = {}
                    if labels_tup_or_none is None:
                        name2labels[type_name] = Point, []

                    _, labels = name2labels[type_name]

                    for tag_name, tag_opts in opts['tags'].items():
                        unique_tags[type_name][tag_name] = {}
                        for label in labels:
                            for tag_opt in tag_opts:
                                tag = label.tags.get(tag_name)

                                if tag_opt == 'unique':
                                    existing_tags = unique_tags[type_name][tag_name]
                                    if tag and tag in existing_tags:
                                        quick_fix_err(
                                            f"Error: {tag_name} is expected to have a unique value, but provided '{tag}' was also used for label {existing_tags[tag]}", label, type_name)
                                        return False
                                    else:
                                        existing_tags[tag] = label.coords_str()

                                if tag_opt == 'required':
                                    if not tag:
                                        quick_fix_err(
                                            f"Error: {tag_name} is required but no value was provided", label, type_name)
                                        return False

                                REG_TOKEN = 'regex:'
                                if REG_TOKEN in tag_opt[:len(REG_TOKEN)]:
                                    regex = tag_opt[len(REG_TOKEN):]
                                    if not re.match(re.compile(regex), tag):
                                        quick_fix_err(
                                            f"Error: {tag_name}: {tag} does not match regex {regex}", label, type_name)
                                        return False

                quick_fix.children = []
                return True

            valid = is_valid()
            if not valid:
                if frame_labels.complete:
                    frame_labels.complete = False

                    if self.dset_browser is not None:
                        self.dset_browser.redraw()

            check_complete_box.disabled = not valid

        def on_change_labels(type_idx=0, label_idx=0):
            global points_labels, label2focus_editor_fn, name2labels, frame_labels, label2type_name

            points_mark.x, points_mark.y, colors, points_labels = [], [], [], []
            label2focus_editor_fn, label2type_name = {}, {}
            frame_labels = self.labels[display_pane.dataset.filepath][curr_dset_idx]
            check_complete_box.disabled = True
            check_complete_box.value = frame_labels.complete
            name2labels = frame_labels.labels

            for type_name, opts in self.config.items():
                if 'init' in opts and type_name not in name2labels:
                    print('running init code?')
                    count = opts['init']['count'] if 'count' in opts['init'] else 0
                    offset = 0.2
                    rows = int(np.sqrt(count))
                    cols = int(rows + (count / rows > rows))

                    points = [
                        Point((
                            int(width * (offset + col / cols * (1 - 2 * offset))),
                            int(height * (offset + row / rows * (1 - 2 * offset)))
                        ))
                        for row in range(rows)
                        for col in range(cols)
                    ]
                    name2labels[type_name] = Point, points
                else:
                    _, points = name2labels[type_name]

                if 'tags' in opts:
                    for tag_name, tag_opts in opts['tags'].items():
                        if 'required' in tag_opts:
                            for point in points:
                                if tag_name not in point.tags:
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
                        label2type_name[point] = name

                    editors += [LabelEditor(label).editor(display_pane, name, on_change_labels, label2focus_editor_fn[label], verify_labels)
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
                        quick_edit.children = [ipy.VBox([
                            ipy.Label(
                                f"Quick-Edit Point {label.coords_str()}"),
                            editor
                        ], layout=ipy.Layout(border='1px dashed'))]

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

            verify_labels()

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
            if not check_complete_box.disabled:
                # just a code change for ui purposes
                self.display_pane.dataset.n_labelled += 1 if frame_labels.complete else -1

                if self.dset_browser is not None:
                    self.dset_browser.redraw()

        check_complete_box.observe(on_check_complete_change, 'value')

        self.ipy_controls = ipy.VBox([
            quick_edit,
            label_accordion,
            add_label_type_button,
            check_complete_box,
            quick_fix
        ])

        self.ipy_controls.layout.width = '50%'

        on_change_labels()
