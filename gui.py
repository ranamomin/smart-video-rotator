# gui.py

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import shutil
import threading
import sys

# Add the directory of model_utils and rotate_utils to sys.path
# This ensures that the imports work correctly when gui.py is run
script_dir = os.path.dirname(__file__)
if script_dir not in sys.path:
    sys.path.append(script_dir)

# Import your existing logic
from model_utils import analyze_person_in_video
from rotate_utils import rotate_video, get_video_resolution

class VideoCorrectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Orientation Corrector")
        self.root.geometry("600x400")
        # --- MODIFIED: Allow window to be resizable ---
        self.root.resizable(True, True) 
        # --- ADDED: Set minimum window size ---
        self.root.minsize(600, 400)

        # Styling
        self.style = ttk.Style()
        self.style.theme_use('clam') # 'clam', 'alt', 'default', 'classic'
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', font=('Helvetica', 10), padding=10)
        self.style.configure('TLabel', font=('Helvetica', 10), background='#f0f0f0')
        self.style.configure('TEntry', font=('Helvetica', 10), padding=5)
        self.style.configure('TProgressbar', thickness=20)

        # Main frame
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Input Folder Selection
        self.input_label = ttk.Label(self.main_frame, text="Select Input Video Folder:")
        self.input_label.grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.input_path_var = tk.StringVar()
        self.input_entry = ttk.Entry(self.main_frame, textvariable=self.input_path_var, width=50)
        self.input_entry.grid(row=1, column=0, padx=(0, 10), sticky="ew")

        self.browse_button = ttk.Button(self.main_frame, text="Browse", command=self.browse_folder)
        self.browse_button.grid(row=1, column=1, sticky="w")

        # Output Folder Display (Informational)
        self.output_label = ttk.Label(self.main_frame, text="Output videos will be saved in 'corrected' subfolder.")
        self.output_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 0))

        # Start Processing Button
        self.start_button = ttk.Button(self.main_frame, text="Start Processing", command=self.start_processing)
        self.start_button.grid(row=3, column=0, columnspan=2, pady=(20, 10))

        # Progress Bar
        self.progress_label = ttk.Label(self.main_frame, text="Progress:")
        self.progress_label.grid(row=4, column=0, sticky="w", pady=(10, 5))

        self.progress_bar = ttk.Progressbar(self.main_frame, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.grid(row=5, column=0, columnspan=2, sticky="ew")

        # Status Label
        self.status_label = ttk.Label(self.main_frame, text="Ready.")
        self.status_label.grid(row=6, column=0, columnspan=2, sticky="w", pady=(10, 0))

        # Configure grid weights for resizing
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=0) # Button column doesn't expand
        # --- MODIFIED: Allow rows to expand vertically ---
        self.main_frame.rowconfigure(5, weight=1) # Allow progress bar row to expand
        self.main_frame.rowconfigure(6, weight=1) # Allow status label row to expand

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.input_path_var.set(folder_selected)

    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update_idletasks() # Update GUI immediately

    def update_progress(self, value):
        self.progress_bar['value'] = value
        self.root.update_idletasks()

    def start_processing(self):
        input_folder = self.input_path_var.get()
        if not input_folder or not os.path.isdir(input_folder):
            messagebox.showerror("Invalid Input", "Please select a valid input folder.")
            return

        self.start_button.config(state=tk.DISABLED)
        self.browse_button.config(state=tk.DISABLED)
        self.update_status("Starting processing...")
        self.progress_bar['value'] = 0

        # Run processing in a separate thread
        self.processing_thread = threading.Thread(target=self._process_videos_thread, args=(input_folder,))
        self.processing_thread.start()

    def _process_videos_thread(self, input_folder):
        output_folder = os.path.join(input_folder, "corrected")
        
        try:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            video_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))]
            total_videos = len(video_files)

            if total_videos == 0:
                self.update_status("No supported video files found in the selected folder.")
                return

            for i, filename in enumerate(video_files):
                video_path = os.path.join(input_folder, filename)
                output_path = os.path.join(output_folder, filename)

                self.update_status(f"Analyzing: {filename} ({i+1}/{total_videos})")
                
                body_axis, head_position = analyze_person_in_video(video_path)

                if body_axis is None:
                    self.update_status(f"Skipping {filename}: No person detected or error during analysis.")
                    self.update_progress((i + 1) / total_videos * 100)
                    continue

                self.update_status(f"Determining rotation for {filename} (Body: {body_axis}, Head: {head_position})")
                
                # Logic to determine the rotation needed to make the video portrait upright
                rotation_needed = False
                direction = None

                if body_axis == "vertical" and head_position == "top":
                    self.update_status(f"{filename}: Already portrait upright. Copying...")
                    shutil.copy2(video_path, output_path) # Copy if no rotation needed
                elif body_axis == "vertical" and head_position == "bottom":
                    self.update_status(f"{filename}: Portrait upside-down. Rotating 180 degrees.")
                    direction = "180"
                    rotation_needed = True
                elif body_axis == "horizontal" and head_position == "right":
                    self.update_status(f"{filename}: Landscape, person head right. Rotating 90 degrees counter-clockwise.")
                    direction = "counterclockwise"
                    rotation_needed = True
                elif body_axis == "horizontal" and head_position == "left":
                    self.update_status(f"{filename}: Landscape, person head left. Rotating 90 degrees clockwise.")
                    direction = "clockwise"
                    rotation_needed = True
                else:
                    self.update_status(f"Skipping {filename}: Could not determine correct rotation.")
                    shutil.copy2(video_path, output_path) # Copy original if unknown rotation
                
                if rotation_needed:
                    self.update_status(f"Rotating: {filename}...")
                    rotate_video(video_path, output_path, direction=direction)

                self.update_progress((i + 1) / total_videos * 100)

            self.update_status("Processing complete!")
            messagebox.showinfo("Complete", "All videos processed successfully!")

        except Exception as e:
            self.update_status(f"An error occurred: {e}")
            messagebox.showerror("Error", f"An error occurred during processing: {e}")
        finally:
            self.start_button.config(state=tk.NORMAL)
            self.browse_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoCorrectorApp(root)
    root.mainloop()
