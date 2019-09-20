from sanic import Blueprint, Sanic, response
from sanic_cors import CORS
from pathlib import Path
from threading import Thread
import subprocess
import os, sys
import io
import logging
import socketserver
from threading import Condition
from http import server
from sanic.websocket import WebSocketProtocol

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from VisionSystem import VideoStream, VisionSystem, VisualObject
from VisionSystem.DetectionModel import ThreshBlob, ColorSpaces

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

    def __init__(self, port, video_stream, vision_system, autobuild=True):
        super().__init__()

        self.blueprint(app)
        self.add_route(self.live_stream, '/live_stream.mjpg')
        self.add_websocket_route(self.remote_control, '/remote_control')
        CORS(self)
        self.port = port
        self.video_stream = video_stream
        self.vision_system = vision_system

        # eject the nextjs frontend to static files for serving
        if autobuild:
            prev_wd = os.getcwd()
            os.chdir(SERVER_BASE_DIR)
            subprocess.call("npm run export".split(" "))
            os.chdir(prev_wd)

    
    async def live_stream(self, req):
        async def stream(res):
            raw_header = lambda name, val: f"{name}: {val}"
            for frame in self.video_stream:
                img = frame.get(ColorSpaces.BGR)
                # await res.write(f"""\
                # --FRAME\r\
                # {raw_header('Content-Type', 'image/jpeg')}\r
                # {raw_header('Content-Length', len(img))}\r
                # """)
                await res.write("Hello World")
                # await res.write('\r\n')

        return response.stream(
            stream,
            # headers={
            #     'Age': 0,
            #     'Cache-Control': 'no-cache, private',
            #     'Pragma': 'no-cache'
            # }
        )
    

    async def remote_control(self, req, ws):
        while True:
            cmd_json = await ws.recv()
            ws.send('got cmd', cmd_json)
    

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs, host='0.0.0.0', port=self.port, protocol=WebSocketProtocol)
        


if __name__ == "__main__":
    video_stream = VideoStream() # use any available live feed device such as a webcam
    
    objects_to_size_and_result_limit = {
        "ball": ((0.043, 0.043, 0.043), 1),
        "obstacle": ((0.18, 0.18, 0.2), None),
        "blue_goal": ((0.3, 0.3, 0.1), 1), # 30 centimetres long, 10 cm high? i guess
        "yellow_goal": ((0.3, 0.3, 0.1), 1)
    }

    vision_system = VisionSystem(camera_pixel_width=video_stream.resolution[0], objects_to_track={
        name: VisualObject(
            real_size=size,
            detection_model=ThreshBlob.load(relpath("..", "models", f"{name}.threshblob.pkl")),
            result_limit=result_limit
        ) for name, (size, result_limit) in objects_to_size_and_result_limit.items()
    })
    ControlServer(
        port=8080,
        video_stream=video_stream, # send a shallow copy of the video stream so that when used as an iterator by the control server it uses 
        vision_system=vision_system
    ).run()
