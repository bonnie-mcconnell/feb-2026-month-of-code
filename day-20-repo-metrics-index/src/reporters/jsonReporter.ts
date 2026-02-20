export function jsonReporter(data: unknown) {
  console.log(JSON.stringify(data, null, 2))
}