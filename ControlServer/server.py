from sanic import Blueprint, Sanic, response
from pathlib import Path
from threading import Thread
import subprocess
import os, sys
import io
import logging
import socketserver
from threading import Condition
from http import server

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from VisionSystem import VideoStream, VisionSystem, VisualObject
from VisionSystem.DetectionModel import ThreshBlob

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


@app.get('/live_stream.mjpg')
async def live_stream(req):
    async def stream(res):

    return response.stream(stream, content_type='Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')


class ControlServer(Sanic):

    def __init__(self, port, video_stream, vision_system, autobuild=True):
        super().__init__()

        self.blueprint(app)
        self.port = port
        self.video_stream = video_stream
        self.vision_system = vision_system

        # eject the nextjs frontend to static files for serving
        if autobuild:
            prev_wd = os.getcwd()
            os.chdir(SERVER_BASE_DIR)
            subprocess.call("npm run export".split(" "))
            os.chdir(prev_wd)


with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    output = StreamingOutput()
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()


    def run_indefinitely(self):
        self.run(host='0.0.0.0', port=self.port)

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    frame = next(video_stream)
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    import copy

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
        video_stream=copy.copy(video_stream), # send a shallow copy of the video stream so that when used as an iterator by the control server it uses 
        vision_system=vision_system
    ).run()
