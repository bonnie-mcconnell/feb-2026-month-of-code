import { readdir } from "fs/promises";
import path from "path";
import { Dirent } from "fs";
import { Ignore } from "ignore";
import { isBinaryFile } from "./binaryDetector.js";

export async function* walkFiles(
  rootPath: string,
  ig: Ignore
): AsyncGenerator<string> {
  async function* walk(dir: string): AsyncGenerator<string> {
    const entries: Dirent[] = await readdir(dir, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      const relativePath = path.relative(rootPath, fullPath);

      if (ig.ignores(relativePath)) continue;

      if (entry.isDirectory()) {
        yield* walk(fullPath);
      } else if (entry.isFile()) {
        const binary = await isBinaryFile(fullPath);
        if (!binary) {
          yield fullPath;
        }
      }
    }
  }

  yield* walk(rootPath);
}
