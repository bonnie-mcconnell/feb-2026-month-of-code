export interface RetryPolicy {
  shouldRetry(attempt: number, error: Error): boolean;
  nextDelay(attempt: number): number;
}

export class ExponentialBackoffRetryPolicy implements RetryPolicy {
  constructor(
    private readonly maxRetries: number,
    private readonly baseDelayMs: number
  ) {
    if (maxRetries < 0) {
      throw new Error("maxRetries must be >= 0");
    }

    if (baseDelayMs <= 0) {
      throw new Error("baseDelayMs must be > 0");
    }
  }

  shouldRetry(attempt: number): boolean {
    return attempt < this.maxRetries;
  }

  nextDelay(attempt: number): number {
    return this.baseDelayMs * Math.pow(2, attempt - 1);
  }
}
