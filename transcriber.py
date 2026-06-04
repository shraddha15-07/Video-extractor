import yt_dlp
import json
import os
import urllib.request

def transcribe_audio(audio_path="audio.mp3"):
    return []

def transcribe_youtube(url):
    print("Fetching transcript from YouTube...")
    
    ydl_opts = {
        'skip_download': True,
        'writeautomaticsub': True,
        'writesubtitles': True,
        'subtitlesformat': 'json3',
        'subtitleslangs': ['en'],
        'outtmpl': 'transcript_raw',
        'quiet': True,
    }
    
    segments = []
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        captions = info.get('subtitles', {}).get('en') or \
                   info.get('automatic_captions', {}).get('en', [])
        
        for fmt in captions:
            if fmt.get('ext') == 'json3':
                with urllib.request.urlopen(fmt['url']) as response:
                    data = json.loads(response.read().decode())
                    
                    for event in data.get('events', []):
                        if 'segs' in event:
                            text = ''.join(seg.get('utf8', '') for seg in event['segs']).strip()
                            if text and text != '\n':
                                segments.append({
                                    'start': round(event.get('tStartMs', 0) / 1000, 2),
                                    'end': round((event.get('tStartMs', 0) + event.get('dDurationMs', 0)) / 1000, 2),
                                    'text': text
                                })
                break
    
    if segments:
        with open("transcript.json", "w") as f:
            json.dump(segments, f, indent=2)
        print(f"Got {len(segments)} segments instantly!")
        return segments
    
    print("No captions found!")
    return []

if __name__ == "__main__":
    segs = transcribe_youtube("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    print(f"Got {len(segs)} segments")