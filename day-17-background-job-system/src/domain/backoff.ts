export interface BackoffConfig {
  baseDelayMs: number;
  maxDelayMs?: number;
}

export function calculateExponentialBackoff(
  attempt: number,
  config: BackoffConfig
): number {
  if (attempt < 1) {
    throw new Error("Attempt must be >= 1");
  }

  const delay = config.baseDelayMs * Math.pow(2, attempt - 1);

  if (config.maxDelayMs) {
    return Math.min(delay, config.maxDelayMs);
  }

  return delay;
}
