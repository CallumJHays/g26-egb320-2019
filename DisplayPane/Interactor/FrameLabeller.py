import ipywidgets as ipy
from abc import ABC, abstractmethod
import bqplot as bq

from .Interactor import Interactor
from VisionSystem.Label import Point, BoundingBox


class FrameLabeller(Interactor):

    is_panel = True

    def __init__(self, labels):
        self.labels = labels

    def link_with(self, display_pane):
        global curr_dset_idx
        super().link_with(display_pane)

        add_label_type_button = ipy.Button(description="Add New Label Type")

        curr_dset_idx = display_pane.dataset_idx
        label_accordion = ipy.Accordion(children=[])

        label_marks = []

        def on_change_labels():
            for mark in label_marks:
                display_pane.image_plot.marks.remove(mark)
            label_marks.clear()

            name2labels = self.labels[display_pane.dataset.filepath][curr_dset_idx].labels
            children = []
            for idx, (name, (label_type, labels)) in enumerate(name2labels.items()):

                plotter = LabelsPlotter(label_type, labels)
                mark = plotter.bqplot_mark(
                    scales=display_pane.image_plot_scales)
                if mark not in display_pane.image_plot.marks:
                    display_pane.image_plot.marks.append(mark)
                label_marks.append(mark)

                add_label_button = ipy.Button(description="Add Label")

                def on_add_label(_):
                    labels.append(Point((0.5, 0.5)))
                    on_change_labels()

                add_label_button.on_click(on_add_label)

                acc = ipy.Accordion(children=[LabelEditor(label).editor(display_pane, on_change_labels)
                                              for label in labels])
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

                children.append(ipy.VBox([
                    ipy.HBox([
                        ipy.VBox([ipy.HBox([ipy.Label("Name", layout=ipy.Layout(
                            width='90%')), save_name_button]), name_textbox]),

                        ipy.VBox(
                            [ipy.Label("Type", layout=ipy.Layout(
                                width='90%')), ipy.Dropdown(options=['Point'], layout=ipy.Layout(
                                    width='90%'))]),
                    ]),
                    acc,
                    add_label_button
                ]))
                label_accordion.set_title(idx, name)
            label_accordion.children = children

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

        self.ipy_controls = ipy.VBox([
            label_accordion,
            add_label_type_button
        ])

        self.ipy_controls.layout.width = '50%'


def LabelEditor(label):
    return {
        Point: PointEditor,
        BoundingBox: BoundingBoxEditor
    }[type(label)](label)


class LabelEditor_(ABC):

    def __init__(self, label):
        self.label = label

    @abstractmethod
    def editor(self, display_pane, redraw):
        raise NotImplementedError()


def LabelsPlotter(label_type, labels):
    return {
        Point: PointsPlotter,
    }[label_type](labels)


class LabelsPlotter_(ABC):

    def __init__(self, labels):
        self.labels = labels

    @abstractmethod
    def on_labels_updated(self):
        raise NotImplementedError()

    @abstractmethod
    def bqplot_mark(self):
        raise NotImplementedError()


class PointsPlotter(LabelsPlotter_):

    def on_labels_updated(self):
        x, y = [], []
        for point in self.labels:
            (px, py) = point.coords
            x.append(px)
            y.append(py)
        self.mark.x = x
        self.mark.y = y

    def bqplot_mark(self, scales):
        self.mark = bq.Scatter(
            x=[], y=[],
            scales=scales,
            tooltip=bq.Tooltip(fields=['x', 'y']),
            enable_move=True,
            marker='cross'
        )
        self.on_labels_updated()
        return self.mark


class PointEditor(LabelEditor_):

    def editor(self, display_pane, redraw):

        tag_editors = []

        save_point_button = ipy.Button(icon='save', disabled=True)

        def on_save_tags(_):
            self.label.tags.clear()
            for name_box, val_box, _ in tag_editors:
                self.label.tags[name_box.value] = val_box.value
            save_point_button.disabled = True

        save_point_button.on_click(on_save_tags)

        add_tag_button = ipy.Button(description='Add Tag', icon='plus')

        def on_add_tag(_):
            self.label.tags['new_tag'] = ''
            redraw()

        add_tag_button.on_click(on_add_tag)

        def on_tag_change(_):
            save_point_button.disabled = False

        for name, tag in self.label.tags.items():
            name_box = ipy.Text(value=name)
            name_box.observe(on_tag_change, 'value')
            name_box.layout.width = '100%'

            val_box = ipy.Text(value=tag)
            val_box.observe(on_tag_change, 'value')
            val_box.layout.width = '100%'

            delete_tag_button = ipy.Button(icon='trash')
            delete_tag_button.layout.width = '100%'

            def on_delete_tag(_):
                del self.label.tags[name]
                redraw()

            delete_tag_button.on_click(on_delete_tag)

            tag_editors.append((name_box, val_box, delete_tag_button))

        return ipy.VBox([
            ipy.HBox([save_point_button, add_tag_button]),
            ipy.GridBox(
                [editor for name_box, val_box, del_button in tag_editors for editor in [
                    name_box, val_box, del_button]],
                layout=ipy.Layout(grid_template_columns="120px 120px 40px"))
        ])


class BoundingBoxEditor(LabelEditor_):

    def editor(self, display_pane, redraw):
        pass
