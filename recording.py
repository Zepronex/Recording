import tkinter as tk
from tkinter import messagebox
import sounddevice as sd
import numpy as np
import threading
import wave

class VoiceRecorder:
    def __init__(self, master):
        self.master = master
        master.title("Voice Recorder")

        self.is_recording = False

        # Filename input
        self.filename_label = tk.Label(master, text="Enter filename:")
        self.filename_label.pack()

        self.filename_entry = tk.Entry(master)
        self.filename_entry.pack()

        # Record button
        self.record_button = tk.Button(master, text="Start Recording", command=self.toggle_recording)
        self.record_button.pack(pady=10)

        # Initialize variables
        self.frames = []
        self.stream = None

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        filename = self.filename_entry.get()
        if not filename:
            messagebox.showwarning("Input Error", "Please enter a filename.")
            return

        self.filename = filename if filename.endswith(".wav") else filename + ".wav"
        self.is_recording = True
        self.record_button.config(text="Stop Recording")

        # Start recording in a new thread
        self.recording_thread = threading.Thread(target=self.record)
        self.recording_thread.start()

    def stop_recording(self):
        self.is_recording = False
        self.record_button.config(text="Start Recording")
        self.save_recording()

    def record(self):
        try:
            with sd.InputStream(samplerate=44100, channels=2, callback=self.audio_callback):
                while self.is_recording:
                    sd.sleep(100)
        except Exception as e:
            messagebox.showerror("Recording Error", str(e))
            self.is_recording = False
            self.record_button.config(text="Start Recording")

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.frames.append(indata.copy())

    def save_recording(self):
        if not self.frames:
            messagebox.showwarning("Recording Error", "No audio recorded.")
            return

        # Convert list of numpy arrays to a single numpy array
        audio_data = np.concatenate(self.frames)

        # Normalize audio data
        audio_data = (audio_data * np.iinfo(np.int16).max).astype(np.int16)

        try:
            with wave.open(self.filename, 'wb') as wf:
                wf.setnchannels(2)
                wf.setsampwidth(2)  # 16 bits per sample
                wf.setframerate(44100)
                wf.writeframes(audio_data.tobytes())
            messagebox.showinfo("Success", f"Recording saved as {self.filename}")
        except Exception as e:
            messagebox.showerror("Saving Error", str(e))

        # Reset frames for next recording
        self.frames = []

# Create the main window
root = tk.Tk()
app = VoiceRecorder(root)
root.mainloop()
