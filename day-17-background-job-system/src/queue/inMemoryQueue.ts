// src/queue/inMemoryQueue.ts

import { Job } from "../domain/job";
import { JobQueue } from "./queue";

export class InMemoryQueue implements JobQueue {
  private readonly jobs = new Map<string, Job>();
  private readonly pendingOrder: string[] = [];
  private readonly deadLetterIds: string[] = [];

  async enqueue(job: Job): Promise<void> {
    if (this.jobs.has(job.id)) {
      throw new Error(`Job with id ${job.id} already exists`);
    }

    this.jobs.set(job.id, job);
    this.pendingOrder.push(job.id);
  }

  async dequeue(): Promise<Job | null> {
    while (this.pendingOrder.length > 0) {
      const jobId = this.pendingOrder.shift();
      if (!jobId) continue;

      const job = this.jobs.get(jobId);
      if (!job) continue;

      if (job.status !== "pending") {
        continue;
      }

      job.status = "processing";
      return job;
    }

    return null;
  }

  async markCompleted(jobId: string): Promise<void> {
    const job = this.getOrThrow(jobId);
    job.status = "completed";
  }

  async markFailed(jobId: string): Promise<void> {
    const job = this.getOrThrow(jobId);
    job.status = "failed";
  }

  async moveToDeadLetter(jobId: string): Promise<void> {
    const job = this.getOrThrow(jobId);

    job.status = "dead_lettered";
    this.deadLetterIds.push(jobId);
  }

  async getDeadLetterJobs(): Promise<Job[]> {
    return this.deadLetterIds
      .map((id) => this.jobs.get(id))
      .filter((job): job is Job => job !== undefined);
  }

  async getJob(jobId: string): Promise<Job | undefined> {
    return this.jobs.get(jobId);
  }

  private getOrThrow(jobId: string): Job {
    const job = this.jobs.get(jobId);
    if (!job) {
      throw new Error(`Job ${jobId} not found`);
    }
    return job;
  }
}
