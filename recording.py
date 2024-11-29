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
        self.audio_data = None  # Add this line

        # Default audio settings
        self.sample_rate = 44100
        self.channels = 1  # Changed from 2 to 1

        # Configure grid layout
        master.columnconfigure(0, weight=1)
        master.columnconfigure(1, weight=3)
        master.rowconfigure(0, weight=1)
        master.rowconfigure(1, weight=1)
        master.rowconfigure(2, weight=1)

        # Filename input
        self.filename_label = tk.Label(master, font=FONT, text="📁 Enter filename:", bg=BG_COLOR, fg=TEXT_COLOR)
        self.filename_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.E)

        self.filename_entry = tk.Entry(master, font=FONT)
        self.filename_entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W+tk.E)

        # Control buttons
        self.record_button = tk.Button(master, text="🎤 Start Recording", font=FONT, command=self.toggle_recording, width=15)
        self.record_button.grid(row=1, column=0, padx=10, pady=10, sticky=tk.E)

        self.play_button = tk.Button(master, text="▶ Play Recording", font=FONT, command=self.play_recording, state=tk.DISABLED, width=15)
        self.play_button.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)

        # Status label spanning both columns
        self.status_label = tk.Label(master, font=FONT, text="", bg=BG_COLOR, fg=TEXT_COLOR)
        self.status_label.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

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
        self.play_button.config(state=tk.DISABLED)  # Disable play button during recording

        # Start recording in a new thread
        self.frames = []  # Reset frames
        self.audio_data = None  # Reset audio data
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

    # Updated the audio_callback method to accept the correct number of arguments
    def audio_callback(self, indata, frames, time, status):
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
        self.audio_data = audio_data  # Store audio data for playback

        try:
            with wave.open(self.filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16 bits per sample
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_data.tobytes())
            messagebox.showinfo("Success", f"Recording saved as {self.filename}")
            self.status_label.config(text=f"Recording saved as {self.filename}")
            self.play_button.config(state=tk.NORMAL)  # Enable play button after saving
        except Exception as e:
            messagebox.showerror("Saving Error", str(e))
            self.status_label.config(text="Saving failed.")

        # Reset frames and prepare for next recording
        self.frames = []
        self.status_label.config(text="Ready to record")

    def play_recording(self):
        if hasattr(self, 'audio_data') and self.audio_data is not None:
            try:
                sd.play(self.audio_data, self.sample_rate)
                sd.wait()  # Wait until audio is finished playing
            except Exception as e:
                messagebox.showerror("Playback Error", str(e))
        else:
            messagebox.showwarning("Playback Error", "No recording to play.")

# Create the main window
root = tk.Tk()
app = VoiceRecorder(root)
root.mainloop()
