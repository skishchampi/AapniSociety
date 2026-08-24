import '@testing-library/jest-dom'

// jsdom does not always expose Storage (depends on document origin). Provide a
// minimal in-memory localStorage so token-store code works under test.
if (typeof globalThis.localStorage === 'undefined') {
  class MemoryStorage {
    private store = new Map<string, string>()
    get length() {
      return this.store.size
    }
    clear() {
      this.store.clear()
    }
    getItem(key: string) {
      return this.store.has(key) ? this.store.get(key)! : null
    }
    setItem(key: string, value: string) {
      this.store.set(key, String(value))
    }
    removeItem(key: string) {
      this.store.delete(key)
    }
    key(index: number) {
      return Array.from(this.store.keys())[index] ?? null
    }
  }
  Object.defineProperty(globalThis, 'localStorage', {
    value: new MemoryStorage(),
    writable: true,
  })
}
