import { getGitChurn } from "../git/gitClient.js"

export async function analyzeChurn(
  rootPath: string,
  filePath: string
): Promise<number> {
  return getGitChurn(rootPath, filePath)
}