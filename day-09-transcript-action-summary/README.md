# Transcript Action Summary CLI

A deterministic command-line tool for extracting key ideas and action items from spoken transcripts (videos, talks, lectures, meetings).

This tool is designed for analysis and review, not summarization or “understanding”.

## What this tool does

Loads transcripts from:
- YouTube URLs
- Local text files

Segments transcripts into fixed analysis windows
Extracts:
- Key ideas (declarative, explanatory statements)
- Action items (explicit, listener-directed steps)

Outputs results as:
- Human-readable text
- Structured JSON for downstream processing

## What this tool does not do
- No LLMs
- No semantic inference
- No paraphrasing
- No hallucinated conclusions
- No automatic task management

All output is directly grounded in transcript text.

## When this works well

- Technical talks
- Tutorials
- Internal demos
- Lectures
- Meetings with clear instructions

## How the analysis works
1. Transcript loading

transcript_loader.py

- Accepts YouTube URLs or local files
- Detects timestamps automatically
- Produces normalized TranscriptLine objects

2. Preprocessing

preprocess.py

- Normalizes whitespace
- Drops empty lines
- Performs no semantic rewriting

This stage exists to keep the pipeline explicit and auditable.

3. Segmentation

segment.py

- Timestamped transcripts → time windows (default: 90s)
- Untimestamped transcripts → line windows (default: 20 lines)
- Produces deterministic Segment objects

4. Key idea extraction

extract.py

Key ideas are:
- Declarative
- Explanatory
- Standalone statements

Each idea is labeled:
- high confidence (explicit declarative markers)
- medium confidence (generalizations / explanations)

False negatives are preferred over false positives.

5. Action item extraction

extract.py

Action items must:
- Address the listener directly
- Contain explicit action verbs
- Appear as concrete instructions

Each item includes:
- Segment ID
- Timestamp (when available)

## Output formats
### Text (default)
```text
KEY IDEAS
---------
[HIGH] Dependency inversion reduces coupling between components

ACTION ITEMS
------------
- Refactor the logging layer @ 320s
```
### JSON (--json)
```json
{
  "source": "example.txt",
  "segments": 4,
  "key_ideas": [...],
  "action_items": [...]
}
```

## Usage
### Local transcript
```bash
python -m src.cli examples/sample_transcript.txt
```

### YouTube video
```bash
python -m src.cli https://www.youtube.com/watch?v=VIDEO_ID
```

### JSON output
```bash
python -m src.cli examples/sample_transcript.txt --json
```

### Running tests
```bash
pytest
```

Golden-file tests ensure output stability.

## Known limitations

- No sentence boundary detection
- No speaker attribution
- English-centric heuristics
- Conservative extraction (some ideas may be missed)

## Failure modes

- Very informal speech
- Highly implicit instructions
- Non-instructional content