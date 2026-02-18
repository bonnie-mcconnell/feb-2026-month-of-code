import { readFile } from "node:fs/promises";
import type { Finding } from "../types/finding.js";
import { BUILTIN_RULES } from "../rules/builtinRules.js";
import { scanWithPatterns } from "./patternEngine.js";
import { scanWithEntropy } from "./entropyScanner.js";
import { walkFiles } from "../scanner/fileWalker.js";
import { createIgnoreMatcher } from "../utils/ignoreMatcher.js";
import { stableSortFindings } from "../utils/stableSort.js";

export interface ScanOptions {
  entropyThreshold?: number;
  minEntropyLength?: number;
}

export async function scanDirectory(
  rootPath: string,
  options: ScanOptions = {}
): Promise<Finding[]> {
  const findings: Finding[] = [];

  const entropyThreshold = options.entropyThreshold ?? 4.5;
  const minEntropyLength = options.minEntropyLength ?? 20;

  const ig = await createIgnoreMatcher(rootPath);

  for await (const filePath of walkFiles(rootPath, ig)) {
    let content: string;

    try {
      content = await readFile(filePath, "utf8");
    } catch {
      continue; // skip unreadable files safely
    }

    const patternFindings = scanWithPatterns(
      filePath,
      content,
      BUILTIN_RULES
    );

    const entropyFindings = scanWithEntropy(
      filePath,
      content,
      entropyThreshold,
      minEntropyLength
    );

    findings.push(...patternFindings, ...entropyFindings);
  }

  return stableSortFindings(findings);
}
