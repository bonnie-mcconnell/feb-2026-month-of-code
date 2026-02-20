import type { RepoIndexSchema } from "../types/indexSchema.js"

export function consoleReporter(index: RepoIndexSchema) {
  console.log("Repository:", index.repo.name)
  console.log("Files:", index.files.length)
  console.log("Directories:", Object.keys(index.directories).length)

  const totalLOC = index.files.reduce(
    (sum, f) => sum + f.loc.total,
    0
  )

  console.log("Total LOC:", totalLOC)
}