# Transcript Action Summary CLI

A deterministic command-line tool for extracting key ideas and action items from spoken transcripts (videos, talks, lectures, meetings).

This tool extracts explicit statements from transcripts for review and analysis. It does not perform summarization, inference, or paraphrasing.

## What this tool does

Loads transcripts from:
- YouTube URLs
- Local text files

YouTube transcript loading relies on the `youtube-transcript-api` package and only works when captions are available.


Segments transcripts into fixed analysis windows
Extracts:
- Key ideas (declarative, explanatory statements)
- Action items (explicit, listener-directed steps)

Outputs results as:
- Human-readable text
- Structured JSON for downstream processing

Output is fully deterministic: the same input always produces the same output.

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

Key ideas are NOT:
- reminders
- transitional phrases
- agenda statements
- calls to action


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
### JSON (--format json)
```json
{
  "source": "example.txt",
  "segments": 4,
  "key_ideas": [
    {
      "text": "...",
      "confidence": "high",
      "score": 0.95
    }
  ],
  "action_items": [
    {
      "segment_id": 1,
      "start_sec": 320,
      "text": "..."
    }
  ]
}
```
Note: score is rounded to 2 decimals for readability.

### Markdown (--format md)

```markdown
# Transcript Summary
**Source:** example.txt

## Key Ideas
- 🔴 **High** — Dependency inversion reduces coupling between components

## Action Items
- Refactor the logging layer (320s)
```

## Usage
#### Local transcript (text output, default)
```bash
python -m src.cli examples/sample_transcript.txt
```
#### Local transcript (JSON output, machine-readable)
```bash
python -m src.cli examples/sample_transcript.txt --format json --out out.json
```
#### Local transcript (Markdown output)
```bash
python -m src.cli examples/sample_transcript.txt --format md --out out.md
```

#### Include per-segment breakdown
```bash
python -m src.cli examples/sample_transcript.txt --format text --segments
```

#### YouTube transcript
```bash
python -m src.cli https://www.youtube.com/watch?v=VIDEO_ID --format json --out out.json
```

### Optional/advanced

Include --segments example with JSON output if you want to show downstream pipeline usage:
```bash
python -m src.cli examples/sample_transcript.txt --format json --segments --out ou
```

#### Running tests
```bash
pytest
```

Golden-file tests ensure output stability.

### Windows note

Use the --out flag for machine-readable output (JSON or Markdown). This avoids BOM issues and ensures consistent UTF-8 encoding:
```powershell
python -m src.cli examples/sample_transcript.txt --format json --out out.json
python -m src.cli examples/sample_transcript.txt --format md --out out.md
``` 

Direct piping (| Out-File) is no longer necessary.

## Known limitations

- No sentence boundary detection
- No speaker attribution
- English-centric heuristics
- Conservative extraction (some ideas may be missed)
- JSON and Markdown outputs preserve Unicode characters and emojis.

## Failure modes

- Very informal speech
- Highly implicit instructions
- Non-instructional content