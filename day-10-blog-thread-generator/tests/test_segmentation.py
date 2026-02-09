from src.segment import segment_text


def test_heading_detection():
    text = "# Title\n\nParagraph text."
    segments = segment_text(text)

    assert segments[0].type == "heading"
    assert segments[0].text == "Title"
    assert segments[1].type == "paragraph"


def test_paragraph_grouping():
    text = "Line one\nLine two\n\nLine three"
    segments = segment_text(text)

    assert len(segments) == 2
    assert segments[0].text == "Line one Line two"
    assert segments[1].text == "Line three"


def test_list_items_are_atomic():
    text = "- Item one\n- Item two"
    segments = segment_text(text)

    assert len(segments) == 2
    assert segments[0].type == "list_item"
    assert segments[1].type == "list_item"


def test_parent_heading_assignment():
    text = "# Section\n- Item\nParagraph"
    segments = segment_text(text)

    heading_id = segments[0].id
    assert segments[1].parent_heading_id == heading_id
    assert segments[2].parent_heading_id == heading_id


def test_source_order_is_sequential():
    text = "# A\nPara\n- Item"
    segments = segment_text(text)

    orders = [s.source_order for s in segments]
    assert orders == sorted(orders)
