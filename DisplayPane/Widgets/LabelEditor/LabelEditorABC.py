import ipywidgets as ipy
from abc import ABC, abstractmethod
from threading import Timer


class LabelEditorABC(ABC):

    def __init__(self, label):
        self.label = label

    @abstractmethod
    def editor(self, display_pane, label_type_name, redraw, focus, verify_labels):
        raise NotImplementedError()

    def tags_editor(self, redraw, focus, verify_labels):

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

        for name, tag in self.label.tags.items():
            # need the closure
            def loop_iter(name, tag):
                global redraw_debounce

                redraw_debounce = None

                def on_change_tag_name(change):
                    global redraw_debounce
                    self.label.tags[change['new']] = \
                        self.label.tags[change['old']]
                    del self.label.tags[change['old']]
                    if redraw_debounce:
                        redraw_debounce.cancel()

                    def redraw_and_focus():
                        redraw()
                        focus()

                    redraw_debounce = Timer(2.0, redraw_and_focus)
                    redraw_debounce.start()

                name_box = ipy.Text(value=name)
                name_box.observe(on_change_tag_name, 'value')
                name_box.layout.width = '100%'

                def on_change_tag_val(change):
                    self.label.tags[name] = change['new']
                    verify_labels()

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
            add_tag_button,
            ipy.GridBox(
                [editor for name_box, val_box, del_button in tag_editors for editor in [
                    name_box, val_box, del_button]],
                layout=ipy.Layout(grid_template_columns="120px 120px 40px"))
        ])

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
