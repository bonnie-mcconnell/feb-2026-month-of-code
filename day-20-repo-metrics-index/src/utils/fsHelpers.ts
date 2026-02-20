import path from "node:path"

export function hasAllowedExtension(
  filePath: string,
  extensions: string[] | null
): boolean {
  if (!extensions) return true

  const ext = path.extname(filePath)
  return extensions.includes(ext)
}