# YouTube Audio Transcriber

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/YOUR_USERNAME/YOUR_REPO_NAME)

This tool downloads audio from a YouTube video and transcribes it to a text file using the `faster-whisper` AI model.

## Why Codespaces?

This project requires `ffmpeg` and specific Python libraries that can be tricky to install on some local machines (especially older macOS versions). Running this in GitHub Codespaces provides a pre-configured Linux environment where everything just works.

## Prerequisites

1.  **FFmpeg**: This is required for audio processing.
    *   **Codespaces**: Installed automatically!
    *   **macOS**: Install via Homebrew: `brew install ffmpeg`
    *   **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.
    *   **Linux**: `sudo apt install ffmpeg`

## Setup

### Option A: GitHub Codespaces (Recommended)

1.  Push this folder to a GitHub repository.
2.  Click the "Code" button on your repository page.
3.  Select the "Codespaces" tab and click "Create codespace on main".
4.  Wait for the environment to build. It will automatically install `ffmpeg` and all Python dependencies.

### Option B: Local Setup

1.  Navigate to the project directory:
    ```bash
    cd youtube_transcribe
    ```

2.  Create and activate a virtual environment (already done if you followed the assistant):
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the script:

```bash
python transcribe.py
```

Or provide the URL directly:

```bash
python transcribe.py "https://www.youtube.com/watch?v=..."
```

The transcription will be saved as a `.txt` file in the `downloads` folder.
