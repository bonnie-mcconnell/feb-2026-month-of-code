import { parse } from "csv-parse/sync"
import { NormalizedJobMetrics } from "../schema/internalTypes"

interface RawCsvRow {
  status: string
  retries: string | number
}

export function parseJobCsv(
  csvContent: string
): NormalizedJobMetrics {

  const records = parse(csvContent, {
    columns: true,
    skip_empty_lines: true,
  }) as RawCsvRow[]

  const total = records.length || 1

  const failures = records.filter(
    (r) => r.status === "failed"
  ).length

  const retries = records.filter(
    (r) => Number(r.retries) > 0
  ).length

  return {
    totalProcessed: total,
    failureRatePct: (failures / total) * 100,
    retryRatePct: (retries / total) * 100,
    deadLetterRatePct: 0,
  }
}