import ipywidgets as ipy
from threading import Timer

from .LabelEditorABC import LabelEditorABC


class PointEditor(LabelEditorABC):

    def editor(self, display_pane, label_type_name, redraw, focus, verify_labels):

        delete_point_button = ipy.Button(icon='trash')

        def on_delete_point(_):
            _, frame_points = display_pane.dataset\
                .labels[display_pane.dataset.filepath][display_pane.dataset_idx]\
                .labels[label_type_name]
            if self.label in frame_points:
                frame_points.remove(self.label)
            redraw()  # cya later bois

        delete_point_button.on_click(on_delete_point)

        tags_editor = super().tags_editor(redraw, focus, verify_labels)

        return ipy.VBox([delete_point_button, tags_editor])
