import librosa
import asyncio
import math
import GPIO
from gpiozero import TonalBuzzer
from gpiozero.tones import Tone
import numpy as np


def _track_playing(play_func):
    async def inner(self, *args, skip_playing_check=False):
        if self.playing:
            raise Exception("Can only play one sound at a time currently")
        await play_func(self, *args)
        self.playing = False
    return inner


class PiezoSpeaker(GPIO.GPIODevice):

    # A1 - G2
    NOTE_SCALE = 'C D EF G A B'
    OCTAVE = 4
    NOTE_FREQUENCIES = [
        261.63, 277.18, 293.66, 311.13,
        329.63, 349.23, 369.99, 392.00,
        415.30, 440.00, 466.16, 493.88
    ]
    REST = None # just use the symbol

    @GPIO.dynamic_config
    def __init__(self, pin, volume=50):
        super().__init__()
        assert 0 <= volume and volume <= 100
        self.buzzer = TonalBuzzer(pin)
        self.playing = False


    @_track_playing
    async def play(self, sound_path):
        print('loading mp3')
        y, sr = librosa.load(sound_path)
        secs = len(y) / sr

        # a centroid is the main frequency playing at any timestep
        print('computing centroids')
        cqt = librosa.feature.chroma_cqt(y, sr)
        secs_per_freq = secs / cqt.shape[1]

        await self.play_frequencies(
            [self.NOTE_FREQUENCIES[row_idx] for row_idx in np.argmax(cqt, 0)],
            secs_per_freq,
            skip_playing_check=True
        )


    @_track_playing
    async def play_notes(self, notes, sec_per_note=0.5):
        frequencies = [
            self.NOTE_FREQUENCIES[
                self.NOTE_SCALE.index(note)
            ]
            if note != ' '
            else self.REST
            for note in notes
        ]
        await self.play_frequencies(frequencies, sec_per_note, skip_playing_check=True)


    @_track_playing
    async def play_frequencies(self, frequencies, sec_per_freq=0.5):
        for freq in frequencies:
            if freq == self.REST:
                self.buzzer.stop()
                await asyncio.sleep(sec_per_freq)
            else:

                # only play frequencies that can be played. if it can't scale it by octave
                while (freq < self.buzzer.min_tone.frequency):
                    freq *= 2
                while (freq > self.buzzer.max_tone.frequency):
                    freq /= 2

                self.buzzer.play(Tone.from_frequency(freq))
                await asyncio.sleep(sec_per_freq)
        
        self.buzzer.stop()
