import { hiAIFoundation } from '@kit.AIFoundationKit';

export class HIAIEngine {
  private modelHandle: number = -1
  private isAvailable: boolean = false
  private initAttempted: boolean = false

  async initialize(): Promise<boolean> {
    if (this.initAttempted) return this.isAvailable
    this.initAttempted = true
    try {
      this.modelHandle = await hiAIFoundation.loadModel({
        modelPath: '/data/storage/el2/base/haps/entry/files/thinkcheck_embedding_v4.model',
        modelType: 'ONNX', backend: 'NPU_PREFERRED'
      })
      this.isAvailable = true
      console.info('[ThinkCheck4] HiAI模型加载成功')
      return true
    } catch (err) {
      console.warn('[ThinkCheck4] HiAI不可用，降级CPU计算')
      this.isAvailable = false
      return false
    }
  }

  async computeSimilarity(embedA: Float32Array, embedB: Float32Array): Promise<number> {
    if (!this.isAvailable) return this.computeSimilarityCPU(embedA, embedB)
    try {
      const input = new Float32Array([...embedA, ...embedB])
      const result = await hiAIFoundation.runModel(this.modelHandle, input)
      return this.cosineSimilarity(result.slice(0, 384), result.slice(384, 768))
    } catch (err) { return this.computeSimilarityCPU(embedA, embedB) }
  }

  computeSimilarityCPU(embedA: Float32Array, embedB: Float32Array): number {
    return this.cosineSimilarity(embedA, embedB)
  }

  private cosineSimilarity(a: Float32Array, b: Float32Array): number {
    let dot = 0, normA = 0, normB = 0
    for (let i = 0; i < a.length; i++) {
      dot += a[i] * b[i]; normA += a[i] * a[i]; normB += b[i] * b[i]
    }
    const denominator = Math.sqrt(normA) * Math.sqrt(normB)
    return denominator > 0 ? dot / denominator : 0
  }

  getAvailability(): boolean { return this.isAvailable }
}