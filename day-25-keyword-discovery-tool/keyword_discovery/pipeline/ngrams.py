from typing import Iterable, List


def generate_ngrams(tokens: Iterable[str], n_values: List[int]) -> List[str]:
    """
    Sliding window n-gram generation.
    Maintains original token order.
    """
    token_list = list(tokens)
    results: List[str] = []

    for n in sorted(n_values):
        if n <= 0:
            continue

        for i in range(len(token_list) - n + 1):
            ngram = " ".join(token_list[i:i + n])
            results.append(ngram)

    return results