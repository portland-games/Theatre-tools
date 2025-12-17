# Ensure Python 3.10 is used
import sys
if not (sys.version_info.major == 3 and sys.version_info.minor == 10):
    sys.stderr.write("This script requires Python 3.10.\n")
    sys.exit(1)

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox
import subprocess
import os
import threading
import signal
from tkinter import Toplevel
import vlc
from tkinter import ttk
import random

# Ensure query_formats is defined at the top of the script
def query_formats():
    """Run yt-dlp -F to query available formats."""
    url = youtube_url.get()
    if not url:
        messagebox.showerror("Error", "No URL provided.")
        return

    list_formats_command = f"yt-dlp -F \"{url}\""
    log_message("Querying available formats...")
    run_command(list_formats_command)

def run_command(command):
    """Run a shell command and capture output."""
    try:
        log_message(f"Running command: {command}")
        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)

        # Run the command with a timeout to prevent hanging
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, cwd=output_dir, timeout=300
        )

        if result.returncode == 0:
            log_message(result.stdout)
            return result.stdout
        else:
            log_message(f"Error: {result.stderr}")
            return result.stderr

    except subprocess.TimeoutExpired:
        log_message("Error: Command timed out.")
        return "Command timed out."

    except Exception as e:
        log_message(f"Unexpected error: {str(e)}")
        return str(e)

def browse_file():
    """Open file dialog to select a video file."""
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.mkv;*.avi;*.mov;*.webm;*.flv;*.ogg")])
    if file_path:
        selected_file.set(file_path)
        update_preview(file_path)

def update_preview(file_path):
    """Update the video preview and recreate the preview frames from random positions."""
    preview_label.config(text=f"Preview: {os.path.basename(file_path)}")

    # Enable the Play button when a video is selected
    play_button.config(state="normal")

    # Delete existing preview frames
    frames_dir = os.path.abspath(os.path.join(os.getcwd(), "output", "frames"))
    if os.path.exists(frames_dir):
        for file in os.listdir(frames_dir):
            file_path = os.path.join(frames_dir, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)  # Remove the file
                    log_message(f"Deleted frame: {file_path}")
            except Exception as e:
                log_message(f"Failed to delete {file_path}: {e}")

    # Recreate the preview frames from random positions
    os.makedirs(frames_dir, exist_ok=True)
    duration_command = f"ffprobe -i \"{file_path}\" -show_entries format=duration -v quiet -of csv=\"p=0\""
    duration_output = run_command(duration_command).strip()
    try:
        duration = float(duration_output)
        random_times = sorted([random.uniform(0, duration) for _ in range(3)])
        for i, time in enumerate(random_times):
            frame_path = os.path.join(frames_dir, f"frame_{i + 1}.png")
            command = f"ffmpeg -i \"{file_path}\" -ss {time} -vframes 1 -vf \"scale=150:150\" \"{frame_path}\""
            ffmpeg_output = run_command(command)
            if os.path.exists(frame_path):
                log_message(f"Extracted frame {i + 1} at {time:.2f}s to: {frame_path}")
            else:
                log_message(f"Failed to create frame {i + 1} at {time:.2f}s. FFmpeg output: {ffmpeg_output}")
    except ValueError:
        log_message(f"Failed to retrieve video duration. FFprobe output: {duration_output}")
        log_message("Random frame extraction skipped.")

    # Ensure persistent storage of PhotoImage objects
    frame_images = []  # List to store references to PhotoImage objects

    # Clear the frame labels and remove any existing labels from the UI
    for label in frame_labels:
        label.destroy()
    frame_labels.clear()

    # Recreate the frame labels
    for i in range(3):
        tab = notebook.nametowidget(notebook.tabs()[i])
        label = tk.Label(tab, text=f"Frame {i + 1}", width=200, height=200, bg="gray")
        label.place(x=0, y=0, anchor="nw")
        frame_labels.append(label)

    # Update the recreated labels with new preview images
    for i, label in enumerate(frame_labels):
        frame_path = os.path.join(frames_dir, f"frame_{i + 1}.png")
        if os.path.exists(frame_path):
            frame_image = tk.PhotoImage(file=frame_path)
            label.config(image=frame_image, width=150, height=150, bg="white")
            label.image = frame_image  # Keep a reference to avoid garbage collection
        else:
            label.config(image="", text=f"Frame {i + 1} (Not Found)", bg="gray")

