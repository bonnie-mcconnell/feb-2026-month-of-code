import ignorePkg from "ignore";
import type { Ignore } from "ignore";
import { readFile } from "node:fs/promises";
import * as path from "node:path";

const ignore = (ignorePkg as any).default ?? ignorePkg;

const BUILTIN_IGNORES = [
  "node_modules/**",
  "dist/**",
  "build/**",
  ".git/**",
  "package-lock.json",
  "yarn.lock",
  "pnpm-lock.yaml",
  "tests/**",
  "**/*.test.ts"
];


export async function createIgnoreMatcher(
  rootPath: string,
  customIgnorePath?: string
): Promise<Ignore> {
  const ig: Ignore = ignore();

  // Built-in ignores
  ig.add(BUILTIN_IGNORES);

  // .gitignore
  await loadIgnoreFile(path.join(rootPath, ".gitignore"), ig);

  // .secretscannerignore
  await loadIgnoreFile(path.join(rootPath, ".secretscannerignore"), ig);

  // Backward compatibility
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
    const sanitized = content.replace(/^\uFEFF/, "");
    ig.add(sanitized);
  } catch {
    // Ignore missing file
  }
}
