export interface Metrics {
  increment(
    name: string,
    tags?: Record<string, string>
  ): void;

  observe(
    name: string,
    value: number,
    tags?: Record<string, string>
  ): void;
}
