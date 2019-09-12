import pigpio
from pigpio import INPUT, OUTPUT, ON, OFF
import RPi.GPIO
from inspect import getframeinfo, stack
import atexit
from abc import ABC


class GPIODevice(ABC):

    config = {}

    def setup(self):
        if len(self.config) == 0:
            raise NotImplementedError("GPIO Device object has an empty config")

        for pin, cfg in self.config.values():
            if type(cfg) == GPIODevice:
                cfg.setup()
            elif type(cfg) == int:
                GPIO.setup(pin, cfg)
            else:
                raise Exception(f"config variable of type {type(cfg)}: {cfg}")



class GPIO(RPi.GPIO):
    """
    GPIO class that forces separate use within the software according to a configuration
    that is passed around and edited by all the subsystems.

    Inherits from RPi.GPIO for type (and tutorial :) ) compatability.

    However, doesn't actually use the library's API at all - Instead circumventing to
    the fantastic pigpio library, which is like 100x faster and better especially 
    with regards to pwm. (It uses software magic to reach 1 microsecond resolution for pwm
    at practically 0 cost to the CPU. Confused? So am I! Does it really work? I hope so!)

    Always uses GPIO BCM mode (ie refer to the numbers in the outer labels in the pinouts)
    """

    PI = pigpio.pi()

    # utilise Python exception handling
    pigpio.exceptions = True

    @classmethod
    def setmode(cls):
        raise NotImplementedError("Only use BCM Mode Pin Numbering")
            

    # for GPIO -related errors
    class Error(Exception):
        pass


    # this is our static global config variable. it'll help make sure
    # we don't step on eachothers' toes.
    config = {}


    @classmethod
    def cleanup(cls):
        for pin, (_, direc) in cls.config.items():

            if direc == OUTPUT:
                cls.PI.write(pin, OFF)
            
            cls.PI.set_mode(pin, INPUT)
            cls.PI.set_pull_up_down(pin, pigpio.PUD_OFF)


    class PWM(RPi.GPIO.PWM):

        def __init__(self, pin, frequency):

            self.pin = pin
            self.frequency = frequency
            self.dutycycle = None
            
            self.ChangeFrequency(self.frequency)
            


        def ChangeDutyCycle(self, dutycycle):

            assert 0 <= dutycycle and dutycycle <= 100
            dutycycle = int(2.55 * dutycycle)
            GPIO.PI.set_PWM_dutycycle(dutycycle)


        def ChangeFrequency(self, frequency):
            GPIO.PI.set_PWM_frequency(frequency)

        def start(self, dutycycle):
            self.ChangeDutyCycle(dutycycle)


        def stop(self):
            self.ChangeDutyCycle(0)


    @classmethod
    def setup(cls, pin, direction):
        if cls.config == {}: # if this is the first time anything has happened, 
            atexit.register(cls.cleanup)

        if pin in cls.config:
            raise cls.Error(f"pin {pin} already in use. (check its declaration at {cls.config[pin][0]}")

        cls.PI.set_mode(pin, pigpio.OUTPUT if direction == super().OUTPUT else pigpio.INPUT)

        caller = getframeinfo(stack()[1][0])

        cls.config[pin] = (
            f"{caller.filename}, line {caller.lineno}",
            direction
        )


    @classmethod
    def output(cls, pin, state):
        if pin not in cls.config:
            raise cls.Error(f"pin {pin} has not yet been setup()'d")
        cls.PI.write(pin, state)


    @classmethod
    def input(cls, pin):
        if pin not in cls.config:
            raise cls.Error(f"pin {pin} has not yet been setup()'d")
        return cls.PI.read(pin)


