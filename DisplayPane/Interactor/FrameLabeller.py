from .Interactor import Interactor


class FrameLabeller(Interactor):

    is_panel = True

    def __init__(self, labels):
        self.labels = labels

    def link_with(self, display_pane):
        super().link_with(display_pane)
