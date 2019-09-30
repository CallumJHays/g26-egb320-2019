from .ColorSpace import ColorSpace, ColorSpaces
import cv2
import numpy as np


class Frame():

    def __init__(self, img, colorspace):
        self.link(img, colorspace)
        self.mask = None

    def get(self, colorspace):
        if isinstance(colorspace, ColorSpaces) or isinstance(colorspace, ColorSpace):
            colorspace = ColorSpaces[colorspace.name]

        if colorspace in self.colorspace2img:
            return self.colorspace2img[colorspace]
        else:
            self.colorspace2img[colorspace] = colorspace.value.bgr2this(
                self.get(ColorSpaces.BGR))
            return self.colorspace2img[colorspace]

        raise "Couldn't find"

    def link(self, img, colorspace):
        self.colorspace2img = {
            colorspace: img
        }

    def copy(self, img, colorspace):
        if isinstance(img, Frame):
            img = img.get(colorspace)

        self.colorspace2img = {
            colorspace: np.copy(img)
        }

    @staticmethod
    def copy_of(frame):
        this = Frame(np.array([]), ColorSpaces.BGR)
        this.copy(frame, ColorSpaces.BGR)
        return this

    def resolution(self):
        for img in self.colorspace2img.values():
            height, width = img.shape[0:2]
            return width, height
