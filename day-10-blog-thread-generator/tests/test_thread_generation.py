from src.segment import Segment
from src.thread_generator import generate_variant_1


def make_segment(
    id,
    text,
    parent=None,
):
    return Segment(
        id=id,
        type="paragraph",
        level=None,
        text=text,
        source_order=id,
        parent_heading_id=parent,
        char_count=len(text),
    )


def test_basic_sequential_packing():
    segments = [
        make_segment(1, "First"),
        make_segment(2, "Second"),
    ]

    variant = generate_variant_1(segments, max_chars=20)
    assert len(variant.posts) == 1
    assert variant.posts[0].text == "First Second"


def test_heading_boundary_flush():
    segments = [
        make_segment(1, "A", parent=1),
        make_segment(2, "B", parent=2),
    ]

    variant = generate_variant_1(segments, max_chars=10)
    assert len(variant.posts) == 2


def test_forced_split_warning():
    long_text = "A" * 50
    segments = [make_segment(1, long_text)]

    variant = generate_variant_1(segments, max_chars=20)
    assert variant.warnings
    assert len(variant.posts) >= 3
