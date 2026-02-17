import { JobStatus } from "./jobStatus";
import { randomUUID } from "crypto";

export interface JobPayload {
  [key: string]: unknown;
}

export interface Job {
  readonly id: string;
  readonly type: string;
  readonly payload: JobPayload;

  readonly createdAt: number;
  readonly idempotencyKey?: string;

  attempts: number;
  maxAttempts: number;
  lastAttemptAt?: number;

  status: JobStatus;
}

export interface CreateJobInput {
  type: string;
  payload: JobPayload;
  maxAttempts: number;
  idempotencyKey?: string;
}

export function createJob(input: CreateJobInput): Job {
  if (!input.type) {
    throw new Error("Job type is required");
  }

  if (input.maxAttempts <= 0) {
    throw new Error("maxAttempts must be greater than 0");
  }

  return {
    id: randomUUID(),
    type: input.type,
    payload: input.payload,
    createdAt: Date.now(),
    idempotencyKey: input.idempotencyKey,
    attempts: 0,
    maxAttempts: input.maxAttempts,
    status: "pending",
  };
}