def convert_video():
    """Convert video to a selected format."""
    file_path = selected_file.get()
    if not file_path:
        messagebox.showerror("Error", "No file selected.")
        return

    output_format = format_combobox.get()
    output_dir = os.path.abspath(os.path.join(os.getcwd(), "output"))  # Use the output folder
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"converted_video.{output_format}")

    command = f"ffmpeg -i \"{file_path}\" \"{output_file}\""
    threading.Thread(target=lambda: messagebox.showinfo("Conversion", run_command(command))).start()

def extract_audio():
    """Extract audio from the selected video."""
    file_path = selected_file.get()
    if not file_path:
        messagebox.showerror("Error", "No file selected.")
        return

    output_dir = os.path.abspath(os.path.join(os.getcwd(), "output"))  # Use the output folder
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "extracted_audio.mp3")

    command = f"ffmpeg -i \"{file_path}\" -q:a 0 -map a \"{output_file}\""
    threading.Thread(target=lambda: messagebox.showinfo("Audio Extraction", run_command(command))).start()

def extract_frames():
    """Extract frames from the selected video."""
    file_path = selected_file.get()
    if not file_path:
        messagebox.showerror("Error", "No file selected.")
        return

    output_dir = os.path.abspath(os.path.join(os.getcwd(), "output", "frames"))  # Use the output folder
    os.makedirs(output_dir, exist_ok=True)
    command = f"ffmpeg -i \"{file_path}\" \"{output_dir}/frame_%04d.png\""
    threading.Thread(target=lambda: messagebox.showinfo("Frame Extraction", run_command(command))).start()

# Move the download_video function definition above the button creation
def download_video():
    """Download a video using yt-dlp."""
    global ytdlp_process
    url = youtube_url.get()
    if not url:
        messagebox.showerror("Error", "No URL provided.")
        return

    downloads_dir = os.path.abspath(os.path.join(os.getcwd(), "downloads"))  # Use the downloads folder
    log_message(f"Downloads directory: {downloads_dir}")

    if os.path.exists(downloads_dir):
        log_message("Clearing existing files in the downloads directory.")
        for file in os.listdir(downloads_dir):
            file_path = os.path.join(downloads_dir, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)  # Remove the file
                    log_message(f"Deleted file: {file_path}")
            except Exception as e:
                log_message(f"Failed to delete {file_path}: {e}")
    else:
        os.makedirs(downloads_dir, exist_ok=True)
        log_message("Created downloads directory.")

    # Build the yt-dlp command
    selected_format = ytdlp_format.get()
    if selected_format:
        command = f"yt-dlp -f {selected_format} -o \"{downloads_dir}/%(title)s.%(ext)s\" \"{url}\""
    else:
        command = f"yt-dlp -o \"{downloads_dir}/%(title)s.%(ext)s\" \"{url}\""

    log_message(f"yt-dlp command: {command}")

    def download():
        global ytdlp_process
        log_message(f"Downloading video from URL: {url}")
        stop_button.config(state="normal")  # Enable the Stop button
        ytdlp_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        merged_file = None
        for line in ytdlp_process.stdout:
            log_message(line.strip())
            if "[Merger] Merging formats into" in line:
                # Extract the merged file path
                merged_file = line.split("into \"")[-1].split("\"")[0].strip()
                log_message(f"Merged file path: {merged_file}")
        for line in ytdlp_process.stderr:
            log_message(line.strip())
        ytdlp_process.wait()
        if ytdlp_process.returncode == 0:
            messagebox.showinfo("Download", "Download complete.")

            # Rename the merged file if it exists
            if merged_file and os.path.exists(merged_file):
                new_file_name = os.path.join(os.path.dirname(merged_file), "renamed_video.mp4")
                os.rename(merged_file, new_file_name)
                log_message(f"Renamed merged file to: {new_file_name}")

                # Set the renamed file as the current selected preview
                selected_file.set(new_file_name)
                update_preview(new_file_name)

    threading.Thread(target=download).start()

