import { Logger, LogEvent } from "./logger";

export class ConsoleLogger implements Logger {
  log(event: LogEvent): void {
    // JSON structured output
    const output = JSON.stringify(event);
    process.stdout.write(output + "\n");
  }
}
