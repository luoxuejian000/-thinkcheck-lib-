/**
 * ThinkCheck 4.0 诊断历史管理
 */
import { DiagnosisHistoryEntry, DiagnosisResult } from '../common/Constants';

export class HistoryManager {
  private history: DiagnosisHistoryEntry[] = []
  private maxHistorySize: number = 50

  constructor() {}

  async addEntry(result: DiagnosisResult, textPreview: string): Promise<void> {
    const entry: DiagnosisHistoryEntry = {
      id: `diag_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`,
      timestamp: result.timestamp, domain: '', H: result.H, verdict: result.verdict,
      textPreview: textPreview.substring(0, 50)
    }
    this.history.unshift(entry)
    if (this.history.length > this.maxHistorySize) this.history.pop()
  }

  getHistory(): DiagnosisHistoryEntry[] { return [...this.history] }
  getLatestH(): number | null { return this.history.length > 0 ? this.history[0].H : null }

  getHTrend(): 'improving' | 'declining' | 'stable' | 'insufficient' {
    if (this.history.length < 3) return 'insufficient'
    const recent3 = this.history.slice(0, 3).map(e => e.H)
    const diff = recent3[0] - recent3[recent3.length - 1]
    if (diff > 0.1) return 'improving'
    if (diff < -0.1) return 'declining'
    return 'stable'
  }

  clearHistory(): void { this.history = [] }
}