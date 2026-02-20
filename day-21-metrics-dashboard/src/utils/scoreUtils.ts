export function clampScore(value: number): number {
  if (Number.isNaN(value) || !Number.isFinite(value)) {
    return 0
  }

  if (value < 0) return 0
  if (value > 100) return 100

  return Math.round(value * 100) / 100
}

export function invertScore(value: number): number {
  return clampScore(100 - value)
}

export function weightedAverage(
  values: Array<{ value: number; weight: number }>
): number {
  const totalWeight = values.reduce((acc, v) => acc + v.weight, 0)

  if (totalWeight === 0) {
    return 0
  }

  const weightedSum = values.reduce(
    (acc, v) => acc + v.value * v.weight,
    0
  )

  return clampScore(weightedSum / totalWeight)
}