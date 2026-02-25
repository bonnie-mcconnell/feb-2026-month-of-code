# Keyword Discovery Tool

A deterministic, fully test-covered keyword extraction and document similarity engine built from first principles using classical Information Retrieval (IR) methods.

This project implements TF-IDF, BM25, inverted indexing, cosine similarity, n-gram modeling, and long-tail phrase extraction without external NLP libraries.

## Overview

This tool performs:
- Directory ingestion (deterministic ordering)
- Tokenization & normalization
- N-gram generation (1–3 grams)
- Inverted index construction
- TF-IDF scoring
- BM25 scoring
- Per-document TF-IDF vectors
- Cosine similarity
- Long-tail keyword extraction
- Subsumption suppression
- CLI-driven querying
- JSON index export

The system is fully deterministic and designed for reproducibility.

## Architecture
```
domain/
    corpus.py
    document.py
    keyword.py
    scoring.py
pipeline/
    index_builder.py
    ingestion.py
    ngrams.py
    normalizer.py
    tokenizer.py
services/
    keyword_engine.py
cli.py
tests/
```

## Design Principles

- Pure functions where possible
- Deterministic ordering
- Domain-specific exceptions
- No hidden global state
- No external NLP dependencies
- High test coverage (97%)

## Mathematical Foundations
### Term Frequency (TF)

TF(t,d) = f_(t,d) / (∣d∣)

Where:
- f_(t,d)= frequency of term t in document d
- ∣d∣= total tokens in document
________________________________________

### Inverse Document Frequency (IDF)

IDF(t) = log⁡(N/(df_t ))

Where:
- N = total number of documents
- df_t= number of documents containing term t
________________________________________

### TF-IDF

TFIDF(t,d) = TF(t,d) × IDF(t)

________________________________________

### BM25

BM25(t,d) = IDF(t) ⋅ (f_(t,d) (k_1+1)) / (f_(t,d)+k_1 (1-b+b (∣d∣)/avgdl) )

Where:
- k_1= term saturation parameter
- b= length normalization parameter
- avgdl= average document length

Defaults:

- k1 = 1.5
- b = 0.75
________________________________________

### Cosine Similarity

"sim"(A,B) = (A⋅B) / (∥A∥∥B∥)

Used for document similarity over TF-IDF vectors.

## Features
### 1. Deterministic Ingestion

- Sorted file traversal
- Stable document IDs
- Consistent results across runs

### 2. Inverted Index

Maps:
```
term -> {doc_id: term_frequency}
```

Enables:
- Efficient document frequency computation
- Fast similarity calculations
- Exportable index

### 3. Long-Tail Phrase Extraction

- N-gram scoring
- Subsumption suppression
- Favors specific phrases over generic substrings
- Designed to surface SEO-relevant multiword terms

### 4. CLI Interface

Examples:

Extract Keywords
```bash
python -m keyword_discovery.cli --input ./docs
```

Compute Similarity
```bash
python -m keyword_discovery.cli \
  --input ./docs \
  --similarity doc_0001 doc_0002
```

Export Inverted Index
```bash
python -m keyword_discovery.cli \
  --input ./docs \
  --export-index index.json
```

Full CLI Options
```bash
python -m keyword_discovery.cli --help
```

Required
```bash
--input PATH
```

Directory containing .txt documents.

### Keyword Extraction Options
```bash
--top N
```

Number of top-ranked keywords (default: 50)
```bash
--ngrams 1,2,3
```

Comma-separated n-gram sizes (default: 1)
```bash
--scoring tfidf|bm25
```

Scoring method (default: tfidf)
```bash
--suppress-subterms
```

Removes lower-scoring substrings when a longer phrase dominates.
```bash
--stopwords FILE
```

Path to newline-separated stopword file.

### Long-Tail Filtering
```
--min-doc-frequency INT
--max-doc-frequency INT
--min-score FLOAT
```

Controls filtering for long-tail keyword extraction.

### Exporting
```bash
--export output.json
```

Writes full keyword result to JSON.
```bash
--export-index index.json
```

Exports inverted index as JSON.

### Similarity
```bash
--similarity DOC_ID_A DOC_ID_B
```

Computes cosine similarity between two documents.

### Debug Mode
```bash
--debug
```

Re-raises ingestion errors instead of graceful exit.

### Testing

- Unit tests for all scoring formulas
- CLI integration tests
- Determinism tests
- Error handling tests
- ≥ 97% coverage

Key properties tested:
- IDF monotonicity
- BM25 length normalization
- Cosine symmetry
- Stable document ordering
- Index export integrity

## Why No External NLP Libraries?

This system intentionally avoids NLTK, spaCy and sklearn for educational transparency, mathematical clarity, full control over implementation, and no hidden preprocessing behavior.
Everything is implemented explicitly.

### Tradeoffs

- No stemming
- No lemmatization
- No stopword removal by default
- No distributed indexing
- In-memory only

This is a compact IR engine, not Elasticsearch.

## Performance Characteristics

- Inverted index construction: O(total_terms)
- TF-IDF computation: O(unique_terms)
- Cosine similarity: O(vector_size)
- Suitable for small-to-medium corpora

## Windows Note

On Windows PowerShell, create test files using:
```
Set-Content filename.txt "text" -Encoding utf8
```
to avoid UTF-16 encoding issues.

## Version

v1.0.0 - deterministic IR engine with similarity and export support.
