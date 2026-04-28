/**
 * ThinkCheck 4.0 端侧向量缓存管理
 */
import { ParagraphVectorCache } from '../common/Constants';

export class VectorCacheManager {
  private cache: Map<number, ParagraphVectorCache> = new Map()
  private maxCacheSize: number = 100

  constructor() {}

  getVector(paragraphIndex: number, contentHash: string): Float32Array | null {
    const entry = this.cache.get(paragraphIndex)
    if (entry && entry.contentHash === contentHash) {
      console.info(`[ThinkCheck4] 向量缓存命中，段落${paragraphIndex}`)
      return entry.vector
    }
    return null
  }

  setVector(paragraphIndex: number, vector: Float32Array, contentHash: string): void {
    if (this.cache.size >= this.maxCacheSize) { this.evictOldest() }
    this.cache.set(paragraphIndex, {
      paragraphIndex: paragraphIndex, vector: vector, timestamp: Date.now(), contentHash: contentHash
    })
  }

  invalidate(paragraphIndex: number): void { this.cache.delete(paragraphIndex) }
  clear(): void { this.cache.clear() }
  getCacheSize(): number { return this.cache.size }

  private evictOldest(): void {
    let oldestIndex = -1, oldestTime = Infinity
    for (const [idx, entry] of this.cache) {
      if (entry.timestamp < oldestTime) { oldestTime = entry.timestamp; oldestIndex = idx }
    }
    if (oldestIndex >= 0) this.cache.delete(oldestIndex)
  }
}