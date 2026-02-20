export function consoleReporter(index: any) {
  console.log("Files:", index.files.length)
  console.log("Directories:", Object.keys(index.directories).length)
}