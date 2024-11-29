import tkinter as tk
from tkinter import messagebox
import sounddevice as sd
import numpy as np
import threading
import wave

# GUI config
BG_COLOR = '#2C2F33'  # Dark gray
TEXT_COLOR = '#FFFFFF'  # White
FONT = ('Georgia', 12)

class VoiceRecorder:
    def __init__(self, master):
        self.master = master
        master.title("Voice Recorder")
        master.configure(bg=BG_COLOR)

        self.is_recording = False

        # Initialize variables
        self.frames = []
        self.stream = None

        # Default audio settings
        self.sample_rate = 44100
        self.channels = 1  # Changed from 2 to 1

        # Filename input frame
        filename_frame = tk.Frame(master, bg=BG_COLOR)
        filename_frame.pack(pady=10)

        self.filename_label = tk.Label(filename_frame, font=FONT, text="Enter filename:", bg=BG_COLOR, fg=TEXT_COLOR)
        self.filename_label.pack(side=tk.LEFT)

        self.filename_entry = tk.Entry(filename_frame)
        self.filename_entry.pack(side=tk.LEFT)

        # Record button
        self.record_button = tk.Button(master, text="Start Recording", font=FONT, command=self.toggle_recording)
        self.record_button.pack(pady=10)

        # Status label
        self.status_label = tk.Label(master, font=FONT, text="", bg=BG_COLOR, fg=TEXT_COLOR)
        self.status_label.pack(pady=10)

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
        self.record_button.config(text="Stop Recording", bg="red", fg="white")
        self.status_label.config(text="Recording...")

        # Start recording in a new thread
        self.frames = []  # Reset frames
        self.recording_thread = threading.Thread(target=self.record)
        self.recording_thread.start()

    def stop_recording(self):
        self.is_recording = False
        self.record_button.config(text="Start Recording", bg="SystemButtonFace", fg="black")
        self.status_label.config(text="Saving recording...")
        self.save_recording()

    def record(self):
        try:
            with sd.InputStream(samplerate=self.sample_rate, channels=self.channels, callback=self.audio_callback):
                while self.is_recording:
                    sd.sleep(100)
        except Exception as e:
            messagebox.showerror("Recording Error", str(e))
            self.is_recording = False
            self.record_button.config(text="Start Recording", bg="SystemButtonFace", fg="black")
            self.status_label.config(text="")

    def audio_callback(self, indata, status):
        if status:
            print(status)
        self.frames.append(indata.copy())

    def save_recording(self):
        if not self.frames:
            messagebox.showwarning("Recording Error", "No audio recorded.")
            self.status_label.config(text="")
            return

        # Convert list of numpy arrays to a single numpy array
        audio_data = np.concatenate(self.frames)

        # Normalize audio data
        audio_data = (audio_data * np.iinfo(np.int16).max).astype(np.int16)

        try:
            with wave.open(self.filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16 bits per sample
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_data.tobytes())
            messagebox.showinfo("Success", f"Recording saved as {self.filename}")
            self.status_label.config(text=f"Recording saved as {self.filename}")
        except Exception as e:
            messagebox.showerror("Saving Error", str(e))
            self.status_label.config(text="Saving failed.")

        # Reset frames and prepare for next recording
        self.frames = []
        self.status_label.config(text="Ready to record")

# Create the main window
root = tk.Tk()
app = VoiceRecorder(root)
root.mainloop()
