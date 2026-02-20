import { z } from "zod"

export const fileSchema = z.object({
  path: z.string(),
  loc: z.object({
    total: z.number(),
    code: z.number(),
    comments: z.number(),
    blank: z.number()
  }),
  complexity: z.number(),
  churn: z.number().optional()
})

export const directorySchema = z.object({
  fileCount: z.number(),
  totalLines: z.number(),
  codeLines: z.number(),
  commentLines: z.number(),
  blankLines: z.number()
})

export const indexSchema = z.object({
  repo: z.object({
    path: z.string(),
    name: z.string(),
    generatedAt: z.string()
  }),
  files: z.array(fileSchema),
  directories: z.record(z.string(), directorySchema)
})

export type RepoIndexSchema = z.infer<typeof indexSchema>