import ipywidgets as ipy

from .Interactor import Interactor


class DataSetBrowser(Interactor):

    # is_panel = True

    def __init__(self, dataset):
        self.dataset = dataset

    def link_with(self, display_pane):
        super().link_with(display_pane)

        self.save_button = ipy.Button(
            icon="save", tooltip="Save dataset labels")

        def on_save_dset(_):
            self.dataset.save()

        self.save_button.on_click(on_save_dset)

        self.ipy_controls = ipy.VBox(children=[],
                                     layout=ipy.Layout(width=f'{100}%')
                                     )
        self.redraw()

    def redraw(self):
        grid_body = []
        for filepath, dataset in self.dataset.files.items():
            for label_str in [filepath[len(self.dataset.filepath):] if filepath != self.dataset.filepath else filepath, dataset.type_str, f'{dataset.n_labelled} / {len(dataset)}']:
                grid_body.append(ipy.Label(label_str, layout=ipy.Layout(
                    border='1px solid grey', margin="0", padding="1")))

            open_button = ipy.Button(icon="folder-open", layout=ipy.Layout(
                border='1px solid grey', width="100%", margin="0", padding="1"))

            def on_open_dset(dataset):
                def inner(_):
                    self.display_pane.dataset = dataset
                return inner

            open_button.on_click(on_open_dset(dataset))

            grid_body.append(open_button)
            self.ipy_controls.children = [
                ipy.HBox(
                    [ipy.Label(f"Dataset ({self.dataset.filepath})"), self.save_button]),
                ipy.GridBox(
                    [ipy.Label(header) for header in ["Filepath", "Type", "Labelled", "Open"]] +
                    grid_body,
                    layout=ipy.Layout(
                        grid_template_columns="auto auto auto 40px")
                )
            ]
