import librosa
import asyncio

from GPIO import GPIO


class PiezoSpeaker:

    def __init__(self, pin, volume=50):
        GPIO.setup(pin, GPIO.OUT)
        self.pwm = GPIO.PWM(pin)
        self.playing = False
        self.pwm.ChangeDutyCycle(volume)

    
    def set_volume(self, volume):
        self.pwm.ChangeDutyCycle(volume)


    async def play(self, sound_path):
        if self.playing:
            raise Exception("Can only play one sound at a time currently")

        self.playing = True
        y, sr = librosa.load(sound_path)
        secs = len(y) / sr

        # a centroid is the main frequency playing at any timestep
        centroids = librosa.feature.spectral_centroid(y, sr)[0]
        secs_per_centroid = secs / len(centroids)

        self.pwm.start(50)

        for freq in centroids:
            self.pwm.ChangeFrequency(freq)
            await asyncio.sleep(secs_per_centroid)

        self.pwm.stop()
        self.playing = False


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    speaker = PiezoSpeaker(18)
    loop.run_until_complete(speaker.play("./data/ImperialMarch"))