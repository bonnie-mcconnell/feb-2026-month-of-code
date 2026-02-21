export type RiskTier = "LOW" | "MEDIUM" | "HIGH"

export function classifyRiskTier(
  score: number
): RiskTier {

  if (score < 30) return "LOW"
  if (score < 70) return "MEDIUM"
  return "HIGH"
}