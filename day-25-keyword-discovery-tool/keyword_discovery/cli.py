import argparse
import json
import sys
from pathlib import Path

from keyword_discovery.pipeline.ingestion import ingest_directory, IngestionError
from keyword_discovery.services.keyword_engine import KeywordEngine


def parse_ngrams(value: str):
    try:
        return sorted({int(v.strip()) for v in value.split(",")})
    except ValueError:
        raise argparse.ArgumentTypeError("Invalid ngram format. Example: 1,2,3")


def main():
    parser = argparse.ArgumentParser(
        prog="keyword-discover",
        description="Deterministic TF-IDF keyword discovery engine",
    )

    parser.add_argument("--input", required=True)
    parser.add_argument("--top", type=int, default=50)
    parser.add_argument("--ngrams", type=parse_ngrams, default="1")
    parser.add_argument("--stopwords", type=str, default=None)
    parser.add_argument("--min-doc-frequency", type=int, default=1)
    parser.add_argument("--max-doc-frequency", type=int, default=5)
    parser.add_argument("--min-score", type=float, default=0.05)
    parser.add_argument("--export", type=str, default=None)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument(
        "--scoring",
        choices=["tfidf", "bm25"],
        default="tfidf",
    )

    parser.add_argument(
        "--suppress-subterms",
        action="store_true",
    )
    parser.add_argument("--export-index", type=str, default=None)
    parser.add_argument(
        "--similarity",
        nargs=2,
        metavar=("DOC_ID_A", "DOC_ID_B"),
        help="Compute cosine similarity between two document IDs",
    )
    
    args = parser.parse_args()

    try:
        corpus = ingest_directory(args.input)

        engine = KeywordEngine(
            corpus=corpus,
            ngrams=args.ngrams,
            stopword_file=args.stopwords,
            scoring=args.scoring,
            suppress_subterms=args.suppress_subterms,
        )

        if args.similarity:
            doc_a, doc_b = args.similarity
            similarity = engine.compute_document_similarity(doc_a, doc_b)
            print(json.dumps({
                "doc_id_a": doc_a,
                "doc_id_b": doc_b,
                "cosine_similarity": round(similarity, 6),
            }, indent=2))
            return

        if args.export_index:
            index_data = engine.export_inverted_index()
            Path(args.export_index).write_text(
                json.dumps(index_data, indent=2),
                encoding="utf-8"
            )

        scores = engine.compute_scores()
        top_keywords = scores[: args.top]

        long_tail = engine.extract_long_tail(
            scores,
            min_doc_frequency=args.min_doc_frequency,
            max_doc_frequency=args.max_doc_frequency,
            min_score=args.min_score,
        )

        result = {
            "corpus_size": corpus.size,
            "total_unique_terms": len(engine.index.inverted_index),
            "top_keywords": [
                {
                    "term": s.term,
                    "ngram_size": s.ngram_size,
                    "doc_frequency": s.doc_frequency,
                    "tfidf_score": round(s.tfidf_score, 3),
                }
                for s in top_keywords
            ],
            "long_tail_keywords": [
                {
                    "term": k.term,
                    "ngram_size": k.ngram_size,
                    "doc_frequency": k.doc_frequency,
                    "tfidf_score": round(k.score, 3),
                }
                for k in long_tail
            ],
        }

        output = json.dumps(result, indent=2)

        if args.export:
            Path(args.export).write_text(output, encoding="utf-8")
        else:
            print(output)

    except IngestionError as e:
        if args.debug:
            raise
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


# add similarity doc1 doc2 flag, print similarity score