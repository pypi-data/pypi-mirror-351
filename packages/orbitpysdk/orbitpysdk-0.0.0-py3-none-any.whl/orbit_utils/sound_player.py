import base64
import numpy as np
import time
import io
from pydub import AudioSegment
import sounddevice as sd

from PyQt5.QtCore import QThread, pyqtSignal


class SoundPlayer(QThread):
    decibel = pyqtSignal(int)
    finished = pyqtSignal(bool)
    def __init__(self, base64_audio):
        super().__init__()
        self.base64_audio = base64_audio
    def play_sound(self):
    # Step 2: Decode to binary
        audio_bytes = base64.b64decode(self.base64_audio)

        # Ses dosyasını oku
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
        samples = np.array(audio.get_array_of_samples(), dtype=np.int16)

        # play(audio)

        # Eğer stereo ise tek kanala düşür
        if audio.channels == 2:
            samples = samples.reshape((-1, 2))
            samples = samples.mean(axis=1).astype(np.int16)

        samples = samples.astype(np.float32) / 32768.0  # Normalize [-1.0, 1.0]

        sr = audio.frame_rate
        print(f"Sample Rate: {sr}, Total Samples: {len(samples)}")
        frame_rate = 30  # 30 FPS 
        frame_samples = sr // frame_rate

        amplitudes = [
            np.max(np.abs(samples[i * frame_samples: (i + 1) * frame_samples]))
            for i in range(len(samples) // frame_samples)
        ]

        min_amp, max_amp = min(amplitudes), max(amplitudes)

        start_time = time.time()

        # Sesi çal
        sd.play(samples, samplerate=sr)
        for i, amp in enumerate(amplitudes):
            lip_height = float(10 + (amp - min_amp) / (max_amp - min_amp) * 110) if max_amp != min_amp else 10.0

            elapsed_time = time.time() - start_time
            target_time = (i + 1) / frame_rate
            wait_time = max(0, target_time - elapsed_time)
            time.sleep(wait_time)
            self.decibel.emit(int(lip_height))
            # print(f"Decibel: {int(lip_height)} at time {wait_time:.2f}s")
        sd.wait()  # Ses bitene kadar bekle
        self.finished.emit(True)
    
    def run(self):
        self.play_sound()