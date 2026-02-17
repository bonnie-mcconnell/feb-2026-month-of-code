import { randomUUID } from "crypto";

export class Job {
  public readonly id: string;
  public readonly createdAt: number;
  public attempts = 0;

  constructor(
    public readonly name: string,
    public readonly payload?: unknown,
    public readonly idempotencyKey?: string
  ) {
    this.id = randomUUID();
    this.createdAt = Date.now();
  }
}
