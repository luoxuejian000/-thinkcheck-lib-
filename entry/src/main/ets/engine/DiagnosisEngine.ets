/**
 * ThinkCheck 4.0（竞赛版）核心诊断引擎
 * 理论注入不变，新增分布式协同建议
 */
import { DiagnosisRequest, DiagnosisResult, DomainConfig, HarmonyThresholds, PathologyType } from '../common/Constants';

export class DiagnosisEngine {
  private domainConfig: any
  private weights: { lambda_u: number; lambda_d: number; lambda_a: number }
  private startTime: number = 0

  constructor() {}

  async diagnose(request: DiagnosisRequest): Promise<DiagnosisResult> {
    this.startTime = Date.now()
    this.domainConfig = DomainConfig.getConfig(request.domain)
    this.weights = request.weights

    const paragraphs = this.splitParagraphs(request.text)
    const sentences = this.splitSentences(request.text)

    const U = await this.calculateUnity(paragraphs, request.domain)
    const D = this.calculateDevelopment(sentences)
    const A = this.calculateAdversariality(sentences, paragraphs)

    const H = this.weights.lambda_u * U + this.weights.lambda_d * D - this.weights.lambda_a * A
    const verdict = this.classifyPathology(U, D, A, H)
    const duration = Date.now() - this.startTime

    return {
      U: this.round(U), D: this.round(D), A: this.round(A), H: this.round(H),
      verdict: verdict,
      drift_warnings: [],
      contradictionAlerts: [],
      missingConfrontation: [],
      suggestions: this.generateSuggestions(U, D, A, H, verdict),
      diagnosisDuration: duration,
      hiAIUsed: false,
      securityLevel: 0,
      timestamp: Date.now()
    }
  }

  private splitParagraphs(text: string): string[] {
    return text.split(/\n\s*\n/).filter(p => p.trim().length > 0)
  }

  private splitSentences(text: string): string[] {
    return text.split(/[。！？\n]/).filter(s => s.trim().length > 0)
  }

  private async calculateUnity(paragraphs: string[], domain: string): Promise<number> {
    const keywords = this.domainConfig.keywords as string[]
    if (keywords.length === 0) return 0.8
    const driftScores: number[] = []
    for (const term of keywords) {
      const occurrences: string[] = []
      for (const p of paragraphs) { if (p.includes(term)) occurrences.push(p) }
      if (occurrences.length >= 2) {
        const driftScore = this.detectConceptDrift(term, occurrences)
        driftScores.push(driftScore)
      }
    }
    if (driftScores.length === 0) return 1.0
    const avgDrift = driftScores.reduce((a, b) => a + b, 0) / driftScores.length
    return Math.max(0, 1 - avgDrift / this.domainConfig.driftThreshold)
  }

  private detectConceptDrift(term: string, contexts: string[]): number {
    if (contexts.length < 2) return 0
    const contextFeatures: number[][] = []
    for (const ctx of contexts) {
      const features = this.extractContextFeatures(term, ctx)
      contextFeatures.push(features)
    }
    const dimensionCount = contextFeatures[0].length
    let totalVariance = 0
    for (let d = 0; d < dimensionCount; d++) {
      const values = contextFeatures.map(f => f[d])
      const mean = values.reduce((a, b) => a + b, 0) / values.length
      const variance = values.reduce((sum, v) => sum + Math.pow(v - mean, 2), 0) / values.length
      totalVariance += variance
    }
    return totalVariance / dimensionCount
  }

  private extractContextFeatures(term: string, context: string): number[] {
    const termIndex = context.indexOf(term)
    const windowSize = 20
    const start = Math.max(0, termIndex - windowSize)
    const end = Math.min(context.length, termIndex + term.length + windowSize)
    const window = context.substring(start, end)
    const f1 = window.length / (2 * windowSize + term.length)
    const f2 = termIndex / Math.max(1, context.length)
    const negCount = (window.match(/[不无非否]/g) || []).length
    const f3 = negCount / Math.max(1, window.length)
    const punctCount = (window.match(/[，。！？、；：]/g) || []).length
    const f4 = punctCount / Math.max(1, window.length)
    const before = context.substring(Math.max(0, termIndex - 5), termIndex)
    const f5 = before.length > 0 ? 1 : 0
    const after = context.substring(termIndex + term.length, Math.min(context.length, termIndex + term.length + 10))
    const f6 = after.includes('指') || after.includes('即') || after.includes('是') ? 1 : 0
    return [f1, f2, f3, f4, f5, f6]
  }

