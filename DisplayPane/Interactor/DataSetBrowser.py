import ipywidgets as ipy

from .Interactor import Interactor


class DataSetBrowser(Interactor):

    # is_panel = True

    def __init__(self, dataset):
        self.dataset = dataset

    def link_with(self, display_pane):
        super().link_with(display_pane)

        def handle_open_dset(dataset):
            def handler():
                print('hello')
                display_pane.dataset = dataset

            return handler

        grid_body = []
        for filepath, dataset in self.dataset.files.items():
            for label_str in [filepath[len(self.dataset.filepath):] if filepath != self.dataset.filepath else filepath, dataset.type_str, f'{dataset.n_labelled} / {len(dataset)}']:
                grid_body.append(ipy.Label(label_str, layout=ipy.Layout(
                    border='1px solid grey', margin="0", padding="1")))

            open_button = ipy.Button(icon="folder-open", layout=ipy.Layout(
                border='1px solid grey', width="100%", margin="0", padding="1"))

            def on_click(_):
                display_pane.dataset = dataset

            open_button.on_click(on_click)

            grid_body.append(open_button)

        self.ipy_controls = ipy.VBox([
            ipy.Label(f"Dataset ({self.dataset.filepath})"),
            ipy.GridBox(
                [ipy.Label(header) for header in ["Filepath", "Type", "Labelled", "Open"]] +
                grid_body,
                layout=ipy.Layout(grid_template_columns="auto auto auto 40px")
            )
        ],
            layout=ipy.Layout(width=f'{100}%')
        )
