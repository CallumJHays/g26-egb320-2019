"""
    However, doesn't actually use the library's API at all - Instead circumventing to
    the fantastic pigpio library, which is like 100x faster and better especially 
    with regards to pwm. (It uses software magic to reach 5 microsecond resolution for pwm
    at practically 0 cost to the CPU. Confused? So am I! Does it really work? I hope so!)

    Always uses GPIO BCM mode (ie refer to the numbers in the outer labels in the pinouts)
"""

import RPIO
import RPi.GPIO
from RPi.GPIO import OUT
from inspect import getframeinfo, stack
import atexit
from abc import ABC
import os


def dynamic_config(func):
    def inner(self, *args, **kwargs):
        global devices, config

        # copy the list so that we don't use the same reference
        before = config.copy()
        func(self, *args, **kwargs)

        print('before', before)
        print('after', config)

        # define the dynamic config based on what pins have been added
        self.dynamic_config = { k: config[k] for k in set(config) - set(before)}
    return inner


class GPIODevice(ABC):

    # static config
    config = {}

    # dynamic configs can be done by calling GPIO.setup() within a GPIODevice method
    # decorated with the @GPIO.dynamic_config decorator (typically in __init__)

    def setup(self):
        devices[self] = []

        if not hasattr(self, 'dynamic_config'):
            self.dynamic_config = {}

        if len(self.config) == 0 and len(self.dynamic_config) == 0:
            raise NotImplementedError("GPIO Device object has an empty config (both static and dynamic)")

        for pin, cfg in { **self.config, **self.dynamic_config }.values():
            if type(cfg) == GPIODevice:
                cfg.setup()
            elif type(cfg) == int: # direction type
                setup(pin, cfg)
                devices[self].append((pin, cfg))
            else:
                raise Exception(f"config variable of type {type(cfg)}: {cfg}")


    def cleanup(self):
        cleanup((pin for pin, _ in devices[self]))
        del devices[self]


    def __del__(self):
        self.cleanup()


RPIO.setmode(RPIO.BOARD)


def setmode(cls):
    raise NotImplementedError("Only use Board Mode Pin Numbering")
        

# for GPIO -related errors; just extend the standard Exception but let people know it came from this module
class Error(Exception):
    pass


# this is our static global config variable. it'll help make sure
# we don't step on eachothers' toes.
config = {}


# keep track of the mapping between devices and the pins they actually end up using.
# this way devices can clean up their pins automagically with a device.cleanup() function.
# with this you can have two devices plugged into the same pins with one being deactivated
devices = {}


class PWM(RPi.GPIO.PWM, GPIODevice):

    MICROSEC_PER_SEC = 1000000
    N_DMA_CHANELS = 15
    USED_DMA_CHANNELS = []


    def __init__(self, pin, frequency=0):

        if len(self.USED_DMA_CHANNELS) == self.N_DMA_CHANELS:
            raise Error("Ran out of DMA channels with which to use hardware PWM")

        self.pin = pin
        self.frequency = frequency
        self.dutycycle = None

        self.dma = next(dma for dma in range(self.N_DMA_CHANELS) if dma not in self.USED_DMA_CHANNELS)
        RPIO.PWM.init_channel(self.dma)
        self.USED_DMA_CHANNELS.append(self.dma)

        self.ChangeFrequency(self.frequency)


    def ChangeDutyCycle(self, dutycycle):
        assert 0 <= dutycycle and dutycycle <= 100
        dutycycle = int(2.55 * dutycycle)
        self.servo.set_servo(self.pin, self.MICROSEC_PER_SEC // self.frequency)


    def ChangeFrequency(self, frequency):
        self.servo.set_servo(self.pin, self.MICROSEC_PER_SEC // self.frequency)


    def start(self, dutycycle):
        self.ChangeDutyCycle(dutycycle)


    def stop(self):
        self.ChangeDutyCycle(0)


    def cleanup(self):
        super().cleanup()
        RPIO.PWM.clear_channel_gpio(self.dma, self.pin)


def setup(pin, direction):
    global config

    if config == {}: # if this is the first time anything has happened, 
        atexit.register(cleanup)

    if pin in config:
        raise Error(f"pin {pin} already in use. (check its declaration at {config[pin][0]})")

    RPIO.setup(pin, RPIO.OUT if direction == OUT else RPIO.IN)

    caller = getframeinfo(stack()[1][0])

    config[pin] = (
        f"{os.path.abspath(caller.filename)}, line {caller.lineno}",
        direction
    )


def _handle_misuse(expected_direction):
    def wrapper(read_or_write_func):
        def result(pin, state=None):
            global config
            if pin not in config:
                raise Error(f"pin {pin} has not yet been setup()'d")
            declaration, direction = config[pin]
            if direction != expected_direction:
                raise Error(f"""\
                    pin {pin} is attempting to output but has not been setup()'d with direction=OUTPUT. \
                    Expected {expected_direction}, got {direction}. Refer to declaration: {declaration}""")
            
        return result
    return wrapper


@_handle_misuse(expected_direction=RPIO.OUT)
def output(pin, state):
    RPIO.output(pin, state)


@_handle_misuse(expected_direction=RPIO.IN)
def input(pin):
    return RPIO.input(pin)


def cleanup(pins=None):
    """
    Cleanup pins if left as None, will cleanup all the pins.
    Otherwise only the BCM pin numbers included in the pins[] array will be cleaned up
    """
    global devices

    # if all pins were removed, we should remove all devices too
    if pins == None:
        # delete the devices synchronously
        for device in devices:
            del device

        # we could have just set this, but the actual device.cleanup() destructor
        # would only be called "at some point in the future" by the python interpreter.
        # this could lead to weird unintended electrical defects.
        devices = {}
    
    else:
        # turn all the pins off and into input mode, then delete from config
        for pin in pins:
            _, direc = config[pin]

            if direc == OUT:
                RPIO.output(pin, RPIO.OUT)
            
            RPIO.setup(pin, RPIO.IN)
            del config[pin]
    
