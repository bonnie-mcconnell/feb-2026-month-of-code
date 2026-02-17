export interface AppConfig {
  concurrency: number;
  pollIntervalMs: number;
  jobTimeoutMs: number;
  retryBaseDelayMs: number;
}

export const defaultConfig: AppConfig = {
  concurrency: 2,
  pollIntervalMs: 100,
  jobTimeoutMs: 5000,
  retryBaseDelayMs: 100,
};
