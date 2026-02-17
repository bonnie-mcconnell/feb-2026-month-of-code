import { promises as fs } from "fs";
import { Job } from "../domain/job";
import { JobQueue } from "./queue";

export class FileQueue implements JobQueue {
  constructor(private readonly filePath: string) {}

  private async read(): Promise<Job[]> {
    try {
      const data = await fs.readFile(this.filePath, "utf-8");
      return JSON.parse(data);
    } catch {
      return [];
    }
  }

  private async write(jobs: Job[]): Promise<void> {
    await fs.writeFile(this.filePath, JSON.stringify(jobs, null, 2));
  }

  async enqueue(job: Job): Promise<void> {
    const jobs = await this.read();
    jobs.push(job);
    await this.write(jobs);
  }

  async dequeue(): Promise<Job | null> {
    const jobs = await this.read();
    const job = jobs.shift() ?? null;
    await this.write(jobs);
    return job;
  }

  async markCompleted(): Promise<void> {}
  async markFailed(): Promise<void> {}
  async moveToDeadLetter(): Promise<void> {}
}
