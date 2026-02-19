import Ajv from "ajv"
import fs from "fs"
import path from "path"
import { fileURLToPath } from "url"

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const schemaPath = path.resolve(
  __dirname,
  "../../schema/repo-health.schema.json"
)

const schema = JSON.parse(fs.readFileSync(schemaPath, "utf-8"))

const ajv = new Ajv({ allErrors: true })

const validate = ajv.compile(schema)

export function validateReport(report: unknown): void {
  const valid = validate(report)

  if (!valid) {
    const errors = validate.errors
      ?.map(e => `${e.instancePath} ${e.message}`)
      .join(", ")

    throw new Error(`Schema validation failed: ${errors}`)
  }
}
