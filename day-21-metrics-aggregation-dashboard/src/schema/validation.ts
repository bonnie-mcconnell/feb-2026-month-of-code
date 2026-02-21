import { z } from "zod"

export const normalizedUptimeSchema = z.object({
  averageAvailabilityPct: z.number().min(0).max(100),
  incidentsLast30Days: z.number().min(0),
  longestOutageMinutes: z.number().min(0),
})

export const normalizedJobsSchema = z.object({
  totalProcessed: z.number().min(0),
  failureRatePct: z.number().min(0).max(100),
  retryRatePct: z.number().min(0).max(100),
  deadLetterRatePct: z.number().min(0).max(100),
})

export const normalizedRepositorySchema = z.object({
  linesOfCode: z.number().min(0),
  churnScore: z.number().min(0).max(100),
  complexityScore: z.number().min(0).max(100),
})

export const normalizedRepoHealthSchema = z.object({
  healthScore: z.number().min(0).max(100),
  contributorRiskPct: z.number().min(0).max(100),
  stalenessDays: z.number().min(0),
})

export const aggregationInputSchema = z.object({
  uptime: normalizedUptimeSchema.optional(),
  jobs: normalizedJobsSchema.optional(),
  repository: normalizedRepositorySchema.optional(),
  repoHealth: normalizedRepoHealthSchema.optional(),
})