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

  if (records.length === 0) {
    return {
        totalProcessed: 0,
        failureRatePct: 0,
        retryRatePct: 0,
        deadLetterRatePct: 0,
    }
    }

    const total = records.length

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