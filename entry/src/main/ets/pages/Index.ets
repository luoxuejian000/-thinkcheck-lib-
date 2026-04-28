// 竞赛增强：展示鸿蒙端侧AI状态、服务卡片入口、分布式流转提示
import { HIAIEngine } from '../utils/HiAIUtils';
import { RestDiagnosisService } from '../utils/HttpUtils';
import { SecurityLabelManager } from '../utils/SecurityUtils';
import { DiagnosisEngine } from '../engine/DiagnosisEngine';
import { HistoryManager } from '../engine/HistoryManager';
import { DiagnosisResult, DiagnosisDomain, DomainConfig, DiagnosisHistoryEntry } from '../common/Constants';
import { AlertDialog } from '@kit.ArkUI';

@Entry
@Component
struct Index {
  @State inputText: string = ''
  @State diagnosisStatus: string = '就绪，输入AI推理文本后点击诊断'
  @State hScore: number = 0; @State uScore: number = 0; @State dScore: number = 0; @State aScore: number = 0
  @State verdict: string = ''
  @State driftAlerts: Array<{ term: string; consistency: number; paragraphIndices: number[] }> = []
  @State suggestions: string[] = []
  @State selectedDomain: string = 'legal'
  @State isHiAIAvailable: boolean = false
  @State diagnosisDuration: number = 0
  @State historyList: DiagnosisHistoryEntry[] = []
  @State hTrend: string = ''

  private hiaiEngine: HIAIEngine = new HIAIEngine()
  private diagnosisEngine: DiagnosisEngine = new DiagnosisEngine()
  private historyManager: HistoryManager = new HistoryManager()

  async aboutToAppear(): Promise<void> {
    this.isHiAIAvailable = await this.hiaiEngine.initialize()
    this.historyList = this.historyManager.getHistory()
    const trend = this.historyManager.getHTrend()
    if (trend === 'improving') this.hTrend = '↑ 推理质量持续改善'
    else if (trend === 'declining') this.hTrend = '↓ 推理质量下降中'
    else if (trend === 'stable') this.hTrend = '→ 推理质量稳定'
  }

  async runDiagnosis(): Promise<void> {
    if (this.inputText.trim() === '') { this.diagnosisStatus = '请输入待诊断的AI推理文本'; return }
    this.diagnosisStatus = '诊断中...'
    this.hScore = 0; this.uScore = 0; this.dScore = 0; this.aScore = 0; this.verdict = ''; this.driftAlerts = []; this.suggestions = []; this.diagnosisDuration = 0
    try {
      const config = DomainConfig.getConfig(this.selectedDomain)
      const result: DiagnosisResult = await this.diagnosisEngine.diagnose({
        text: this.inputText, domain: this.selectedDomain, weights: config.weights
      })
      this.hScore = result.H; this.uScore = result.U; this.dScore = result.D; this.aScore = result.A
      this.verdict = result.verdict; this.driftAlerts = result.drift_warnings; this.suggestions = result.suggestions
      this.diagnosisDuration = result.diagnosisDuration
      this.diagnosisStatus = `诊断完成：${result.verdict}（耗时${result.diagnosisDuration}ms）`
      await this.historyManager.addEntry(result, this.inputText)
      this.historyList = this.historyManager.getHistory()
      await SecurityLabelManager.setDiagnosisSecurityLevel('/data/storage/el2/base/files/last_diagnosis.json', this.selectedDomain)
    } catch (err) {
      this.diagnosisStatus = '端侧诊断失败，尝试云端后备...'
      try {
        const config = DomainConfig.getConfig(this.selectedDomain)
        const result = await RestDiagnosisService.diagnose({ text: this.inputText, domain: this.selectedDomain, weights: config.weights })
        this.hScore = result.H; this.uScore = result.U; this.dScore = result.D; this.aScore = result.A
        this.verdict = result.verdict; this.driftAlerts = result.drift_warnings; this.suggestions = result.suggestions
        this.diagnosisDuration = result.diagnosisDuration
        this.diagnosisStatus = `云端诊断完成：${result.verdict}`
      } catch (cloudErr) { this.diagnosisStatus = '诊断失败，请检查网络连接' }
    }
  }

