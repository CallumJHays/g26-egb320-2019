import ipywidgets as ipy

from .Interactor import Interactor


class DataSetBrowser(Interactor):

    is_panel = True

    def __init__(self, dataset):
        self.dataset = dataset

    def link_with(self, display_pane):
        super().link_with(display_pane)

        self.ipy_controls = ipy.VBox([
            ipy.Label("Dataset Browser"),
            ipy.VBox([ipy.HBox(["filepath", "type", "labelled", "open"])] + [
                ipy.HBox([filepath, dataset.type_str,
                          f'{dataset.n_labelled}/{len(dataset)}', examples])
                for filepath, dataset
                in self.dataset.files.items()
            ])
        ])
