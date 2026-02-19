import * as fs from "node:fs"
import * as path from "node:path"
import { fileURLToPath } from "node:url"
import { Ajv } from "ajv"
import type { ErrorObject } from "ajv"

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

// Read schema from dist/schema after build
const schemaPath = path.resolve(__dirname, "repo-health.schema.json")
const rawSchema = fs.readFileSync(schemaPath, "utf-8")
const schema = JSON.parse(rawSchema)

const ajv = new Ajv({ allErrors: true, strict: false })
const validate = ajv.compile(schema)


export function validateReport(report: unknown): void {
  const valid = validate(report)

  if (!valid) {
    const errors = (validate.errors as ErrorObject[] | null)
      ?.map((e) => `${e.instancePath || "/"} ${e.message}`)
      .join(", ")

    throw new Error(`Schema validation failed: ${errors}`)
  }
}
