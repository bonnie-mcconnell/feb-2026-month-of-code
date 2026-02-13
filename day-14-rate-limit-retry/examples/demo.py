from src.client import HttpClient
from src.retry import RetryPolicy
from src.rate_limiter import RateLimiter
from src.exceptions import RetryableError
import random
import time

# Seed random for deterministic demo behavior
random.seed(42)

def unreliable_request():
    """Simulate a request that fails ~50% of the time."""
    print("executing request")
    if random.random() < 0.5:
        print("failing temporarily")
        raise RetryableError("temporary failure")
    print("success")
    return "ok"

# Setup middleware
retry = RetryPolicy(
    max_attempts=5,
    base_delay=0.5,
    jitter=True
)

rate_limiter = RateLimiter(
    capacity=2,
    refill_rate=1
)

client = HttpClient(
    middlewares=[retry, rate_limiter]
)

# Execute and observe behavior
try:
    result = client.execute(unreliable_request)
except RetryableError:
    print("request ultimately failed")
    result = None

print("\n--- Observability ---")
print(f"Retry attempts: {retry.last_attempt_count}")
print(f"Retries performed: {retry.last_retry_count}")
print(f"Total wait (s): {retry.last_total_wait:.2f}")
print(f"Last failure: {retry.last_failure}")
print(f"Rate limiter last wait (s): {rate_limiter.last_wait_time}")
print(f"Rate limiter loops: {rate_limiter.last_acquire_loops}")

print("\nResult:", result)
