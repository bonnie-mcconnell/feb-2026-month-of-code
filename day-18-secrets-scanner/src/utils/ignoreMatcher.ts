import ignorePkg from "ignore";
import type { Ignore } from "ignore";
import { readFile } from "node:fs/promises";
import * as path from "node:path";

const ignore = (ignorePkg as any).default ?? ignorePkg;

const BUILTIN_IGNORES = [
  "node_modules/**",
  "dist/**",
  "build/**",
  ".git/**"
];

/**
 * Creates an Ignore matcher that merges:
 * - Built-in ignores
 * - .gitignore (if present)
 * - .secretscannerignore (if present)
 */
export async function createIgnoreMatcher(
  rootPath: string,
  customIgnorePath?: string // kept for backward compatibility
): Promise<Ignore> {
  const ig: Ignore = ignore();

  // 1️⃣ Built-in ignores (always applied)
  ig.add(BUILTIN_IGNORES);

  // 2️⃣ .gitignore (optional)
  await loadIgnoreFile(path.join(rootPath, ".gitignore"), ig);

  // 3️⃣ .secretscannerignore (optional)
  await loadIgnoreFile(path.join(rootPath, ".secretscannerignore"), ig);

  // 4️⃣ Explicit custom ignore path (legacy support)
  if (customIgnorePath) {
    await loadIgnoreFile(customIgnorePath, ig);
  }

  return ig;
}

async function loadIgnoreFile(
  filePath: string,
  ig: Ignore
): Promise<void> {
  try {
    const content = await readFile(filePath, "utf8");

    // Trim BOM if present (important on Windows)
    const sanitized = content.replace(/^\uFEFF/, "");

    ig.add(sanitized);
  } catch {
    // File does not exist → silently ignore
  }
}
