import numpy as np


class DetectionResult():

    # rectangular bounds of detected object.

    # coords ((x1, y1), (x2, y2)) <tuple<tuple<int, int>, tuple<int, int>>>
    # pixel coords of lower left and upper-right corners of bounding box rect, respectively
    coords = (None, None)

    # bitmask <np.array<uint8>?>
    # bitmask of the solution
    bitmask = None

    def __init__(self, coords, bitmask=None):
        self.coords = coords
        self.bitmask = bitmask

    def area(self):
        if len(self.coords) == 2:
            ((x1, y1), (x2, y2)) = self.coords
            return int((x2 - x1)) * int((y2 - y1))
        else:
            x, y = zip(*list(self.coords))
            x, y = np.array(x), np.array(y)
            # "shoelace" algorithm by Mahdi
            # https://stackoverflow.com/questions/24467972/calculate-area-of-polygon-given-x-y-coordinates
            return 0.5*np.abs(np.dot(x, np.roll(y, 1))-np.dot(y, np.roll(x, 1)))