  build() {
    Column({ space: 10 }) {
      Text('ThinkCheck 4.0（竞赛版）').fontSize(24).fontWeight(FontWeight.Bold).margin({ top: 20 })
      Text('晶脉谐振 · AI推理诊断引擎').fontSize(13).fontColor('#888888')

      Row() {
        Text(this.isHiAIAvailable ? '🟢 HiAI端侧就绪' : '🟡 CPU模式运行').fontSize(11)
        if (this.hTrend !== '') Text(this.hTrend).fontSize(11).fontColor('#007AFF').margin({ left: 12 })
      }.width('100%')

      Row({ space: 6 }) {
        Button('法律').fontSize(12).onClick(() => { this.selectedDomain = DiagnosisDomain.LEGAL })
        Button('医疗').fontSize(12).onClick(() => { this.selectedDomain = DiagnosisDomain.MEDICAL })
        Button('金融').fontSize(12).onClick(() => { this.selectedDomain = DiagnosisDomain.FINANCIAL })
        Button('通用').fontSize(12).onClick(() => { this.selectedDomain = DiagnosisDomain.GENERAL })
      }.width('100%').justifyContent(FlexAlign.SpaceEvenly)

      TextArea({ placeholder: '请粘贴 AI 生成的推理文本' }).height(120).onChange((value: string) => { this.inputText = value })

      Row({ space: 10 }) {
        Button('🔍 一键诊断').fontSize(16).backgroundColor('#007AFF').width('60%').onClick(() => { this.runDiagnosis() })
        Button('📌 添加到桌面').fontSize(12).width('30%').onClick(() => {
          AlertDialog.show({ message: '长按应用图标，选择“服务卡片”即可添加推理健康度卡片到桌面' })
        })
      }.width('100%').justifyContent(FlexAlign.Center)

      Text(this.diagnosisStatus).fontSize(13).margin({ top: 6 })

      if (this.hScore !== 0) {
        Column() {
          Row() {
            Text(`U=${this.uScore.toFixed(2)}`).fontSize(13).width('25%')
            Text(`D=${this.dScore.toFixed(2)}`).fontSize(13).width('25%')
            Text(`A=${this.aScore.toFixed(2)}`).fontSize(13).width('25%')
            Text(`H=${this.hScore.toFixed(2)}`).fontSize(16).fontColor(this.hScore > 0.4 ? '#34C759' : '#FF3B30').width('25%')
          }
          Text(`判定：${this.verdict}`).fontSize(14).fontColor('#FF9500').margin({ top: 4 })
        }.margin({ top: 6 })
      }

      Scroll() {
        Column({ space: 6 }) {
          if (this.driftAlerts.length > 0) {
            Text('⚠️ 概念漂移警报').fontSize(13).fontColor('#FF9500')
            ForEach(this.driftAlerts, (alert) => {
              Text(`  ${alert.term}: 一致性${alert.consistency.toFixed(2)}`).fontSize(11).fontColor('#FF3B30')
            })
          }
          if (this.suggestions.length > 0) {
            Text('💡 调谐建议（含鸿蒙能力推荐）').fontSize(13).fontColor('#34C759')
            ForEach(this.suggestions, (s) => {
              Text('  • ' + s).fontSize(11).padding({ left: 6 })
            })
          }
        }
      }.height(120).margin({ top: 6 })

      if (this.historyList.length > 0) {
        Button(`📋 历史 (${this.historyList.length}条)  >`).fontSize(12).width('80%')
      }

      Text('HiAI Foundation · MindSpore Lite · 服务卡片 · 分布式流转').fontSize(9).fontColor('#AAAAAA').margin({ top: 8, bottom: 8 })
    }.padding(16).width('100%').height('100%')
  }
}