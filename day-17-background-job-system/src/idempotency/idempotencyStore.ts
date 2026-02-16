export interface IdempotencyStore {
  has(key: string): Promise<boolean>;

  markProcessed(key: string): Promise<void>;
}
