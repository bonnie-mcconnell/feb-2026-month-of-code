import { Metrics } from "./metrics";

export class InMemoryMetrics implements Metrics {
  public counters: Record<string, number> = {};
  public observations: Array<{
    name: string;
    value: number;
    tags?: Record<string, string>;
  }> = [];

  increment(name: string, tags?: Record<string, string>): void {
    const key = this.buildKey(name, tags);
    this.counters[key] = (this.counters[key] ?? 0) + 1;
  }

  observe(
    name: string,
    value: number,
    tags?: Record<string, string>
  ): void {
    this.observations.push({ name, value, tags });
  }

  private buildKey(
    name: string,
    tags?: Record<string, string>
  ): string {
    if (!tags) return name;

    const sorted = Object.keys(tags)
      .sort()
      .map((k) => `${k}:${tags[k]}`)
      .join("|");

    return `${name}|${sorted}`;
  }
}
