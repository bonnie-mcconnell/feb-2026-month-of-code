import { Metrics } from "./metrics";

export class InMemoryMetrics implements Metrics {
  private counters: Record<string, number> = {};
  private observations: Array<{
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

  getCounter(name: string): number {
    return this.counters[name] ?? 0;
  }

  exportPrometheus(): string {
    return Object.entries(this.counters)
      .map(([key, value]) => `${key} ${value}`)
      .join("\n");
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
