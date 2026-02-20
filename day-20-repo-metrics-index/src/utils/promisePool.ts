export async function promisePool<T>(
  items: T[],
  worker: (item: T) => Promise<void>,
  concurrency: number
) {
  const executing: Promise<void>[] = []
  let index = 0

  async function enqueue() {
    if (index >= items.length) return

    const item = items[index++]

    const p = worker(item)
      .catch((err) => {
        console.error("Worker error:", err)
      })
      .then(() => {
        executing.splice(executing.indexOf(p), 1)
      })

    executing.push(p)

    if (executing.length >= concurrency) {
      await Promise.race(executing)
    }

    return enqueue()
  }

  await enqueue()
  await Promise.all(executing)
}