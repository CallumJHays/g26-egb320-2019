from __future__ import print_function
from pyngrok import ngrok

from email.mime.text import MIMEText
import os.path
import pickle
import base64
import smtplib
import ssl

import signal

import os
import socket
from urllib.request import urlopen, URLError


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


def format_email(fr, to, subject, message):
    return """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (fr, to, subject, message)


def main():
    SSL_PORT = 465
    EMAIL = "egb320.2019.g26@gmail.com"
    EMAIL_PASSWORD = "rustisthebest"
    EMAIL_SERVER = "smtp.gmail.com"

    print("Waiting for an internet connection...")
    wait_for_internet_connection()

    print("Setting up an ngrok tunnel")
    public_ssh_url = ngrok.connect(22, 'tcp')
    print("ngrok public ssh url:", public_ssh_url)

    lan_ip = get_lan_ip()
    print("local ip:", lan_ip)

    print("Sending email to", EMAIL, "with Gmail SMTP server")
    with smtplib.SMTP_SSL(EMAIL_SERVER, SSL_PORT, context=ssl.create_default_context()) as server:
        server.ehlo()
        server.login(EMAIL, EMAIL_PASSWORD)

        server.sendmail(EMAIL, EMAIL, format_email(
            EMAIL, EMAIL, "SSH: %s" % (lan_ip,), "local: %s\nglobal: %s" % (lan_ip, public_ssh_url)))

    print("Sent detail update to", EMAIL)

    # pause until new data is sent to this process from another (will never happen)
    # this allows the ngrok daemon (running on a different python thread) to stay online while we do other things
    signal.pause()

    # TODO: track local IP changes and update the gmail


if __name__ == '__main__':
    main()
