import { IdempotencyStore } from "./idempotencyStore";

export class InMemoryIdempotencyStore implements IdempotencyStore {
  private readonly processedKeys = new Set<string>();

  async has(key: string): Promise<boolean> {
    return this.processedKeys.has(key);
  }

  async markProcessed(key: string): Promise<void> {
    this.processedKeys.add(key);
  }
}
