import yt_dlp
import os

def download_audio(url, output_path="audio.mp3"):
    
    if os.path.exists(output_path):
        os.remove(output_path)
    if os.path.exists("audio"):
        os.remove("audio")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path.replace('.mp3', ''),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ffmpeg_location': 'C:\\ffmpeg\\bin',
        'quiet': False,
    }

    print(f"Downloading audio from: {url}")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    print(f"Audio saved as {output_path}")
    return output_path

if __name__ == "__main__":
    download_audio("https://www.youtube.com/watch?v=dQw4w9WgXcQ")   