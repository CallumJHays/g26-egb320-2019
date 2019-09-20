import cv2
from threading import Thread, Event
import numpy as np
from .DetectionModel import Frame, ColorSpaces
from time import time
try:
    from picamera import PiCamera, PiResolution
    PICAMERA_MODE = True
except Exception:
    PICAMERA_MODE = False
    

PI_CAM_SENSOR_MODE = 5
PI_CAM_RESOLUTION = (1640, 922)

class FrameIterator():
    
    def __init__(self, video_stream):
        self.stream = video_stream
    
    def __next__(self):
        stream = self.stream
        if stream.on_disk:
            frame = stream.read_frame(stream.frame_idx)
            stream.frame_idx += 1
            return frame
        else:
            if not stream.started:
                stream.start()
            stream.new_frame_event.wait() # blocks until there is a new frame (when strea.new_frame.set() is called)
            image = stream.image_buffer

        if image.shape != stream.resolution + (3,):
            image = cv2.resize(image, stream.resolution)

        return Frame(image, ColorSpaces.BGR)


# Asynchronous camera / video-stream class
class VideoStream():

    def __init__(self, video_path=None, downsample_scale=1, rotate_90_n=0):
        self.pi_cam = None
        self.on_disk = video_path is not None
        self.rotate_90_n = rotate_90_n
        
        if self.on_disk:
            self.frame_idx = 0

            self.cap = cv2.VideoCapture(video_path)
            self.on_disk = True
            self.resolution = (
                int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) / downsample_scale),
                int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) / downsample_scale),
            )
        else:
            if PICAMERA_MODE:
                self.resolution = PiResolution(
                    int(PI_CAM_RESOLUTION[0] / downsample_scale),
                    int(PI_CAM_RESOLUTION[1] / downsample_scale),
                ).pad()
                print('self.resolution', self.resolution)
                self.pi_cam = PiCamera(sensor_mode=PI_CAM_SENSOR_MODE, resolution=self.resolution)
            else:
                self.cap = cv2.VideoCapture(0)
                self.resolution = (
                    int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) / downsample_scale),
                    int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) / downsample_scale),
                )
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[1])
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[0])
                
            self.image_buffer = np.empty((self.resolution[0] * self.resolution[1] * 3,), dtype=np.uint8)
            self.new_frame_event = Event()
            self.new_frame_event.clear()
            self.started = False
            self.stopped = False


    def __iter__(self):
        return FrameIterator(self)


    def update_forever(self):
        while True:
            self.new_frame_event.clear() # a new frame is on the way!
            if self.pi_cam:
                image = np.empty((self.resolution[0] * self.resolution[1] * 3,), dtype=np.uint8)
                self.pi_cam.capture(image, 'bgr', use_video_port=True)
                self.image_buffer = image.reshape(self.resolution.transpose() + (3,))
            else:
                _, self.image_buffer = self.cap.read()
            
            if self.rotate_90_n > 0:
                self.image_buffer = np.rot90(self.image_buffer, k=self.rotate_90_n)
            
            self.new_frame_event.set() # let consumers know the new frame is ready

            if self.stopped:
                return


    def close(self):
        self.stopped = True
        if self.pi_cam:
            self.pi_cam.close()
        else:
            self.cap.release()
            

    def read_frame(self, frame_idx):
        if not self.on_disk:
            raise Exception("Reading specific frames is not possible in a live feed... unless another feature is added")

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        _, bgr_img = self.cap.read()
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        if bgr_img.shape != self.resolution + (3,):
            bgr_img = cv2.resize(bgr_img, self.resolution)
        return Frame(bgr_img, ColorSpaces.BGR)

    
    def start(self):
        Thread(target=self.update_forever).start()
        self.started = True