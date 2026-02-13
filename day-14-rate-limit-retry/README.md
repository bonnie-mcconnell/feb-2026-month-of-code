# Rate Limiting & Retry Middleware

A minimal, composable HTTP client middleware system designed for local pipelines, scrapers, or API clients.  
Demonstrates production-grade retry logic, rate limiting, and clean middleware composition.

---

## Why Retry Logic is Complex

Retrying sounds simple, but naive retries can cause:

- Duplicate operations on non-idempotent endpoints  
- Retry storms that exacerbate load spikes  
- Hidden delays when backoff is miscalculated  

This implementation:

- Retries only explicitly `RetryableError`  
- Uses exponential backoff  
- Optional jitter prevents synchronized retries  

---

## Why Naive Retries are Dangerous

- Retrying FatalErrors or 4xx client errors can hide bugs  
- Blind loops can overload downstream systems  
- Lack of observability leaves operations blind  

---

## Why Rate Limiting Matters

Rate limiting ensures:

- Compliance with service limits  
- Smooth, predictable traffic  
- Prevention of burst abuse  

This library uses a token bucket with:

- Configurable capacity  
- Configurable refill rate  
- Blocking behavior  

---

## Design Decisions

- **Middleware Interface**: composable, callable, minimal  
- **HttpClient**: executes middleware stack deterministically  
- **RetryPolicy**: isolated, deterministic, observable  
- **RateLimiter**: fractional refill, deterministic, blocking  

No framework dependencies, async, or distributed coordination.

---

## Backoff & Jitter

Backoff formula:
```bash
delay = base_delay * (backoff_factor ** (attempt - 1))
```

Optional jitter:
```bash
delay = delay * random()
```

Jitter prevents multiple clients from retrying simultaneously, avoiding retry storms.

---

## Observability Hooks

- RetryPolicy: `last_attempt_count`, `last_retry_count`, `last_total_wait`, `last_failure`  
- RateLimiter: `last_wait_time`, `last_acquire_loops`  

Hooks are lightweight and suitable for logging or monitoring during development.

---

## Known Limitations

- Single-threaded only, not thread-safe  
- No circuit breaker  
- No metrics framework  
- No async support  
- Rate limiter will block synchronously  

---

## Extension Ideas

- HTTP 429 `Retry-After` header support  
- Pluggable backoff strategies  
- Optional request timeouts  
- Integration with Day 13 scraper as demonstration