  private calculateDevelopment(sentences: string[]): number {
    if (sentences.length <= 1) return 0.1
    let infoGainTotal = 0
    const seenTokens = new Set<string>()
    for (let i = 0; i < sentences.length; i++) {
      const tokens = this.tokenize(sentences[i])
      let newTokens = 0
      for (const token of tokens) { if (!seenTokens.has(token)) { newTokens++; seenTokens.add(token) } }
      const infoGain = tokens.length > 0 ? newTokens / tokens.length : 0
      infoGainTotal += infoGain * (1 + i / sentences.length)
    }
    return Math.min(1, infoGainTotal * 2 / sentences.length)
  }

  private tokenize(sentence: string): string[] {
    const tokens: string[] = []
    const cleaned = sentence.replace(/[，。！？、；：\s]/g, '')
    for (let len = 2; len <= 4; len++) {
      for (let i = 0; i <= cleaned.length - len; i++) {
        tokens.push(cleaned.substring(i, i + len))
      }
    }
    return tokens
  }

  private calculateAdversariality(sentences: string[], paragraphs: string[]): number {
    let contradictionScore = 0
    for (let i = 0; i < sentences.length; i++) {
      for (let j = i + 1; j < sentences.length; j++) {
        if (this.detectExplicitContradiction(sentences[i], sentences[j])) contradictionScore++
      }
    }
    const explicitA = Math.min(1, contradictionScore / Math.max(1, sentences.length))
    const missingConfrontationScore = this.detectMissingConfrontation(paragraphs)
    return (explicitA + missingConfrontationScore) / 2
  }

  private detectExplicitContradiction(a: string, b: string): boolean { /* ...原代码不变... */ return false }
  private extractCore(sentence: string, marker: string): string { /* ...原代码不变... */ return '' }
  private textSimilarity(a: string, b: string): number { /* ...原代码不变... */ return 0 }
  private detectMissingConfrontation(paragraphs: string[]): number { /* ...原代码不变... */ return 0 }

  private classifyPathology(U: number, D: number, A: number, H: number): string {
    if (H >= HarmonyThresholds.RESONANCE) return PathologyType.RESONANCE
    if (U < 0.3 && A > 0.7 && H < 0) return PathologyType.LOGIC_SUICIDE
    if (D < 0.2 && A < 0.3 && H < HarmonyThresholds.SUSPICIOUS) return PathologyType.LOGIC_HOLLOW
    if (H >= HarmonyThresholds.ACCEPTABLE && A < 0.2) return PathologyType.VACATION_PASS
    if (H < HarmonyThresholds.PATHOLOGICAL) return PathologyType.LOGIC_SUICIDE
    return '待进一步诊断'
  }

  private generateSuggestions(U: number, D: number, A: number, H: number, verdict: string): string[] {
    const suggestions: string[] = []
    if (verdict === PathologyType.LOGIC_SUICIDE) {
      suggestions.push('[统一性] 检测到显性逻辑矛盾，请定位矛盾句对并修正（关系本体论介入）')
      suggestions.push('[鸿蒙] 建议使用分布式流转，将诊断报告同步至平板进行深度分析')
    }
    if (verdict === PathologyType.LOGIC_HOLLOW) {
      suggestions.push('[发展性] 信息增量过低，请引入新论据或更深层的分析维度（矛盾动力论：引入外部矛盾刺激演化）')
    }
    if (verdict === PathologyType.VACATION_PASS) {
      suggestions.push('[对抗性] 检测到缺失对抗——论证回避了核心矛盾，请补充相反论点并进行权衡（矛盾动力论）')
      suggestions.push('[鸿蒙] 可将诊断结果添加到桌面服务卡片，持续监控推理健康度')
    }
    if (H < HarmonyThresholds.ACCEPTABLE) {
      suggestions.push('[综合] 整体推理健康度不足，建议重新审视推理链（谐振调谐）')
    }
    if (U < 0.5) {
      suggestions.push('[统一性] 核心术语存在语义漂移风险，请统一关键概念的定义和使用（关系本体论调谐）')
    }
    return suggestions
  }

  private round(value: number): number { return Math.round(value * 1000) / 1000 }
}