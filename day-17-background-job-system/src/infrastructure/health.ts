export interface HealthCheck {
  isHealthy(): Promise<boolean>;
}

export class BasicHealthCheck implements HealthCheck {
  async isHealthy(): Promise<boolean> {
    return true;
  }
}
