# Video Tool

## Overview
The Video Tool is a Python-based application designed to simplify video processing tasks. It provides a graphical user interface (GUI) for downloading videos, playing them, extracting frames, and converting formats.

## Features
- **Video Download**: Download videos from YouTube using `yt-dlp`.
- **Video Playback**: Play selected videos using VLC.
- **Frame Extraction**: Extract preview frames from videos at random positions.
- **Format Conversion**: Convert videos to different formats.
- **Preview Recreation**: Dynamically recreate preview images for selected videos.

## Requirements
- Python 3.10
- `yt-dlp`
- `python-vlc`
- `ffmpeg`
- `tkinter`

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/portland-games/Theatre-tools.git
   ```
2. Navigate to the `video-tools` directory:
   ```bash
   cd Theatre-tools/video-tools
   ```
3. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   source .venv/bin/activate  # On macOS/Linux
   ```
4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Run the application:
   ```bash
   python video_tool_ui.py
   ```
2. Use the GUI to:
   - Browse and select videos.
   - Download videos by providing a YouTube URL.
   - Play selected videos.
   - Extract frames and recreate previews.
   - Convert videos to different formats.

## Notes
- Ensure `ffmpeg` is installed and added to your system's PATH.
- The application creates an `output` directory for storing extracted frames and converted videos.

## Troubleshooting
- If the "Play Video" button does not work, ensure VLC is installed and accessible.
- For frame extraction issues, verify that `ffmpeg` is correctly installed.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing
Contributions are welcome! Feel free to open issues or submit pull requests to improve the tool.