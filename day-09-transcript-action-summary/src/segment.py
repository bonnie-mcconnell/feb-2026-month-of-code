from dataclasses import dataclass
from typing import List, Optional

from src.transcript_loader import TranscriptLine


@dataclass
class Segment:
    segment_id: int
    lines: List[TranscriptLine]
    start_sec: Optional[int] = None
    end_sec: Optional[int] = None


TIME_WINDOW_SEC = 90
LINE_WINDOW_SIZE = 20


def segment_transcript(
    transcript_lines: List[TranscriptLine],
    has_timestamps: bool,
) -> List[Segment]:
    """
    Segment transcript lines into fixed analysis windows.

    Time-based segmentation is used when timestamps are available.
    Otherwise, line-count-based segmentation is used.
    """
    if not transcript_lines:
        return []

    if has_timestamps:
        return _segment_by_time(transcript_lines)

    return _segment_by_line_count(transcript_lines)


def _segment_by_time(lines: List[TranscriptLine]) -> List[Segment]:
    segments: List[Segment] = []

    current_lines: List[TranscriptLine] = []
    window_start: Optional[int] = None
    segment_id = 1

    for line in lines:
        if line.start_sec is None:
            continue  # timestamped mode expects timestamps

        if window_start is None:
            window_start = line.start_sec

        if line.start_sec - window_start <= TIME_WINDOW_SEC:
            current_lines.append(line)
        else:
            segments.append(
                Segment(
                    segment_id=segment_id,
                    lines=current_lines,
                    start_sec=window_start,
                    end_sec=current_lines[-1].start_sec,
                )
            )
            segment_id += 1
            current_lines = [line]
            window_start = line.start_sec

    if current_lines:
        segments.append(
            Segment(
                segment_id=segment_id,
                lines=current_lines,
                start_sec=window_start,
                end_sec=current_lines[-1].start_sec,
            )
        )

    return segments


def _segment_by_line_count(lines: List[TranscriptLine]) -> List[Segment]:
    segments: List[Segment] = []
    segment_id = 1

    for i in range(0, len(lines), LINE_WINDOW_SIZE):
        chunk = lines[i : i + LINE_WINDOW_SIZE]
        segments.append(
            Segment(
                segment_id=segment_id,
                lines=chunk,
            )
        )
        segment_id += 1

    return segments
