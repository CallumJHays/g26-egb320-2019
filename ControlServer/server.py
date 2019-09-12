from sanic import Blueprint, Sanic, response
from pathlib import Path
from threading import Thread
import subprocess
import os

SERVER_BASE_DIR = Path(__file__).parents[0]
CLIENT_STATICS_DIR = SERVER_BASE_DIR / 'out'

app = Blueprint("ControlServer")

app.static('/', str(CLIENT_STATICS_DIR))


@app.route('/')
async def index(req):
    return await response.file(CLIENT_STATICS_DIR / 'index.html')


class ControlServer():
    def __init__(self, port):
        self.server = Sanic()
        self.server.blueprint(app)
        self.port = port

        if not CLIENT_STATICS_DIR.exists():
            prev_wd = os.getcwd()
            os.chdir(SERVER_BASE_DIR)
            subprocess.call("npx next export".split(" "))
            os.chdir(prev_wd)
    
    def run_indefinitely(self):
        self.server.run(host='0.0.0.0', port=self.port)