from __future__ import print_function
from pyngrok import ngrok
from email.mime.text import MIMEText
import os
import pickle
import base64
import smtplib
import ssl
import signal
import socket
from urllib.request import urlopen, URLError
from npm.bindings import npm_run
from pathlib import Path

from ControlServer import ControlServer
from VisionSystem import VisionSystem, VisualObject, VideoStream
from VisionSystem.DetectionModel import ThreshBlob


# helper
def relpath(*paths):
    return os.path.join(os.path.dirname(__file__), *paths)


def wait_for_internet_connection():
    while True:
        try:
            urlopen('https://google.com', timeout=1)
            return
        except URLError:
            pass


def get_lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def format_email(fr, to, subject, body):
    # is broken :(
    from email import encoders
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = fr
    message["To"] = to
    message["Subject"] = subject

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    return message.as_string()


# load detection models and setup vision system with all objects' sizes for distance
# detection
def setup_vision_system(resolution):
    objects_to_size_and_result_limit = [
        ("ball", (0.043, 0.043, 0.043), 1),
        ("obstacle", (0.18, 0.18, 0.2), None),
        # 30 centimetres long, 10 cm high? i guess
        ("blue_goal", (0.3, 0.3, 0.1), 1),
        ("yellow_goal", (0.3, 0.3, 0.1), 1)
    ]

    return VisionSystem(
        resolution=resolution,
        objects_to_track={
            name: VisualObject(
                real_size=size,
                detection_model=ThreshBlob.load(
                    relpath("models", f"{name}.threshblob.pkl")),
                result_limit=result_limit
            ) for name, size, result_limit in objects_to_size_and_result_limit
        }
    )


def main():
    CONTROL_SERVER_PORT = 3000

    try:
        from DriveSystem import DriveSystem
        drive_system = DriveSystem()

        from KickerSystem import KickerSystem
        kicker_system = KickerSystem()
        kicker_system.setup()
    except ModuleNotFoundError:
        # not on the raspberry pi, just mock it
        def drive_system():
            pass

        drive_system.set_desired_motion = lambda x, y, omega: print(
            'mock drive system driving', x, y, omega)

    print("Waiting for an internet connection...")
    wait_for_internet_connection()

    print("Setting up an ngrok tunnel to the control server")
    # public_ssh_url = ngrok.connect(22, 'tcp')
    control_server_url = ngrok.connect(CONTROL_SERVER_PORT, 'http')

    # print("ngrok public ssh url:", public_ssh_url)
    print("ngrok public control-server url:", control_server_url)

    lan_ip = get_lan_ip()
    print("local ip:", lan_ip)

    send_email(control_server_url, lan_ip, CONTROL_SERVER_PORT)

    print("Launching control server...")
    try:
        # video_stream = VideoStream(downsample_scale=8)
        # vision_system = setup_vision_system(video_stream.resolution)

        ControlServer(
            port=CONTROL_SERVER_PORT,
            video_stream=None,
            vision_system=None,
            drive_system=drive_system,
            kicker_system=kicker_system
        ).run()
    except Exception as e:
        print("Control server failed to launch with exception", e)


def send_email(control_server_url, lan_ip, CONTROL_SERVER_PORT):
    SSL_PORT = 465
    EMAIL = "egb320.2019.g26@gmail.com"
    EMAIL_PASSWORD = "rustisthebest"
    EMAIL_SERVER = "smtp.gmail.com"

    print("Sending email to", EMAIL, "with Gmail SMTP server")
    with smtplib.SMTP_SSL(EMAIL_SERVER, SSL_PORT, context=ssl.create_default_context()) as mail:
        mail.ehlo()
        mail.login(EMAIL, EMAIL_PASSWORD)

        subject = f"control_server: {control_server_url}"
        email_body = f"""\
        control_server: {control_server_url}
        local: {lan_ip}:{CONTROL_SERVER_PORT}
        global: Needs Ngrok account upgrade (paid) to use in tandem with control_server\
        """

        mail.sendmail(
            EMAIL, EMAIL,
            format_email(EMAIL, EMAIL, subject, email_body)
        )
    print("Sent detail update to", EMAIL)


if __name__ == '__main__':
    main()
