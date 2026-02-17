import { Logger, LogEvent } from "./logger";

export class ConsoleLogger implements Logger {
  log(event: LogEvent): void {
    process.stdout.write(JSON.stringify(event) + "\n");
  }

  info(message: string, metadata?: Record<string, unknown>): void {
    this.log({
      level: "info",
      event: "log",
      timestamp: Date.now(),
      message,
      metadata,
    });
  }

  error(
    message: string,
    error?: Error,
    metadata?: Record<string, unknown>
  ): void {
    this.log({
      level: "error",
      event: "error",
      timestamp: Date.now(),
      message,
      metadata,
      error: error
        ? {
            name: error.name,
            message: error.message,
            stack: error.stack,
          }
        : undefined,
    });
  }
}
