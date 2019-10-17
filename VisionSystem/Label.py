from abc import ABC, abstractmethod, abstractclassmethod


class Label(ABC):

    def __init__(self, tags=None):
        self.tags = tags or {}

    @abstractmethod
    def coords_str(self):
        raise NotImplementedError()


class FrameLabels():

    def __init__(self, labels=None):
        self.complete = False
        self.labels = labels or {}


class CoordsWrapper(Label):

    def __init__(self, coords):
        super().__init__()
        self.coords = coords

    def coords_str(self):
        return str(self.coords)


class BoundingBox(CoordsWrapper):
    pass


class Polygon(CoordsWrapper):
    pass


class Point(CoordsWrapper):
    pass