def stop_download():
    """Stop the yt-dlp download process."""
    global ytdlp_process
    if ytdlp_process and ytdlp_process.poll() is None:  # Check if the process is running
        ytdlp_process.terminate()  # Terminate the process
        log_message("Download process terminated.")
        stop_button.config(state="disabled")  # Disable the Stop button
    else:
        log_message("No active download process to stop.")

def play_selected_video():
    """Play the currently selected video."""
    file_path = selected_file.get()
    log_message(f"Attempting to play file: {file_path}")  # Log the file being played
    if not file_path:
        messagebox.showerror("Error", "No video selected.")
        return

    # Log the file path and add a fallback print statement
    try:
        log_message(f"Attempting to play file: {file_path}")
    except Exception as e:
        print(f"Logging failed: {e}")
        print(f"Attempting to play file: {file_path}")

    try:
        log_message("Initializing VLC for video playback.")

        # Create a new window for video playback
        playback_window = tk.Toplevel(root)
        playback_window.title("Video Playback")
        playback_window.geometry("640x480")

        # Create VLC instance and media player
        vlc_instance = vlc.Instance()
        log_message("VLC instance created.")

        media_player = vlc_instance.media_player_new()
        log_message("VLC media player created.")

        media = vlc_instance.media_new(file_path)
        log_message(f"Media loaded: {file_path}")

        media_player.set_media(media)
        log_message("Media set to media player.")

        # Embed the VLC player in the Tkinter window
        video_frame = tk.Frame(playback_window, width=640, height=480, bg="black")
        video_frame.pack(expand=True, fill="both")
        playback_window.update_idletasks()  # Ensure the window is fully rendered

        # Set the window handle for VLC
        if os.name == "nt":  # Windows
            media_player.set_hwnd(video_frame.winfo_id())
            log_message("VLC window handle set for Windows.")
        else:  # Unix-based systems
            media_player.set_xwindow(video_frame.winfo_id())
            log_message("VLC window handle set for Unix-based system.")

        # Play the video
        media_player.play()
        log_message("Video playback started.")

        # Stop the VLC player when the window is closed
        def on_close():
            media_player.stop()
            media_player.release()
            playback_window.destroy()
            log_message("Video playback stopped.")

        playback_window.protocol("WM_DELETE_WINDOW", on_close)

    except Exception as e:
        log_message(f"Error during video playback: {e}")
        messagebox.showerror("Playback Error", f"An error occurred: {e}")

# Initialize main window
root = tk.Tk()
root.title("Video Tool UI")
root.geometry("800x600")

# Variables
selected_file = tk.StringVar()
youtube_url = tk.StringVar()

# Ensure ytdlp_format is initialized after the root window is created
ytdlp_format = tk.StringVar(root)  # Associate with the root window
ytdlp_format.set("best")  # Default to "best"

# Layout
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

left_frame = tk.Frame(main_frame, width=400)
left_frame.pack(side=tk.LEFT, fill=tk.Y)

right_frame = tk.Frame(main_frame, width=400)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Left Frame Widgets
file_label = tk.Label(left_frame, text="Selected File:")
file_label.pack(anchor="w", padx=10, pady=5)

file_entry = tk.Entry(left_frame, textvariable=selected_file, width=40)
file_entry.pack(anchor="w", padx=10, pady=5)

browse_button = tk.Button(left_frame, text="Browse", command=browse_file)
browse_button.pack(anchor="w", padx=10, pady=5)

format_label = tk.Label(left_frame, text="Convert to Format:")
format_label.pack(anchor="w", padx=10, pady=5)

