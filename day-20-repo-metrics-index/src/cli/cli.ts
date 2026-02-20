#!/usr/bin/env node

import path from "node:path"
import { buildIndex } from "../indexer/indexBuilder.js"
import { jsonReporter } from "../reporters/jsonReporter.js"

async function main() {
  const target = process.argv[2]

  if (!target) {
    console.error("Usage: repo-index <path>")
    process.exit(1)
  }

  const absolute = path.resolve(target)
  const index = await buildIndex(absolute)

  jsonReporter(index)
}

main()