import { Job } from "./job";
import { calculateExponentialBackoff, BackoffConfig } from "./backoff";

export interface RetryDecision {
  shouldRetry: boolean;
  delayMs?: number;
  shouldDeadLetter: boolean;
}

export interface RetryPolicyConfig extends BackoffConfig {}

export class RetryPolicy {
  constructor(private readonly config: RetryPolicyConfig) {
    if (config.baseDelayMs <= 0) {
      throw new Error("baseDelayMs must be greater than 0");
    }
  }

  evaluate(job: Job): RetryDecision {
    if (job.attempts >= job.maxAttempts) {
      return {
        shouldRetry: false,
        shouldDeadLetter: true,
      };
    }

    const nextAttempt = job.attempts + 1;

    const delay = calculateExponentialBackoff(
      nextAttempt,
      this.config
    );

    return {
      shouldRetry: true,
      delayMs: delay,
      shouldDeadLetter: false,
    };
  }
}
