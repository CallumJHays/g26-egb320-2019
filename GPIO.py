"""
    However, doesn't actually use the library's API at all - Instead circumventing to
    the fantastic pigpio library, which is like 100x faster and better especially 
    with regards to pwm. (It uses software magic to reach 5 microsecond resolution for pwm
    at practically 0 cost to the CPU. Confused? So am I! Does it really work? I hope so!)

    Always uses GPIO BCM mode (ie refer to the numbers in the outer labels in the pinouts)
"""

import pigpio
from pigpio import INPUT, OUTPUT, ON, OFF
import RPi.GPIO
from RPi.GPIO import OUT
from inspect import getframeinfo, stack
import atexit
from abc import ABC
import os

class GPIODevice(ABC):

    config = {}

    def setup(self):
        if len(self.config) == 0:
            raise NotImplementedError("GPIO Device object has an empty config")

        for pin, cfg in self.config.values():
            if type(cfg) == GPIODevice:
                cfg.setup()
            elif type(cfg) == int:
                setup(pin, cfg)
            else:
                raise Exception(f"config variable of type {type(cfg)}: {cfg}")

PI = pigpio.pi()

# utilise Python exception handling
pigpio.exceptions = True


def setmode(cls):
    raise NotImplementedError("Only use BCM Mode Pin Numbering")
        

# for GPIO -related errors
class Error(Exception):
    pass


# this is our static global config variable. it'll help make sure
# we don't step on eachothers' toes.
config = {}


class PWM(RPi.GPIO.PWM):

    def __init__(self, pin, frequency=0):
        self.pin = pin
        self.frequency = frequency
        self.dutycycle = None

        self.ChangeFrequency(self.frequency)


    def ChangeDutyCycle(self, dutycycle):
        assert 0 <= dutycycle and dutycycle <= 100
        dutycycle = int(2.55 * dutycycle)
        PI.set_PWM_dutycycle(self.pin, dutycycle)


    def ChangeFrequency(self, frequency):
        PI.set_PWM_frequency(self.pin, int(frequency))

    def start(self, dutycycle):
        self.ChangeDutyCycle(dutycycle)

    def stop(self):
        self.ChangeDutyCycle(0)


def setup(pin, direction):
    if config == {}: # if this is the first time anything has happened, 
        atexit.register(cleanup)

    if pin in config:
        raise Error(f"pin {pin} already in use. (check its declaration at {config[pin][0]})")

    PI.set_mode(pin, pigpio.OUTPUT if direction == OUT else pigpio.INPUT)

    caller = getframeinfo(stack()[1][0])

    config[pin] = (
        f"{os.path.abspath(caller.filename)}, line {caller.lineno}",
        direction
    )


def handle_misuse(expected_direction):
    def wrapper(read_or_write_func):
        def result(pin, state=None):
            if pin not in config:
                raise Error(f"pin {pin} has not yet been setup()'d")
            declaration, direction = config[pin]
            if direction != expected_direction:
                raise Error(f"""\
                    pin {pin} is attempting to output but has not been setup()'d with direction=OUTPUT. \
                    Expected {expected_direction}, got {direction}. Refer to declaration: {declaration}""")
            
        return result
    return wrapper


@handle_misuse(expected_direction=OUTPUT)
def output(pin, state):
    PI.write(pin, state)


@handle_misuse(expected_direction=INPUT)
def input(pin):
    if pin not in config:
        raise Error(f"pin {pin} has not yet been setup()'d")
    return PI.read(pin)


def cleanup():
    for pin, (_, direc) in config.items():
        if direc == OUTPUT:
            PI.write(pin, OFF)
        
        PI.set_mode(pin, INPUT)