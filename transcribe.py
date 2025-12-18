import os
import sys
from pytubefix import YouTube
from faster_whisper import WhisperModel
import re
import shutil

def sanitize_filename(name):
    """Sanitize the filename to remove illegal characters."""
    return re.sub(r'[\\/*?:"<>|]', "", name)

def download_audio(youtube_url, output_dir="."):
    """Downloads audio from YouTube URL using pytubefix."""
    print(f"⬇️  Downloading audio from {youtube_url}...")
    
    try:
        # Try to use oauth
        # use_oauth=True: triggers the OAuth flow if needed
        # allow_oauth_cache=True: caches the token for future uses
        yt = YouTube(youtube_url, use_oauth=True, allow_oauth_cache=True)
        
        def on_progress(stream, chunk, bytes_remaining):
            # Optional: print progress
            pass
            
        yt.register_on_progress_callback(on_progress)

        print(f"ℹ️  Fetching video info for: {youtube_url}")
        # Accessing streams triggers the auth flow if needed
        # Get the highest quality audio stream
        audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
        
        if not audio_stream:
            print("❌ Error: No audio stream found.")
            return None, None

        print(f"✅ Found audio stream: {audio_stream}")
        # Download
        out_file = audio_stream.download(output_path=output_dir)
        print(f"✅ Download complete: {out_file}")
        
        return out_file, yt.title
    except Exception as e:
        print(f"❌ Error downloading video: {e}")
        if "428" in str(e) or "Precondition Required" in str(e):
             print("\n⚠️  Authentication required! Please run the script in an interactive terminal and follow the instructions to sign in.")
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
    # Using 'base' model for speed. Change to 'medium' or 'large' for better accuracy.
    transcription = transcribe_audio(audio_file, model_name="base")
    
    if transcription:
        # 3. Save
        save_transcription(transcription, title, output_dir)
        
        # Optional: Cleanup audio file
        # os.remove(audio_file)
        # print(f"🗑️  Deleted temporary audio file: {audio_file}")
    
    print("\n🎉 Done!")

if __name__ == "__main__":
    main()
