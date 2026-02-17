import { Job } from "../domain/job";
import { JobQueue } from "./queue";

export class InMemoryQueue implements JobQueue {
  private readonly jobs = new Map<string, Job>();
  private readonly pendingOrder: string[] = [];
  private readonly deadLetterIds: string[] = [];

  async enqueue(job: Job): Promise<void> {
    this.jobs.set(job.id, job);
    this.pendingOrder.push(job.id);
  }

  async dequeue(): Promise<Job | null> {
    const jobId = this.pendingOrder.shift();
    if (!jobId) return null;

    return this.jobs.get(jobId) ?? null;
  }

  async markCompleted(jobId: string): Promise<void> {
    this.jobs.delete(jobId);
  }

  async markFailed(_jobId: string): Promise<void> {
    // no-op — worker controls retry
  }

  async moveToDeadLetter(jobId: string): Promise<void> {
    if (this.jobs.has(jobId)) {
      this.deadLetterIds.push(jobId);
    }
  }

  async getDeadLetterJobs(): Promise<Job[]> {
    return this.deadLetterIds
      .map(id => this.jobs.get(id))
      .filter((job): job is Job => job !== undefined);
  }

  async getJob(jobId: string): Promise<Job | undefined> {
    return this.jobs.get(jobId);
  }
}