format_combobox = Combobox(left_frame, values=["mp4", "mkv", "avi", "mov", "webm"])
format_combobox.set("mp4")
format_combobox.pack(anchor="w", padx=10, pady=5)

convert_button = tk.Button(left_frame, text="Convert Video", command=convert_video)
convert_button.pack(anchor="w", padx=10, pady=5)

extract_audio_button = tk.Button(left_frame, text="Extract Audio", command=extract_audio)
extract_audio_button.pack(anchor="w", padx=10, pady=5)

extract_frames_button = tk.Button(left_frame, text="Extract Frames", command=extract_frames)
extract_frames_button.pack(anchor="w", padx=10, pady=5)

youtube_label = tk.Label(left_frame, text="YouTube URL:")
youtube_label.pack(anchor="w", padx=10, pady=5)

youtube_entry = tk.Entry(left_frame, textvariable=youtube_url, width=40)
youtube_entry.pack(anchor="w", padx=10, pady=5)

# Move the Query Formats button next to the Download button
download_frame = tk.Frame(left_frame)
download_frame.pack(anchor="w", padx=10, pady=5)

download_button = tk.Button(download_frame, text="Download Video", command=download_video)
download_button.pack(side="left", padx=5)

query_button = tk.Button(download_frame, text="Query Formats", command=query_formats)
query_button.pack(side="left", padx=5)

stop_button = tk.Button(download_frame, text="Stop Download", command=stop_download, state="disabled")
stop_button.pack(side="left", padx=5)

# Add a text field for specifying the format
ytdlp_format_field = tk.Entry(left_frame, textvariable=ytdlp_format, width=20)
ytdlp_format_field.pack(anchor="w", padx=10, pady=5)

# Right Frame Widgets
preview_label = tk.Label(right_frame, text="Preview: None", wraplength=300)
preview_label.pack(anchor="center", pady=20)

# Add a Play button for the video preview
play_button = tk.Button(right_frame, text="Play Video", state="disabled")
play_button.pack(anchor="center", pady=10)

# Add a button to recreate preview images
recreate_previews_button = tk.Button(right_frame, text="Recreate Previews", command=lambda: update_preview(selected_file.get()))
recreate_previews_button.pack(anchor="center", pady=10)

# Bind the play_selected_video function to the Play button
play_button.config(command=play_selected_video)

# Create a Notebook widget for tabs
notebook = ttk.Notebook(right_frame)
notebook.pack(fill="both", expand=True, padx=10, pady=10)

# Create three tabs for preview images
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)
tab3 = ttk.Frame(notebook)
notebook.add(tab1, text="Preview 1")
notebook.add(tab2, text="Preview 2")
notebook.add(tab3, text="Preview 3")

# Add preview images to each tab
frame_labels = []
for i, tab in enumerate([tab1, tab2, tab3]):
    label = tk.Label(tab, text=f"Frame {i + 1}", width=200, height=200, bg="gray")
    label.place(x=0, y=0, anchor="nw")  # Place at the top-left corner of the tab
    frame_labels.append(label)

# Set the preview image size to 10 pixels until preview frames are downloaded
for i in range(3):
    frame_labels[i].config(width=10, height=10)

# Reintroduce the log window at the bottom of the UI
log_text = tk.Text(root, height=10, state="disabled")
log_text.pack(side=tk.BOTTOM, fill=tk.X)

# Update the log_message function to also write logs to a file
log_file_path = os.path.join(os.getcwd(), "video_tool.log")

def log_message(message):
    """Log a message to the log window and a log file."""
    log_text.config(state="normal")
    log_text.insert(tk.END, message + "\n")
    log_text.config(state="disabled")
    log_text.see(tk.END)

    # Write the log message to a file
    try:
        with open(log_file_path, "a", encoding="utf-8") as log_file:
            log_file.write(message + "\n")
    except Exception as e:
        print(f"Failed to write to log file: {e}")

# Run the application
root.mainloop()