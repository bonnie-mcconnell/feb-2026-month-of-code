# Stock News Sentiment Tracker (Rule-Based)

A deterministic, rule-based system for scoring and aggregating stock-related news headlines.

This project is designed as a backend data component - not a trading system, not a prediction engine, and not a machine learning model.

It provides transparent sentiment scoring and daily aggregation suitable for research pipelines or monitoring systems.


## Problem Framing

Financial news sentiment is often used in research and monitoring contexts, but it is frequently implemented using opaque or overcomplicated models.

This project intentionally avoids that.

Instead of attempting to "predict markets", it:

- Scores headlines using a transparent keyword heuristic
- Aggregates tone per ticker per day
- Produces structured, auditable summaries

The goal is signal inspection rather than alpha generation.


## Why Rule-Based?

Rule-based sentiment is:

- Deterministic
- Easy to audit
- Easy to test
- Stable across time

In financial contexts, explainability matters.

Given a headline, you can inspect the lexicon and understand exactly why it was scored positive or negative.

No hidden weights. No probabilistic output. No training data.


## What This Is Not

This project does not:

- Predict stock prices
- Estimate probabilities
- Claim trading edge
- Model market reactions
- Perform backtesting

Headline tone does not directly translate into price movement.

Market behavior depends on expectations, positioning, macro context, and many non-textual factors.

This tool simply measures lexical tone density.


## Design Overview

Pipeline:

1. Load JSON or CSV news records
2. Normalize and tokenize headlines
3. Apply keyword-based scoring
4. Aggregate per ticker per calendar day
5. Output structured summaries

Architecture is intentionally modular:

- `loader.py` – strict input parsing and validation
- `tokenizer.py` – deterministic text normalization
- `scorer.py` – rule-based sentiment scoring
- `aggregator.py` – daily aggregation logic
- `engine.py` – orchestration layer
- `cli.py` – thin command interface


## Scoring Logic

Each headline is tokenized and matched against small, domain-focused lexicons.

Example positive terms:

- strong
- growth
- beat
- profit
- upgrade

Example negative terms:

- loss
- decline
- miss
- lawsuit
- downgrade

Score is the sum of matched token weights.

Classification:

- score > 0 → positive
- score < 0 → negative
- score == 0 → neutral

No context modeling. No negation handling. No phrase detection.


## Aggregation Logic

Headlines are grouped by:

- Ticker
- Calendar date (YYYY-MM-DD)

For each group:

- Average sentiment score
- Volume (headline count)
- Positive ratio
- Negative ratio

This provides a simple daily tone summary per ticker.


## Example Usage

Run full aggregation:
```bash
python -m src.cli run data/sample_news.json
```

Get summary per ticker:
```bash
python -m src.cli summary data/sample_news.json
```

Report on specific ticker:
```bash
python -m src.cli report data/sample_news.json --ticker AAPL
```

## Example Output

See `examples/sample_output.json`.

## Limitations

- No contextual understanding
- No negation handling
- No sarcasm detection
- No phrase-level semantics
- No weighting by source credibility
- No time-of-day modeling

This is a lexical heuristic not a language model.
It is suited for deterministic signal enrichment, not decision automation.

## Potential Future Extensions

- Weighted keywords
- Rolling multi-day averages
- Source-level aggregation
- CSV export

Any extension should preserve transparency and determinism.

## License

For educational and research purposes.
