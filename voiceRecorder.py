import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from audioHandling import AudioManager
from guiHandling import GUIManager

# GUI styling constants
BG_COLOR = '#2C2F33'  # Dark gray background color
TEXT_COLOR = '#FFFFFF'  # White text color
FONT = ('Georgia', 12)  # Font style and size

class VoiceRecorderApp:
    def __init__(self, master):
        # Initialize main window settings
        self.master = master
        master.title("Voice Recorder")
        master.configure(bg=BG_COLOR)

        # Audio manager for handling recording operations
        self.audio_manager = AudioManager()

        # GUI manager for setting up the GUI
        self.gui_manager = GUIManager(master, self)

    def toggle_recording(self):
        # Toggle between start and stop recording states
        if not self.audio_manager.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        # Start recording if a valid filename is provided
        filename = self.gui_manager.get_filename()
        if not filename:
            messagebox.showwarning("Input Error", "Please enter a filename.")
            return

        if self.audio_manager.start_recording(filename):
            self.gui_manager.update_recording_state(True)

    def stop_recording(self):
        # Stop recording and save audio
        if self.audio_manager.stop_recording():
            self.gui_manager.update_recording_state(False)
            self.gui_manager.update_recordings_listbox()

    def play_recording(self):
        # Play back the recorded audio
        if self.audio_manager.audio_data is not None:
            self.audio_manager.play_audio()

    def on_recording_select(self, event):
        # Handle selection of a recording from the listbox
        filename = self.gui_manager.get_selected_recording()
        if filename:
            if self.audio_manager.load_recording(filename):
                self.gui_manager.update_playback_ready_state(filename)

# Create and run the GUI application
root = tk.Tk()
app = VoiceRecorderApp(root)
root.mainloop()
