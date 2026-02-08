from src.segment import segment_transcript, TIME_WINDOW_SEC, LINE_WINDOW_SIZE
from src.transcript_loader import TranscriptLine


def test_time_based_segmentation():
    lines = [
        TranscriptLine(index=0, text="a", start_sec=0),
        TranscriptLine(index=1, text="b", start_sec=30),
        TranscriptLine(index=2, text="c", start_sec=60),
        TranscriptLine(index=3, text="d", start_sec=120),
    ]

    segments = segment_transcript(lines, has_timestamps=True)

    assert len(segments) == 2
    assert segments[0].segment_id == 1
    assert segments[1].segment_id == 2
    assert segments[0].start_sec == 0
    assert segments[0].end_sec == 60
    assert segments[1].start_sec == 120


def test_line_count_segmentation():
    lines = [
        TranscriptLine(index=i, text=f"line {i}")
        for i in range(LINE_WINDOW_SIZE + 5)
    ]

    segments = segment_transcript(lines, has_timestamps=False)

    assert len(segments) == 2
    assert len(segments[0].lines) == LINE_WINDOW_SIZE
    assert len(segments[1].lines) == 5


def test_empty_transcript():
    segments = segment_transcript([], has_timestamps=False)
    assert segments == []
