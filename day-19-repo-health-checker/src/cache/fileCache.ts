import * as fs from "node:fs"
import * as path from "node:path"

const CACHE_FILE = path.resolve(".repo-health-cache.json")
const TTL_MS = 1000 * 60 * 60 // 1 hour

interface CacheEntry {
  timestamp: number
  data: unknown
}

type CacheStore = Record<string, CacheEntry>

function readCache(): CacheStore {
  if (!fs.existsSync(CACHE_FILE)) {
    return {}
  }

  try {
    const raw = fs.readFileSync(CACHE_FILE, "utf-8")
    return JSON.parse(raw) as CacheStore
  } catch {
    return {}
  }
}

function writeCache(store: CacheStore): void {
  fs.writeFileSync(
    CACHE_FILE,
    JSON.stringify(store, null, 2),
    "utf-8"
  )
}

export function getCached(key: string): unknown | null {
  const store = readCache()
  const entry = store[key]

  if (!entry) return null

  if (Date.now() - entry.timestamp > TTL_MS) {
    delete store[key]
    writeCache(store)
    return null
  }

  return entry.data
}

export function setCache(key: string, data: unknown): void {
  const store = readCache()

  store[key] = {
    timestamp: Date.now(),
    data
  }

  writeCache(store)
}
