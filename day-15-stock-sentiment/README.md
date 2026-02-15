# Stock News Sentiment Tracker (Rule-Based)

A deterministic, rule-based system for scoring and aggregating stock-related news headlines.

This project is designed as a backend data component - not a trading system, not a prediction engine, and not a machine learning model.

It provides:
- Transparent lexical sentiment scoring
- Persistent storage in SQLite
- Daily aggregation per ticker
- Sector-weighted sentiment adjustment
- Rolling averages
- Volatility, momentum, and z-score metrics
- CLI-driven reporting

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

Each headline's score can be inspected directly; no hidden weights or probabilistic outputs.


## What This Is Not

This project does not:

- Predict stock prices
- Estimate probabilities
- Claim trading edge
- Model market reactions
- Perform backtesting

Headline tone does not directly translate into price movement. Market behavior depends on expectations, positioning, macro context, and many non-textual factors.

This tool simply measures lexical tone density.


## System Architecture

The system is modular and stateful.

### Core Components

- loader.py
  Strict JSON/CSV input parsing and validation.
- ingest.py
  Handles ingestion of raw news records into the repository layer.
- repository.py
  Database abstraction layer over SQLite.
  Responsible for:
  - Creating tables
  - Inserting raw news
  - Inserting scored news
  - Fetching scored news
  - Fetching daily aggregates
- db.py
  Database connection handling. Database schema is stable and versioned implicitly through repository layer.
- scorer.py
  Deterministic keyword-based headline scoring.
- sector.py
  Loads sector/ticker weight configuration used during aggregation.
- aggregator.py
  Groups scored headlines by ticker and date and computes:
  - Sector-weighted average sentiment
  - Volume
  - Positive ratio
  - Negative ratio
- engine.py
  Orchestrates:
  load → score → persist → aggregate
- cli.py
  Thin command interface exposing ingestion, aggregation, summary, and reporting.

## Data Flow
1. Ingest
Raw news records are inserted into SQLite via Repository.

2. Score
Headlines are scored deterministically using keyword heuristics.

3. Persist
Scored results are stored in the database.

4. Aggregate
All scored records are grouped by:
- Ticker
- Calendar date (YYYY-MM-DD)

5. Report

CLI generates analytical summaries using aggregated daily data.

## Sentiment Scoring

Scoring is fully rule-based.

Each headline:
- Is tokenized
- Matched against positive and negative keyword lexicons
- Assigned a numeric score

Classification:
- score > 0 → positive
- score < 0 → negative
- score = 0 → neutral

No ML, embeddings, probabilistic outputs, contextual modeling, negation handling. Completely deterministic.

## Sector Weighting

During aggregation, average daily sentiment is multiplied by a configurable sector weight:
```bash
avg_score = (sum(scores) / volume) * sector_weight
```

Weights are loaded from configuration via sector.py.

If a ticker has no configured weight, default = 1.0.

This allows controlled cross-sector normalization without changing the scoring engine.

## Daily Aggregation Metrics

For each ticker and date:
- avg_score (sector-weighted)
- volume (headline count)
- positive_ratio
- negative_ratio

Aggregation operates only on previously scored headlines stored in SQLite.

## Reporting Metrics (CLI report)

The report command computes additional analytics on top of daily aggregates:

### Rolling Average

3-day rolling average of daily sentiment.

### Volume-Weighted Volatility

Standard deviation of daily sentiment weighted by daily volume:
- Mean = volume-weighted mean sentiment
- Variance = volume-weighted variance
- Volatility = sqrt(variance)

### Momentum

Change in average sentiment between last two days:
```bash
momentum = last_day_avg - previous_day_avg
```

### Z-Score

Normalized last-day sentiment relative to volume-weighted mean:
```bash
z_score = (last_day - mean) / volatility
```

### Trend Classification
- improving
- deteriorating
- flat

Based purely on momentum sign.

### Volume Spike Detection

Flags True if latest day's volume > 1.5 × average volume.

## CLI Usage
### Ingest Data
```bash
python -m src.cli ingest data/sample_news.json
```

Supported formats:
- JSON
- CSV

Inserts records into SQLite database.

### Run Full Pipeline
```bash
python -m src.cli run data/sample_news.json
```

Performs:
- load
- score
- persist
- aggregate

Outputs structured daily aggregates.

### Summary (All Tickers)
```bash
python -m src.cli summary
```

Outputs per-ticker:
- total_volume
- overall_avg_score (volume-weighted across all days)

### Detailed Report
```bash
python -m src.cli report --ticker AAPL
```

Optional filter:
```bash
--min-volume <int>
```

Example:
```bash
python -m src.cli report --ticker AAPL --min-volume 5
```

If filtering removes all days, exits with message.

## Example Output

```json
{
  "ticker": "AAPL",
  "volatility": 0.0123,
  "momentum": -0.045,
  "z_score": -1.22,
  "trend": "deteriorating",
  "volume_spike": false,
  "days": [
    {
      "date": "2024-02-01",
      "avg_score": -0.27,
      "rolling_3": -0.27,
      "volume": 2,
      "positive_ratio": 0.5,
      "negative_ratio": 0.5
    }
  ]
}
```

## Limitations

- No contextual understanding
- No negation handling
- No sarcasm detection
- No phrase-level semantics
- No weighting by source credibility (beyond sector weights)
- No intraday granularity

This is a lexical heuristic not a language model.
It is suited for deterministic signal enrichment, not decision automation.

## Future Additions

- Negation handling
- Phrase scoring
- Extended config-driven keyword weights
- Source credibility weighting
- Time-decay weighting
- API layer