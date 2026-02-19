export function logisticScore(
  value: number,
  midpoint: number,
  steepness = 0.1
): number {
  const score =
    100 / (1 + Math.exp(-steepness * (value - midpoint)))

  return Math.max(0, Math.min(100, score))
}
