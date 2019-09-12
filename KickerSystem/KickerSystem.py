from GPIO import GPIO
import time


class KickerSystem():

    def __init__(self):
        raise NotImplementedError

    def start_dribbling(self):
        raise NotImplementedError

    def stop_dribbling(self):
        raise NotImplementedError

    def kick(self):
        raise NotImplementedError
