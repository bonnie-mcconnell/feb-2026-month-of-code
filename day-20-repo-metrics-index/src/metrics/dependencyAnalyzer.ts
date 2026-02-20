export function analyzeDependencies() {
  return {
    external: { count: 0, names: [] },
    internal: { moduleCount: 0, avgImportsPerFile: 0, maxImportsPerFile: 0 }
  }
}