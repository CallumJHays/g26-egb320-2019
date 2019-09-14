import librosa
import asyncio
import math
import GPIO

def _track_playing(play_func):
    async def inner(self, *args, skip_playing_check=False):
        if self.playing:
            raise Exception("Can only play one sound at a time currently")
        await play_func(self, *args)
        self.playing = False
    return inner


class PiezoSpeaker(GPIO.GPIODevice):

    # A1 - G2
    NOTE_SCALE = 'ABCDEFG'
    OCTAVE = 3
    SCALE = [55.00, 61.74, 65.41, 73.42, 82.41, 87.31, 98.00]
    REST = None # just use the symbol

    @GPIO.dynamic_config
    def __init__(self, pin, volume=50):
        super().__init__()
        assert 0 <= volume and volume <= 100
        GPIO.setup(pin, GPIO.OUT)
        self.pwm = GPIO.PWM(pin)
        self.playing = False
        self.set_volume(volume)

    
    def set_volume(self, volume):
        self.volume = volume
        self.pwm.ChangeDutyCycle(volume)


    @_track_playing
    async def play(self, sound_path):

        y, sr = librosa.load(sound_path)
        secs = len(y) / sr

        # a centroid is the main frequency playing at any timestep
        centroids = librosa.feature.spectral_centroid(y, sr)[0]
        secs_per_freq = secs / len(centroids)

        await self.play_frequencies(centroids, secs_per_freq, skip_playing_check=True)


    @_track_playing
    async def play_notes(self, notes, sec_per_note=0.5):
        frequencies = [
            int(
                self.SCALE[
                    self.NOTE_SCALE.index(note)
                ] * math.pow(2, self.OCTAVE - 1)
            )
            if note != ' '
            else self.REST
            for note in notes
        ]
        await self.play_frequencies(frequencies, sec_per_note, skip_playing_check=True)


    @_track_playing
    async def play_frequencies(self, frequencies, sec_per_freq=0.5):
        self.pwm.start(self.volume)

        for freq in frequencies:
            if freq == self.REST:
                self.pwm.stop()
                await asyncio.sleep(sec_per_freq)
                self.pwm.start(self.volume)
            else:
                self.pwm.ChangeFrequency(freq)
                await asyncio.sleep(sec_per_freq)

        self.pwm.stop()