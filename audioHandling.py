import sounddevice as sd
import numpy as np
import wave
import os
import threading
import tkinter as tk
from tkinter import messagebox

class AudioManager:
    def __init__(self):
        # Recorder state and data
        self.is_recording = False
        self.frames = []
        self.lock = threading.Lock()
        self.audio_data = None
        self.sample_rate = 44100
        self.channels = 1
        self.filename = None

    def start_recording(self, filename):
        # Ensure valid filename
        filename = filename if filename.endswith(".wav") else filename + ".wav"
        self.filename = os.path.join(os.getcwd(), filename)

        if os.path.exists(self.filename):
            messagebox.showwarning("File Exists", "A file with this name already exists.")
            return False

        self.is_recording = True
        self.frames = []
        self.audio_data = None
        self.recording_thread = threading.Thread(target=self._record)
        self.recording_thread.start()
        return True

    def stop_recording(self):
        with self.lock:
            self.is_recording = False
        self.recording_thread.join()
        return self._save_recording()

    def _record(self):
        try:
            with sd.InputStream(samplerate=self.sample_rate, channels=self.channels, callback=self._audio_callback):
                while self.is_recording:
                    sd.sleep(100)
        except Exception as e:
            messagebox.showerror("Recording Error", str(e))
            with self.lock:
                self.is_recording = False

    def _audio_callback(self, indata, frames, time, status):
        if status:
            print(status)
        with self.lock:
            if self.is_recording:
                self.frames.append(indata.copy())

    def _save_recording(self):
        if not self.frames:
            messagebox.showwarning("Recording Error", "No audio recorded.")
            return False

        audio_data = np.concatenate(self.frames)
        audio_data = (audio_data * np.iinfo(np.int16).max).astype(np.int16)
        self.audio_data = audio_data

        try:
            with wave.open(self.filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_data.tobytes())
            messagebox.showinfo("Success", f"Recording saved as {self.filename}")
            return True
        except Exception as e:
            messagebox.showerror("Saving Error", str(e))
            return False

    def play_audio(self):
        try:
            sd.play(self.audio_data, self.sample_rate)
            sd.wait()
        except Exception as e:
            messagebox.showerror("Playback Error", str(e))

    def load_recording(self, filename):
        try:
            self.filename = os.path.join(os.getcwd(), filename)
            with wave.open(self.filename, 'rb') as wf:
                self.sample_rate = wf.getframerate()
                self.channels = wf.getnchannels()
                frames = wf.readframes(wf.getnframes())
                self.audio_data = np.frombuffer(frames, dtype=np.int16)
            return True
        except Exception as e:
            messagebox.showerror("Loading Error", str(e))
            return False