import random
import time
from dataclasses import asdict

from observability_harness.instrumentation.retry import retry
from observability_harness.instrumentation.logger import emit_log
from observability_harness.contracts.logging_schema import LogLevel
from observability_harness.slo.types import RequestObservation, SLOSpec
from observability_harness.slo.evaluator import evaluate_slo


# simulate crypto price fetch
@retry(attempts=3)
def fetch_price():
    if random.random() < 0.3:
        raise ConnectionError("exchange timeout")
    return random.uniform(30000, 40000)


def main():
    observations = []

    for i in range(10):
        start = int(time.time())
        try:
            price = fetch_price()

            emit_log(
                service="crypto-arb",
                environment="dev",
                level=LogLevel.INFO,
                correlation_id=f"req-{i}",
                event="price_fetched",
                metadata={"price": price},
            )

            latency = random.randint(50, 300)

            observations.append(
                RequestObservation(
                    timestamp=int(time.time()),
                    latency_ms=latency,
                    success=True,
                )
            )

        except Exception as e:
            emit_log(
                service="crypto-arb",
                environment="dev",
                level=LogLevel.ERROR,
                correlation_id=f"req-{i}",
                event="fetch_failed",
                error_type=type(e).__name__,
            )

            observations.append(
                RequestObservation(
                    timestamp=int(time.time()),
                    latency_ms=0,
                    success=False,
                )
            )

    spec = SLOSpec(
        service="crypto-arb",
        window_minutes=5,
        availability=0.95,
        p95_latency_ms=500,
        error_rate=0.05, 
    )

    result = evaluate_slo(
        observations,
        spec,
        current_time=int(time.time()),
    )

    print("\nFinal SLO Evaluation:")
    for k, v in asdict(result).items():
        if k == "violated":
            print(f"{k}: {v}")
        else:
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()