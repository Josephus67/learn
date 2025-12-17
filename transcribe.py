import os
import sys
import yt_dlp
from faster_whisper import WhisperModel
import re
import shutil

def sanitize_filename(name):
    """Sanitize the filename to remove illegal characters."""
    return re.sub(r'[\\/*?:"<>|]', "", name)

def download_audio(youtube_url, output_dir="."):
    """Downloads audio from YouTube URL and converts to WAV."""
    print(f"⬇️  Downloading audio from {youtube_url}...")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            filename = ydl.prepare_filename(info)
            # The file extension changes after post-processing to .wav
            base, _ = os.path.splitext(filename)
            final_filename = base + ".wav"
            return final_filename, info.get('title', 'transcription')
    except Exception as e:
        print(f"❌ Error downloading video: {e}")
        return None, None

def transcribe_audio(audio_path, model_name="base"):
    """Transcribes the audio file using Faster Whisper."""
    print(f"🎧 Loading Faster Whisper model ({model_name})...")
    try:
        # Use 'auto' to let faster-whisper choose the best available device
        # On macOS, it will likely default to CPU as MPS is not fully supported by ctranslate2 yet
        device = "cpu"
        compute_type = "int8"
            
        print(f"🚀 Using device: {device} ({compute_type})")
        
        model = WhisperModel(model_name, device=device, compute_type=compute_type)
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None

    print(f"📝 Transcribing '{audio_path}'...")
    try:
        segments, info = model.transcribe(audio_path, beam_size=5)
        
        print(f"Detected language '{info.language}' with probability {info.language_probability:.2f}")
        
        text_segments = []
        for segment in segments:
            text_segments.append(segment.text)
            
        return " ".join(text_segments).strip()
    except Exception as e:
        print(f"❌ Error during transcription: {e}")
        return None

def save_transcription(text, title, output_dir="."):
    """Saves the transcription text to a file."""
    safe_title = sanitize_filename(title)
    output_path = os.path.join(output_dir, f"{safe_title}.txt")
    
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text.strip())
        print(f"✅ Transcription saved to: {output_path}")
        return output_path
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        return None

def main():
    print("--- YouTube Audio Transcriber ---")

    # Check for ffmpeg
    if not shutil.which("ffmpeg"):
        print("❌ Error: 'ffmpeg' is not installed or not in PATH.")
        print("👉 Please install it using: brew install ffmpeg")
        return
    
    # Get URL from user
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("🔗 Enter YouTube URL: ").strip()
    
    if not url:
        print("❌ No URL provided.")
        return

    # Ensure output directory exists
    output_dir = "downloads"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. Download
    audio_file, title = download_audio(url, output_dir)
    if not audio_file:
        return

    # 2. Transcribe
    # Using 'medium' model as per your previous script preference, 
    # but you can change to 'base' or 'small' for speed.
    transcription = transcribe_audio(audio_file, model_name="medium")
    
    if transcription:
        # 3. Save
        save_transcription(transcription, title, output_dir)
        
        # Optional: Cleanup audio file
        # os.remove(audio_file)
        # print(f"🗑️  Deleted temporary audio file: {audio_file}")
    
    print("\n🎉 Done!")

if __name__ == "__main__":
    main()
