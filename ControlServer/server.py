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
import asyncio
from ffmpy3 import FFmpeg


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
        self.add_route(self.live_stream_mjpg, '/live_stream.mjpg')
        self.add_websocket_route(self.live_stream_ws_x264, '/live_stream')
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

    async def live_stream_ws_x264(self, req, ws):
        # implements a x264 livestream that works with the WSAvcPlayer used by the LiveStream component
        # I assume this is the thing in a x264 livestream that specifies the beginning of a new frame
        NAL_SEPERATOR = b'\x00\x00\x00\x01'
        NAL_SEP_LEN = len(NAL_SEPERATOR)

        vid_width, vid_height = self.video_stream.resolution

        transcoder_process = await FFmpeg(
            executable="docker run jrottenberg/ffmpeg",
            inputs={
                'pipe:0': f'-f mjpeg'},
            outputs={
                'pipe:1': f'-c:v h264 -f h264 -s:v {vid_width}x{vid_height}'}
        ).run_async(stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)

        # iterate until the client disconnects and teardown occurs
        for frame in self.video_stream:
            bgr = frame.get(ColorSpaces.BGR)
            jpeg = cv2.imencode('.jpg', bgr)[1].tostring()

            # an mjpg stream is literally just raw jpeg data one after the other - nice and easy!
            # write to the stream which will trigger ffmpeg in the other process to start transcoding to a h264 frame
            resp, err = await transcoder_process.communicate(jpeg)
            assert not err and not resp

            # buffer the output until the frame separator is encountered
            buffer = io.BytesIO()
            byte_ranges_scanned = 0

            def buffer_NAL_SEPARATOR_idx():
                global byte_ranges_scanned
                buf_len = buffer.getbuffer().nbytes

                while buf_len > 4 and buf_len > (byte_ranges_scanned + NAL_SEP_LEN):
                    buffer.seek(byte_ranges_scanned)
                    curr_range = buffer.read(NAL_SEP_LEN)
                    byte_ranges_scanned += 1
                    if curr_range == NAL_SEPERATOR:
                        buffer.seek(buf_len)
                        return byte_ranges_scanned - 1
                buffer.seek(buf_len)
                return -1

            # imitate the nodejs codes' stream.split(NAL_SEPERATOR) function
            while buffer_NAL_SEPARATOR_idx() == -1:
                reply, err = await transcoder_process.communicate()
                # print('got reply', reply, 'got err', err)
                if reply:
                    print(reply)
                buffer.write(reply)

            # the buffer now contains the full x264 frame, as well as some (erroneous?) extra data
            buffer.seek(0)
            x264_frame = buffer.read(buffer_NAL_SEPARATOR_idx() + 1)
            buffer.seek(NAL_SEP_LEN, 1)
            await ws.send(x264_frame)

    async def live_stream_mjpg(self, req):
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
            'mock drive', x, y, omega)

    ControlServer(
        port=8080,
        # send a shallow copy of the video stream so that when used as an iterator by the control server it uses
        video_stream=video_stream,
        vision_system=vision_system,
        drive_system=drive_system,
        autobuild=False
    ).run()
