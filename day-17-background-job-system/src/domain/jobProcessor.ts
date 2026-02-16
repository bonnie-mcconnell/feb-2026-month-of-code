import { Job } from "./job";

export interface JobProcessor {
  process(job: Job): Promise<void>;
}
