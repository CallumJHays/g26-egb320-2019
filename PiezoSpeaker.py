import librosa
import asyncio

import GPIO


def _track_playing(play_func):
    async def inner(self, *args, skip_playing_check=False):
        if self.playing:
            raise Exception("Can only play one sound at a time currently")
        await play_func(self, *args)
        self.playing = False
    return inner

class PiezoSpeaker:

    # A4 - G5
    NOTE_SCALE = 'ABCDEF'
    SCALE = [440, 493.88, 523.25, 587.33, 659.25, 698.46, 783.99]

    def __init__(self, pin, volume=50):
        assert 0 <= volume and volume <= 100
        GPIO.setup(pin, GPIO.OUT)
        self.pwm = GPIO.PWM(pin)
        self.playing = False
        self.pwm.ChangeDutyCycle(volume)

    
    def set_volume(self, volume):
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
        frequencies = [self.SCALE[self.NOTE_SCALE.index(note)] for note in notes]
        await self.play_frequencies(frequencies, sec_per_note, skip_playing_check=True)


    @_track_playing
    async def play_frequencies(self, frequencies, sec_per_freq=0.5):
        self.pwm.start(50)

        for freq in frequencies:
            self.pwm.ChangeFrequency(freq)
            await asyncio.sleep(sec_per_freq)

        self.pwm.stop()