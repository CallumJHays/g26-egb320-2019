import cv2
import os
from collections import OrderedDict
import pickle
from itertools import islice

from .DetectionModel.Frame import Frame
from .DetectionModel.DetectionResult import DetectionResult
from .VisionSystem import ColorSpaces
from .Label import FrameLabels


class DataSetIterator():

    def __init__(self, dataset):
        self.dataset = dataset
        self.label_iter = iter(dataset.labels.values())
        self.curr_vid_file = None
        self.bgr = None
        self.curr_img_dir_dset_iter = None

        if any(dataset.files):
            self.file_iter = iter(dataset.files)

        else:
            self.file_iter = None
            # its a single file - source it!
            self.source_file(dataset.filepath)

    def __iter__(self):
        return self

    def __len__(self):
        return len(self.dataset)

    def source_file(self, filepath):
        if os.path.isdir(filepath):
            dset = self.dataset.files[filepath]
            assert dset.type_str == "img-dir"

            self.curr_img_dir_dset_iter = (
                cv2.imread(filepath) for filepath in dset.image_files)
        else:
            self.bgr = cv2.imread(filepath)
            if self.bgr is None:
                self.curr_vid_file = cv2.VideoCapture(filepath)

    def __next__(self):
        if self.bgr is not None:
            bgr = self.bgr
            self.bgr = None
            return bgr, next(self.label_iter)
        elif self.curr_vid_file is not None:
            ret, bgr = self.curr_vid_file.read()

            if ret:
                return bgr, next(self.label_iter)
            else:
                self.curr_vid_file = None
        elif self.curr_img_dir_dset_iter is not None:
            bgr = next(self.curr_img_dir_dset_iter)
            if bgr is None:
                self.curr_img_dir_dset_iter = None
            else:
                return bgr, next(self.label_iter)

        if self.file_iter is not None:
            filepath = next(self.file_iter)
            self.source_file(filepath)
            return self.__next__()
        else:
            raise StopIteration()

    def __del__(self):
        if self.curr_vid_file is not None:
            self.curr_vid_file.release()


class DataSet():

    # A dataset. If initialized on a folder, will do a recursive scan of all image/video
    # data within it to find entries for the dataset.
    # If initialized on a video, will take input from each frame sequentially,
    # aside from those blacklisted via the gui while labelling.

    def __init__(self, filepath):

        self.filepath = filepath
        self.blacklist = {}
        self.files = OrderedDict()
        self.n_labelled = 0

        self.labels_filepath = os.path.join(filepath, 'labels.pkl') if os.path.isdir(
            filepath) else f'{filepath}.labels.pkl'
        if os.path.exists(self.labels_filepath):
            self.labels = pickle.load(open(self.labels_filepath, 'rb'))
            for _, frame_labels in self.labels.items():
                self.n_labelled += sum(frame.complete for frame in frame_labels)
        else:
            self.labels = OrderedDict()

        # try to read it as an image
        bgr = cv2.imread(filepath)
        if bgr is not None:
            self.length = 1
            self.type_str = "img"
        else:
            # try to read it as a video file
            cap = cv2.VideoCapture(filepath)
            if cap.isOpened():
                self.length = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                self.type_str = "vid"
            else:
                self.rescan_files()

            cap.release()

    def rescan_files(self):
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(self.filepath)
        self.length = 0
        self.files = OrderedDict()

        for item in os.listdir(self.filepath):
            if 'labels.pkl' in item:
                continue
            # try opening it
            filepath = os.path.join(self.filepath, item)
            dataset = DataSet(filepath)
            self.files[filepath] = dataset
            if filepath in self.labels:
                self.n_labelled += sum(
                    label.complete for label in self.labels[filepath])
            if filepath not in self.labels:
                # instantiate an empty framelabels object for each example in the dataset
                self.labels[filepath] = [FrameLabels()
                                         for _ in range(len(dataset))]
            self.length += len(dataset)

        def directory_only_images():
            return any(self.files) and all([f.type_str == "img" for f in self.files.values()])

        if directory_only_images():
            self.type_str = "img-dir"
            self.image_files = self.files
            self.files = OrderedDict({self.filepath: self})
            self.labels = OrderedDict(
                {self.filepath: [label[0] for label in self.labels.values()]})
        else:
            if not os.path.isdir(filepath):
                raise Exception(
                    f"given filepath: {filepath} is neither a directory, nor image or video of recognizeable format")
            self.type_str = "dir"

    def read_frame(self, idx):
        "read frame by idx. only works for img-dir and video datasets"
        if self.type_str == "vid":
            cap = cv2.VideoCapture(self.filepath)
            assert cap.isOpened()

            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            _, bgr = cap.read()
        elif self.type_str == "img-dir":
            bgr = cv2.imread(
                next(islice(iter(self.image_files), idx, idx + 1)))
        else:
            raise Exception("Unsupported")

        return Frame(bgr, colorspace=ColorSpaces.BGR)

    def save(self):
        pickle.dump(self.labels, open(self.labels_filepath, 'wb'))

    def __len__(self):
        return self.length

    def __iter__(self):
        return DataSetIterator(self)
