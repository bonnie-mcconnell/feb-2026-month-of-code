export function calculateShannonEntropy(input: string): number {
  if (!input.length) return 0;

  const freqMap = new Map<string, number>();

  for (const char of input) {
    freqMap.set(char, (freqMap.get(char) ?? 0) + 1);
  }

  let entropy = 0;

  for (const count of freqMap.values()) {
    const p = count / input.length;
    entropy -= p * Math.log2(p);
  }

  return entropy;
}

export function isHighEntropyString(
  value: string,
  threshold: number = 4.5,
  minLength: number = 20
): boolean {
  if (value.length < minLength) return false;

  return calculateShannonEntropy(value) >= threshold;
}
