from src.client import HttpClient
from src.retry import RetryPolicy
from src.rate_limiter import RateLimiter
from src.exceptions import RetryableError
import random
import time

def unreliable_request():
    print("executing request")
    if random.random() < 0.7:
        print("failing temporarily")
        raise RetryableError("temporary failure")
    print("success")
    return "ok"

client = HttpClient(
    middlewares=[
        RetryPolicy(max_attempts=5, base_delay=0.5, jitter=True),
        RateLimiter(capacity=2, refill_rate=1),
    ]
)

result = None
try:
    result = client.execute(unreliable_request)
except RetryableError:
    print("request ultimately failed")

print("Result:", result)
