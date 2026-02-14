from src.scorer import score_headline, classify


def test_positive_headline_scores_positive():
    headline = "Company reports strong growth and record profit"
    score = score_headline(headline)

    assert score > 0
    assert classify(score) == "positive"


def test_negative_headline_scores_negative():
    headline = "Company faces lawsuit after earnings miss and decline"
    score = score_headline(headline)

    assert score < 0
    assert classify(score) == "negative"


def test_neutral_headline_scores_zero():
    headline = "Company announces quarterly results"
    score = score_headline(headline)

    assert score == 0
    assert classify(score) == "neutral"


def test_mixed_sentiment_balances_correctly():
    headline = "Strong growth but weak outlook"
    score = score_headline(headline)

    # strong + growth = +2
    # weak = -1
    assert score == 1
