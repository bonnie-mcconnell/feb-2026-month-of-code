import { promises as fs } from "fs";
import { Job } from "../domain/job";
import { JobQueue } from "./queue";

interface FileQueueData {
  active: Job[];
  dead: Job[];
}

export class FileQueue implements JobQueue {
  constructor(private readonly filePath: string) {}

  private async read(): Promise<FileQueueData> {
    try {
      const data = await fs.readFile(this.filePath, "utf-8");
      return JSON.parse(data);
    } catch {
      return { active: [], dead: [] };
    }
  }

  private async write(data: FileQueueData): Promise<void> {
    await fs.writeFile(this.filePath, JSON.stringify(data, null, 2));
  }

  async enqueue(job: Job): Promise<void> {
    const data = await this.read();
    data.active.push(job);
    await this.write(data);
  }

  async dequeue(): Promise<Job | null> {
    const data = await this.read();
    const job = data.active.shift() ?? null;
    await this.write(data);
    return job;
  }

  async markCompleted(jobId: string): Promise<void> {
    // no-op (already removed on dequeue)
  }

  async markFailed(jobId: string): Promise<void> {
    // no-op (retry handled by worker)
  }

  async moveToDeadLetter(jobId: string): Promise<void> {
    const data = await this.read();

    const jobIndex = data.active.findIndex(j => j.id === jobId);
    if (jobIndex === -1) return;

    const [job] = data.active.splice(jobIndex, 1);
    data.dead.push(job);

    await this.write(data);
  }

  async getJob(jobId: string): Promise<Job | undefined> {
    const data = await this.read();
    return data.active.find(j => j.id === jobId);
  }

  async getDeadLetterJobs(): Promise<Job[]> {
    const data = await this.read();
    return data.dead;
  }
}
