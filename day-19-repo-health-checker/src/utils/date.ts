// src/utils/date.ts

export function daysBetween(a: Date, b: Date): number {
  const diff = Math.abs(a.getTime() - b.getTime())
  return Math.floor(diff / (1000 * 60 * 60 * 24))
}
