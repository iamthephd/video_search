import re
from typing import List, Dict
from youtube_transcript_api import YouTubeTranscriptApi



def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from URL."""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/)([^&\n?]*)',
        r'(?:youtube\.com/embed/)([^&\n?]*)'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    raise ValueError("Invalid YouTube URL")


def get_transcript(video_id: str) -> List[Dict]:
    """Get transcript for a YouTube video."""
    try:
        return YouTubeTranscriptApi.get_transcript(video_id)
    except Exception as e:
        raise Exception(f"Failed to get transcript: {str(e)}")
    

def format_time(seconds: float) -> str:
    """Convert seconds to HH:MM:SS format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"