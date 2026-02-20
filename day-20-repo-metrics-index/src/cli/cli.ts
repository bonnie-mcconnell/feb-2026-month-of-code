#!/usr/bin/env node
import fs from "node:fs/promises"
import path from "node:path"
import { Command } from "commander"
import { buildIndex } from "../indexer/indexBuilder.js"
import { DEFAULT_CONFIG } from "../config/config.js"

const program = new Command()

program
  .name("repo-index")
  .description("Generate a metrics index for a local repository")
  .argument("<root>", "Path to repository root")
  .option("--extensions <list>", "Comma-separated file extensions to include")
  .option(
    "--parallel <number>",
    "Number of files to process in parallel",
    `${DEFAULT_CONFIG.parallelism}`
  )
  .option("--no-git", "Disable Git churn analysis")
  .option("--skip-binary", "Skip binary file analysis")
  .option("-o, --output <file>", "Write JSON output to file")
  .option(
    "--format <type>",
    "Output format: 'json' (default) or 'pretty'",
    "json"
  )
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
    ? options.extensions
        .split(",")
        .map((s: string) => s.trim().replace(/^\./, "").toLowerCase())
    : null,
  parallelism: Number(options.parallel),
  enableGit: options.git,
  includeBinaryAnalysis: !options.skipBinary
}

async function main() {
  try {
    const index = await buildIndex(config)

    let output: string
    if (options.format === "pretty") {
      output = JSON.stringify(index, null, 4)
    } else {
      output = JSON.stringify(index, null, 2)
    }

    if (options.output) {
      await fs.writeFile(options.output, output)
      console.log(`Index written to ${options.output}`)
    } else {
      console.log(output)
    }
  } catch (err) {
    console.error("Failed to build index:", err)
    process.exit(1)
  }
}

main()