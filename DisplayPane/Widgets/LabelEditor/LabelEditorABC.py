import ipywidgets as ipy
from abc import ABC, abstractmethod
from threading import Timer


class LabelEditorABC(ABC):

    def __init__(self, label):
        self.label = label

    @abstractmethod
    def editor(self, display_pane, label_type_name, redraw):
        raise NotImplementedError()

    def tags_editor(self, redraw, focus):

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
