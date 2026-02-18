export async function paginate<T>(
  fetchPage: (page: number) => Promise<T[]>
): Promise<T[]> {
  const results: T[] = []
  let page = 1

  while (true) {
    const data = await fetchPage(page)
    if (data.length === 0) break
    results.push(...data)
    page++
  }

  return results
}
