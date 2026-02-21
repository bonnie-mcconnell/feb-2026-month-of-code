export class MetricsParseError extends Error {
  constructor(
    public readonly source: string,
    message: string
  ) {
    super(`[${source}] ${message}`)
  }
}