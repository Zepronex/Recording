import tkinter as tk
from tkinter import messagebox, ttk
import os

# GUI styling constants
BG_COLOR = '#2C2F33'  # Dark gray background color
TEXT_COLOR = '#FFFFFF'  # White text color
FONT = ('Georgia', 12)  # Font style and size

class GUIManager:
    def __init__(self, master, app):
        self.master = master
        self.app = app

        # Configure grid layout for GUI
        master.columnconfigure([0, 1], weight=1)
        master.rowconfigure([0, 1, 2, 3], weight=1)

        # Filename input field and label
        self.filename_label = tk.Label(master, font=FONT, text="📁 Enter filename:", bg=BG_COLOR, fg=TEXT_COLOR)
        self.filename_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.E)

        self.filename_entry = tk.Entry(master, font=FONT)
        self.filename_entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W+tk.E)

        # Buttons for recording and playback
        self.record_button = tk.Button(master, text="🎤 Start Recording", font=FONT, command=self.app.toggle_recording, width=15)
        self.record_button.grid(row=1, column=0, padx=10, pady=10, sticky=tk.E)

        self.play_button = tk.Button(master, text="▶ Play Recording", font=FONT, command=self.app.play_recording, state=tk.DISABLED, width=15)
        self.play_button.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)

        # Status label for feedback
        self.status_label = tk.Label(master, font=FONT, text="", bg=BG_COLOR, fg=TEXT_COLOR)
        self.status_label.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        # Listbox for browsing previous recordings with a scrollbar
        recordings_frame = tk.Frame(master)
        recordings_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W+tk.E)

        self.scrollbar = tk.Scrollbar(recordings_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.recordings_listbox = tk.Listbox(recordings_frame, font=FONT, bg=BG_COLOR, fg=TEXT_COLOR, yscrollcommand=self.scrollbar.set)
        self.recordings_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.recordings_listbox.yview)

        self.update_recordings_listbox()
        self.recordings_listbox.bind("<Double-1>", self.app.on_recording_select)

    def get_filename(self):
        # Get the filename from the entry field
        return self.filename_entry.get()

    def update_recording_state(self, is_recording):
        # Update the GUI elements based on recording state
        if is_recording:
            self.record_button.config(text="Stop Recording", bg="red", fg="white")
            self.status_label.config(text="Recording...")
            self.play_button.config(state=tk.DISABLED)
        else:
            self.record_button.config(text="Start Recording", bg="SystemButtonFace", fg="black")
            self.status_label.config(text="Recording stopped. Saving...")

    def update_recordings_listbox(self):
        # Update the listbox with available recordings
        self.recordings_listbox.delete(0, tk.END)
        for file in os.listdir(os.getcwd()):
            if file.endswith(".wav"):
                self.recordings_listbox.insert(tk.END, file)

    def get_selected_recording(self):
        # Get the selected recording from the listbox
        selection = self.recordings_listbox.curselection()
        if selection:
            return self.recordings_listbox.get(selection[0])
        return None

    def update_playback_ready_state(self, filename):
        # Update the GUI when a recording is loaded and ready for playback
        self.play_button.config(state=tk.NORMAL)
        self.status_label.config(text=f"Ready to play {filename}")
