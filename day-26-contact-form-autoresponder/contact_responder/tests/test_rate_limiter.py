from contact_responder.infra.rate_limiter import RateLimiter


def test_allows_under_limit():
    limiter = RateLimiter(max_requests=2, window_seconds=60)

    assert limiter.allow("1.1.1.1")
    assert limiter.allow("1.1.1.1")


def test_blocks_over_limit():
    limiter = RateLimiter(max_requests=1, window_seconds=60)

    assert limiter.allow("1.1.1.1")
    assert limiter.allow("1.1.1.1") is False


