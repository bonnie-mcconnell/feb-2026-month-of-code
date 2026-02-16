import { Job } from "../domain/job";

export interface JobQueue {
  enqueue(job: Job): Promise<void>;

  /**
   * Dequeues the next pending job and marks it as processing.
   * Returns null if no job is available.
   */
  dequeue(): Promise<Job | null>;

  markCompleted(jobId: string): Promise<void>;

  markFailed(jobId: string): Promise<void>;

  moveToDeadLetter(jobId: string): Promise<void>;

  getJob(jobId: string): Promise<Job | undefined>;

  getDeadLetterJobs(): Promise<Job[]>;
}
