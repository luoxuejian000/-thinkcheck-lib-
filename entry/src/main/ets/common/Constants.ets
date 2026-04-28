/**
 * ThinkCheck 4.0（竞赛版） - 核心常量与类型定义
 *
 * 理论注入：晶脉哲学四公理的边界定义
 * 竞赛增强：新增鸿蒙服务卡片、分布式协同相关常量
 */
export class OpenCapability {
  static readonly HIAI_FOUNDATION = {
    name: 'HiAI Foundation Kit',
    usage: '端侧加载轻量语义嵌入模型，执行概念漂移检测中的余弦相似度计算',
    innovation: '继承3.0概念，HiAI端侧推理，数据不出设备'
  }
  static readonly MINDSPORE_LITE = {
    name: 'MindSpore Lite Kit',
    usage: '端侧语义向量NPU加速',
    innovation: '3.0用NumPy，4.0用MindSpore Lite端侧同精度计算'
  }
  static readonly DATA_SECURITY = {
    name: '数据安全分级（S1-S4）',
    usage: '诊断报告按领域分级存储，跨设备流转自动校验',
    innovation: '3.0无此能力，4.0利用鸿蒙安全架构'
  }
  static readonly DISTRIBUTED_FLOW = {
    name: '分布式数据流转',
    usage: '手机诊断，平板分析，多端协同调谐',
    innovation: '3.0单机运行，4.0鸿蒙分布式协同'
  }
}

export enum DiagnosisDomain {
  LEGAL = 'legal',
  MEDICAL = 'medical',
  FINANCIAL = 'financial',
  GENERAL = 'general'
}

export class DomainConfig {
  static getConfig(domain: string): DomainPreset {
    const presets: Record<string, DomainPreset> = {
      legal: {
        keywords: ['故意', '过失', '善意', '恶意', '合理', '侵权', '违约', '证据', '举证', '判决', '裁定'],
        driftThreshold: 0.15,
        weights: { lambda_u: 0.6, lambda_d: 0.2, lambda_a: 0.2 }
      },
      medical: {
        keywords: ['诊断', '症状', '病因', '治疗', '预后', '并发症', '禁忌', '适应症', '剂量', '副作用'],
        driftThreshold: 0.12,
        weights: { lambda_u: 0.5, lambda_d: 0.3, lambda_a: 0.2 }
      },
      financial: {
        keywords: ['估值', '市盈率', '风险', '收益', '资产', '负债', '现金流', '增长率', '安全边际', '价值投资'],
        driftThreshold: 0.18,
        weights: { lambda_u: 0.3, lambda_d: 0.4, lambda_a: 0.3 }
      },
      general: {
        keywords: [],
        driftThreshold: 0.20,
        weights: { lambda_u: 0.4, lambda_d: 0.3, lambda_a: 0.3 }
      }
    }
    return presets[domain] || presets.general
  }
}

export interface DomainPreset {
  keywords: string[]
  driftThreshold: number
  weights: { lambda_u: number; lambda_d: number; lambda_a: number }
}

export interface DiagnosisResult {
  U: number; D: number; A: number; H: number
  verdict: string
  drift_warnings: Array<{ term: string; consistency: number; paragraphIndices: number[] }>
  contradictionAlerts: Array<{ sentenceA: string; sentenceB: string; conflictType: string }>
  missingConfrontation: Array<{ expected: string; found: string }>
  suggestions: string[]
  diagnosisDuration: number
  hiAIUsed: boolean
  securityLevel: number
  timestamp: number
}

export interface DiagnosisRequest {
  text: string
  domain: string
  weights: { lambda_u: number; lambda_d: number; lambda_a: number }
  incremental?: boolean
  previousVectors?: Map<string, Float32Array>
}

export interface ParagraphVectorCache {
  paragraphIndex: number; vector: Float32Array; timestamp: number; contentHash: string
}

export interface DiagnosisHistoryEntry {
  id: string; timestamp: number; domain: string; H: number; verdict: string; textPreview: string
}

export class HarmonyThresholds {
  static readonly RESONANCE = 0.60
  static readonly ACCEPTABLE = 0.40
  static readonly SUSPICIOUS = 0.20
  static readonly PATHOLOGICAL = 0.00
}

export class PathologyType {
  static readonly LOGIC_SUICIDE = '逻辑自杀'
  static readonly LOGIC_HOLLOW = '逻辑空洞'
  static readonly VACATION_PASS = '度假合格'
  static readonly RESONANCE = '谐振态'
}

// 竞赛新增：服务卡片消息类型
export enum WidgetAction {
  REFRESH = 'refresh',
  SHOW_HISTORY = 'showHistory',
  DISTRIBUTE = 'distribute'
}