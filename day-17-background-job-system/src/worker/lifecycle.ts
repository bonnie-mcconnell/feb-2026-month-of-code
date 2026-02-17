import { Worker } from "./worker";
import { Logger } from "../infrastructure/logger";

export class WorkerLifecycle {
  constructor(
    private readonly worker: Worker,
    private readonly logger: Logger
  ) {}

  async start(): Promise<void> {
    await this.worker.start();
  }

  async stop(): Promise<void> {
    await this.worker.stop();
  }

  attachSignalHandlers(): void {
    process.on("SIGINT", async () => {
      this.logger.log({
        level: "info",
        event: "signal_sigint_received",
        timestamp: Date.now(),
      });

      await this.stop();
      process.exit(0);
    });

    process.on("SIGTERM", async () => {
      this.logger.log({
        level: "info",
        event: "signal_sigterm_received",
        timestamp: Date.now(),
      });

      await this.stop();
      process.exit(0);
    });
  }
}
