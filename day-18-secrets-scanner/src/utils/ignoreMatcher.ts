import ignore, { Ignore } from "ignore";
import { readFile } from "fs/promises";
import path from "path";

const BUILTIN_IGNORES = [
  "node_modules/**",
  "dist/**",
  "build/**",
  ".git/**"
];

export async function createIgnoreMatcher(
  rootPath: string,
  customIgnorePath?: string
): Promise<Ignore> {
  const ig = ignore();

  ig.add(BUILTIN_IGNORES);

  // .gitignore
  try {
    const gitignorePath = path.join(rootPath, ".gitignore");
    const gitignore = await readFile(gitignorePath, "utf8");
    ig.add(gitignore);
  } catch {
    // no .gitignore is acceptable
  }

  if (customIgnorePath) {
    const custom = await readFile(customIgnorePath, "utf8");
    ig.add(custom);
  }

  return ig;
}
