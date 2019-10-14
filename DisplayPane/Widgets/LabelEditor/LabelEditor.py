from VisionSystem.Label import Point, BoundingBox, Polygon
from .BoundingBoxEditor import BoundingBoxEditor
from .PointEditor import PointEditor
from .PolygonEditor import PolygonEditor


def LabelEditor(label):
    return {
        Point: PointEditor,
        BoundingBox: BoundingBoxEditor,
        Polygon: PolygonEditor
    }[type(label)](label)
