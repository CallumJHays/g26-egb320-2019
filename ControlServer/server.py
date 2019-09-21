from sanic import Blueprint, Sanic, response
from sanic_cors import CORS
from pathlib import Path
from threading import Thread
import subprocess
import os
import sys
import io
import logging
import socketserver
from threading import Condition
from http import server
from sanic.websocket import WebSocketProtocol
import json
from inspect import cleandoc
import cv2


SERVER_BASE_DIR = Path(__file__).parents[0]
CLIENT_STATICS_DIR = SERVER_BASE_DIR / 'out'
SERVER_STATICS_DIR = SERVER_BASE_DIR / 'static'

app = Blueprint("ControlServer")


app.static('/', str(CLIENT_STATICS_DIR))

# helper


def relpath(*paths):
    return os.path.join(os.path.dirname(__file__), *paths)


@app.route('/')
async def index(req):
    return await response.file(CLIENT_STATICS_DIR / 'index.html')


class ControlServer(Sanic):

    def __init__(self, port, video_stream, vision_system, drive_system, autobuild=True):
        super().__init__()

        self.blueprint(app)
        self.add_route(self.live_stream, '/live_stream.mjpg')
        self.add_websocket_route(self.remote_control, '/remote_control')
        CORS(self)
        self.port = port
        self.video_stream = video_stream
        self.vision_system = vision_system
        self.drive_system = drive_system

        # eject the nextjs frontend to static files for serving
        if autobuild:
            prev_wd = os.getcwd()
            os.chdir(SERVER_BASE_DIR)
            subprocess.call("npm run export".split(" "))
            # if nextjs static serving is setup this can be avoided
            subprocess.call(
                f"cp {SERVER_STATICS_DIR}/* {CLIENT_STATICS_DIR}/*".split(" "))
            os.chdir(prev_wd)

    async def live_stream(self, req):
        async def stream(res):
            for frame in self.video_stream:
                bgr = frame.get(ColorSpaces.BGR)
                jpeg = cv2.imencode('.jpg', bgr)[1].tostring()
                packet = cleandoc(f"""\
                --frame\r
                Content-Type: image/jpeg\r
                Content-Length: {len(jpeg)}\r
                \r
                """).encode('utf8')
                packet += jpeg + b"\r\n"
                await res.write(packet)

        return response.stream(
            stream,
            headers={
                'Age': 0,
                'Cache-Control': 'no-cache, private',
                'Pragma': 'no-cache',
                'Content-Type': 'multipart/x-mixed-replace; boundary=frame',
            }
        )

    async def remote_control(self, req, ws):
        while True:
            cmd_json = await ws.recv()
            cmd = json.loads(cmd_json)
            self.drive_system.set_desired_motion(
                cmd['x'], cmd['y'], cmd['omega'])

    def run(self, *args, **kwargs):
        print('running')
        super().run(*args, **kwargs, host='0.0.0.0', port=self.port)


if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

    from VisionSystem.DetectionModel import ThreshBlob, ColorSpaces
    from VisionSystem import VideoStream, VisionSystem, VisualObject

    # use any available live feed device such as a webcam
    video_stream = VideoStream(downsample_scale=8)

    objects_to_size_and_result_limit = {
        "ball": ((0.043, 0.043, 0.043), 1),
        "obstacle": ((0.18, 0.18, 0.2), None),
        # 30 centimetres long, 10 cm high? i guess
        # "blue_goal": ((0.3, 0.3, 0.1), 1),
        # "yellow_goal": ((0.3, 0.3, 0.1), 1)
    }

    vision_system = VisionSystem(camera_pixel_width=video_stream.resolution[0], objects_to_track={
        name: VisualObject(
            real_size=size,
            detection_model=ThreshBlob.load(
                relpath("..", "models", f"{name}.threshblob.pkl")),
            result_limit=result_limit
        ) for name, (size, result_limit) in objects_to_size_and_result_limit.items()
    })

    try:
        from DriveSystem import DriveSystem
        drive_system = DriveSystem()
    except ModuleNotFoundError:
        # not on the raspberry pi, just mock it
        def drive_system():
            pass

        drive_system.set_desired_motion = lambda x, y, omega: print(
            'mock drive system driving', x, y, omega)

    ControlServer(
        port=8080,
        # send a shallow copy of the video stream so that when used as an iterator by the control server it uses
        video_stream=video_stream,
        vision_system=vision_system,
        drive_system=drive_system,
        autobuild=False
    ).run()
