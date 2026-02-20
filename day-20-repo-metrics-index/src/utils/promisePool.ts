export async function promisePool<T>(
  items: T[],
  worker: (item: T) => Promise<void>,
  concurrency: number
) {
  const queue = [...items]
  const workers: Promise<void>[] = []

  for (let i = 0; i < concurrency; i++) {
    workers.push(
      (async function run() {
        while (queue.length) {
          const item = queue.shift()
          if (!item) return
          await worker(item)
        }
      })()
    )
  }

  await Promise.all(workers)
}