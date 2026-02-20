#!/usr/bin/env node
import path from "node:path"
import { Command } from "commander"
import { buildIndex } from "../indexer/indexBuilder.js"
import { jsonReporter } from "../reporters/jsonReporter.js"
import { DEFAULT_CONFIG } from "../config/config.js"

const program = new Command()

program
  .name("repo-index")
  .description("Generate a metrics index for a local repository")
  .argument("<root>", "Path to repository root")
  .option("--extensions <list>", "Comma-separated file extensions to include")
  .option("--parallel <number>", "Number of files to process in parallel", `${DEFAULT_CONFIG.parallelism}`)
  .option("--no-git", "Disable Git churn analysis")
  .option("--skip-binary", "Skip binary file analysis")
  .parse(process.argv)

const options = program.opts()
const root = program.args[0]

if (!root) {
  console.error("Error: repository root path is required")
  process.exit(1)
}

const config = {
  rootPath: path.resolve(root),
  includeExtensions: options.extensions
    ? options.extensions.split(",").map((s: string) => s.trim())
    : null,
  parallelism: Number(options.parallel),
  enableGit: options.git,
  includeBinaryAnalysis: !options.skipBinary
}

async function main() {
  try {
    const index = await buildIndex(config)
    jsonReporter(index)
  } catch (err) {
    console.error("Failed to build index:", err)
    process.exit(1)
  }
}

main()