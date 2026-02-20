export function estimateComplexity(sourceCode: string): number {
  const patterns = [
    /\bif\b/g,
    /\bfor\b/g,
    /\bwhile\b/g,
    /\bcase\b/g,
    /\bcatch\b/g,
    /&&/g,
    /\|\|/g,
    /\?/g
  ]

  let complexity = 1

  for (const pattern of patterns) {
    const matches = sourceCode.match(pattern)
    if (matches) {
      complexity += matches.length
    }
  }

  return complexity
}