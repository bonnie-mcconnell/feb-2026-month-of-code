# Blog → Social Thread Generator

A deterministic command-line tool for restructuring long-form blog content into deterministic, character-bounded social media thread posts.

This project focuses on content structuring, not creative rewriting. It preserves meaning, enforces character limits, and makes every transformation explicit and inspectable.

---

## Why This Exists

Teams often need to repurpose existing blog content into social threads quickly and reliably.

Manual restructuring is:
- Time-consuming
- Inconsistent
- Error-prone when character limits are involved

This tool provides a technical solution for **deterministic content segmentation and packing** without inventing or embellishing text.

---

## What This Tool Does

- Accepts a blog post as plain text or Markdown
- Normalizes and preprocesses content
- Segments content into logical units (headings, paragraphs, lists)
- Packs segments into thread posts under a strict character limit
- Preserves traceability from blog segments to thread posts
- Emits human-readable text or structured JSON
- Markdown support is structural only (headings, paragraphs, lists); inline formatting is preserved as raw text.

---

## What This Tool Explicitly Does Not Do

- Rewrite or paraphrase content creatively
- Optimize tone, engagement, or “virality”
- Generate new ideas or filler text
- Post to social platforms
- Predict engagement or performance

This is a **content structuring tool**, not a writing assistant.

---

## How Content Is Segmented

Input content is parsed into ordered `Segment` objects representing:
- Headings
- Paragraphs
- List items

Each segment retains:
- A stable ID
- Its original text
- Character count
- Optional parent heading relationship
- A deterministic position in the original document order

Segmentation favors readability and traceability over aggressive compression.

---

## Thread Generation Logic (Variant 1)

Variant 1 implements a conservative, sequential strategy:

- Segments are packed in original order
- Posts respect a strict `max_chars` limit
- Segments under the same heading are packed sequentially when space allows
- Oversized segments are split at sentence boundaries
- Hard splits are used only as a last resort

All decisions are deterministic and reproducible.

Warnings are recorded when:
- A segment exceeds the character limit
- A sentence requires a hard split


## Thread Generation Variants

### Variant 1: Conservative Sequential
Packs segments strictly in original document order with minimal restructuring.
This variant prioritizes traceability, predictability, and auditability.

### Variant 2: Heading-First Emphasis
Biases packing toward leading headings and their immediately associated content.
This variant produces more top-heavy threads while remaining deterministic.

Both variants:
- Operate on the same segmented input
- Respect the same character limits
- Produce fully inspectable output

---

## Output Formats

### Text (default)
```text
Thread Variant: Variant 1: Conservative Sequential

1/5
First post text...

2/5
Second post text...
```

### JSON

JSON output is designed for programmatic consumption and uses stable top-level variant keys ("Variant 1", "Variant 2", etc.). JSON output is emitted as a single line to ensure pipe safety and compatibility with CLI tooling.

```json
{
  "Variant 1": {
    "name": "Variant 1: Conservative Sequential",
    "count": 5,
    "warnings": [],
    "posts": [
      {
        "index": 1,
        "char_count": 243,
        "segment_ids": [1, 2],
        "text": "..."
      }
    ]
  }
}
```

### Usage

The CLI accepts a single input file and produces one or more thread variants deterministically.

```bash
python -m src.cli examples/sample_blog.md
```

Custom character limit:
```bash
python -m src.cli examples/sample_blog.md --max-chars 240
```

JSON output:
```bash
python -m src.cli examples/sample_blog.md --json
```

Write to file:
```bash
python -m src.cli examples/sample_blog.md --out thread.txt
```

Generate multiple variants in one run:
```bash
python -m src.cli examples/sample_blog.md --variant 1,2
```

Write multiple variants to separate files:
```bash
python -m src.cli examples/sample_blog.md --variant 1,2 --out thread.txt
# Produces:
# thread_variant1.txt
# thread_variant2.txt
```

## Known Limitations

- Sentence splitting is conservative and punctuation-based
- Deeply nested lists are flattened
- No semantic reordering or summarization is performed
- Hard splits may produce very short trailing posts when no safe boundary exists
- Variant 2 uses a simpler heuristic and is intentionally less conservative than Variant 1
- Input files must be UTF-8 encoded 


These trade-offs are intentional to preserve determinism and auditability.

## Extending This Tool

Production systems could add:
- Additional thread variants
- Section prioritization rules
- Platform-specific character limits
- Rich preview rendering
- Integration tests for CLI behavior

The current architecture is designed to support these without refactoring.
