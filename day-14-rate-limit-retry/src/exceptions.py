class RetryableError(Exception):
    """An error that is safe to retry."""
    pass


class FatalError(Exception):
    """An error that should not be retried."""
    pass


class RateLimitExceeded(Exception):
    """Raised when rate limiting cannot proceed."""
    pass
