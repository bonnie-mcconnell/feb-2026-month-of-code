from dataclasses import dataclass
from typing import List, Optional, Tuple
import re
import os

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    YouTubeTranscriptApi = None


@dataclass
class TranscriptLine:
    index: int
    text: str
    start_sec: Optional[int] = None
    end_sec: Optional[int] = None
    speaker: Optional[str] = None



_TIMESTAMP_PATTERN = re.compile(r"^\[(\d{2}):(\d{2}):(\d{2})\]\s*(.*)$")


def load_transcript(source: str) -> Tuple[List[TranscriptLine], bool]:
    """
    Load a transcript from a YouTube URL or a local text file.

    Returns:
        (lines, has_timestamps)

    Raises:
        ValueError on unsupported input or empty transcript.
    """
    if source.startswith("http"):
        return _load_from_youtube(source)
    else:
        return _load_from_file(source)


def _load_from_file(path: str) -> Tuple[List[TranscriptLine], bool]:
    if not os.path.exists(path):
        raise ValueError(f"Transcript file not found: {path}")

    lines: List[TranscriptLine] = []
    has_timestamps = False

    with open(path, "r", encoding="utf-8") as f:
        raw_lines = [line.strip() for line in f if line.strip()]

    if not raw_lines:
        raise ValueError("Transcript file is empty.")

    for idx, raw in enumerate(raw_lines):
        match = _TIMESTAMP_PATTERN.match(raw)
        if match:
            has_timestamps = True
            hours, minutes, seconds, text = match.groups()
            start_sec = (
                int(hours) * 3600
                + int(minutes) * 60
                + int(seconds)
            )
            lines.append(
                TranscriptLine(
                    index=idx,
                    text=text,
                    start_sec=start_sec,
                )
            )
        else:
            lines.append(
                TranscriptLine(
                    index=idx,
                    text=raw,
                )
            )

    return lines, has_timestamps


def _load_from_youtube(url: str) -> Tuple[List[TranscriptLine], bool]:
    if YouTubeTranscriptApi is None:
        raise ValueError(
            "youtube-transcript-api is not installed. "
            "Install it to enable YouTube transcript loading."
        )

    video_id = _extract_video_id(url)
    if not video_id:
        raise ValueError("Could not extract video ID from URL.")

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id) # type: ignore[attr-defined]
    except Exception as e:
        raise ValueError(f"Failed to fetch transcript: {e}")

    if not transcript:
        raise ValueError("No transcript available for this video.")

    lines: List[TranscriptLine] = []

    for idx, entry in enumerate(transcript):
        lines.append(
            TranscriptLine(
                index=idx,
                text=entry.get("text", "").strip(),
                start_sec=int(entry.get("start", 0)),
                end_sec=int(entry.get("start", 0) + entry.get("duration", 0)),
            )
        )

    return lines, True


def _extract_video_id(url: str) -> Optional[str]:
    """
    Extract YouTube video ID from common URL formats.
    """
    patterns = [
        r"v=([a-zA-Z0-9_-]{11})",
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None
