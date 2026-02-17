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
      this.logger.info("SIGINT received, shutting down...");
      await this.stop();
      process.exit(0);
    });

    process.on("SIGTERM", async () => {
      this.logger.info("SIGTERM received, shutting down...");
      await this.stop();
      process.exit(0);
    });
  }
}
