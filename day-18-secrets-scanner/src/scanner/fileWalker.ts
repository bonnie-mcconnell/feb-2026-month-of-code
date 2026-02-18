// src/scanner/fileWalker.ts
import { readdir } from "node:fs/promises";
import * as path from "node:path";
import type { Dirent } from "node:fs";
import { Ignore } from "ignore";
import { isBinaryFile } from "./binaryDetector.js";

/**
 * Recursively walk all files under rootPath, yielding only non-binary files
 * and respecting the provided ignore matcher.
 */
export async function* walkFiles(
  rootPath: string,
  ig: Ignore
): AsyncGenerator<string> {

  async function* walk(dir: string): AsyncGenerator<string> {
    const entries: Dirent[] = await readdir(dir, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      const relativePath = path.relative(rootPath, fullPath);

      // Skip ignored paths
      if (ig.ignores(relativePath)) continue;

      if (entry.isDirectory()) {
        yield* walk(fullPath); // recurse into directory
      } else if (entry.isFile()) {
        // Only yield non-binary files
        const binary = await isBinaryFile(fullPath);
        if (!binary) {
          yield fullPath;
        }
      }
    }
  }

  yield* walk(rootPath);
}
