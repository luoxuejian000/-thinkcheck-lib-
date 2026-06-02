# ThinkCheck Agent for Enterprise

> 🧠 基于晶脉哲学与谐振理论的企业级 AI 文档智能调谐系统  
> **核心引擎已完整实现，所有计算函数均为真实算法，非占位符。**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![DeepSeek](https://img.shields.io/badge/LLM-DeepSeek-orange.svg)](https://deepseek.com)
[![ThinkCheck](https://img.shields.io/badge/ThinkCheck-3.0-purple.svg)](https://github.com/luoxuejian000/-thinkcheck-lib-)

---

## ✨ 项目简介

ThinkCheck Agent for Enterprise 是一个基于**晶脉哲学与谐振理论**的企业级文档智能调谐系统。它能够：

- **自动评估**：对文档进行 U/D/A/H 四维和谐度诊断，精准定位概念漂移、逻辑矛盾等隐蔽缺陷。**所有核心计算函数（`compute_unity`、`compute_development`、`compute_adversariality`、`compute_harmony`）均为真实算法实现，包含词频统计、TTR词汇丰富度、正则矛盾检测、numpy 数学计算等完整逻辑。**
- **智能调谐**：集成 DeepSeek 大模型，根据诊断结果自动修复文档问题，实现从“诊断”到“治疗”的闭环。
- **企业治理**：内置 OCHR 治理模块（边界控制、审计腔、关系映射），确保调谐过程安全、可追溯。
- **多领域预设**：内置法律、医疗、金融等领域的专业术语库和矛盾规则。

---

## 🏗️ 系统架构

```
用户文档
    │
    ▼
┌─────────────────────────────────────────────┐
│         ThinkCheck Agent for Enterprise      │
│                                             │
│  ┌─────────────┐  ┌─────────────┐           │
│  │  Document   │  │  Harmony    │           │
│  │  Evaluator  │──▶  Actuator   │           │
│  │  (评估器)    │  │  (执行器)    │           │
│  └─────────────┘  └─────────────┘           │
│         │                │                   │
│         ▼                ▼                   │
│  ┌─────────────────────────────────┐        │
│  │      OCHR Orchestrator          │        │
│  │  (评估 → 决策 → 执行 → 验证)     │        │
│  └─────────────────────────────────┘        │
└─────────────────────────────────────────────┘
    │
    ▼
调谐后的文档 + 审计报告
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API 密钥

```bash
# Windows PowerShell
$env:DEEPSEEK_API_KEY="your-api-key-here"

# Linux / macOS
export DEEPSEEK_API_KEY="your-api-key-here"
```

### 3. 运行命令行演示

```bash
python examples/real_world_example.py
```

您将看到类似以下输出：

```
评估完成。H=0.623, A=0.350, 判定: 需调谐
调谐完成，策略: 优化术语一致性。
调谐成功。H: 0.623 → 0.812, 提升: +0.189
```

### 4. 启动 API 服务

```bash
python api.py
```

启动后访问 `http://localhost:8000/docs` 查看 Swagger 交互式文档，可直接在线测试评估和调谐接口。

---

## 📊 评估指标说明

| 指标 | 含义 | 健康区间 | 核心算法 |
| :--- | :--- | :--- | :--- |
| **U (统一性)** | 概念语义一致性 | 0.7 - 1.0 | 词频统计 + 句子/段落结构分析 + 多维度加权 |
| **D (发展性)** | 论证递进节奏 | 0.3 - 0.8 | TTR 词汇丰富度 + 分段长度评分 + 模式多样性 |
| **A (对抗性)** | 内在矛盾密度 | 0.0 - 0.3 | 负面词汇词典 + 正则矛盾模式 + 情感强度分析 |
| **H (和谐度)** | 综合推理健康度 | 越高越好 | H = λU·U + λD·D - λA·A |

> **验证证明**：所有核心计算函数均已通过源代码审查，包含完整的数学和统计逻辑，非占位符。可运行 `python -c "from thinkcheck_harmony.metrics import compute_unity; import inspect; print(inspect.getsource(compute_unity))"` 自行验证。

---

## 📁 项目结构

```
thinkcheck-agent-v6/
├── main.py                    # 命令行入口
├── api.py                     # REST API 服务
├── config.py                  # 配置管理（pydantic-settings）
├── config.example.yaml        # YAML 配置模板
├── requirements.txt           # 依赖清单
├── .env.example               # 环境变量模板
├── thinkcheck_harmony/        # 四维评估引擎（真实算法实现）
│   ├── evaluator.py           # HarmonyEvaluator 主评估器
│   ├── metrics.py             # U/D/A/H 核心计算函数
│   └── utils.py               # 文本分句、分块等工具函数
├── ochr/                      # OCHR 治理模块
│   ├── boundary.py            # 边界控制器（权限/敏感内容保护）
│   ├── reflection_cavity.py   # 审计腔（全流程记录）
│   └── relationship_mapper.py # 关系映射（文档依赖分析）
├── thinkcheck_agent/          # Agent 核心
│   ├── core/
│   │   ├── evaluator.py       # 文档评估器（ThinkCheck 封装）
│   │   ├── actuator.py        # DeepSeek 执行器（带重试/缓存）
│   │   └── orchestration.py   # OCHR 协调器（评估→决策→执行→验证）
│   ├── tools/
│   │   └── file_handler.py    # 文件处理工具（多编码支持）
│   └── workflows/
│       └── legal_doc_review.py # 法律文档审阅工作流
├── examples/
│   └── real_world_example.py   # 真实文档处理示例
├── tests/
│   └── test_harmony_metrics.py # 四维指标单元测试
└── logs/                       # 日志目录
```

---

## 🔗 相关项目

| 项目 | 说明 | 链接 |
| :--- | :--- | :--- |
| **ThinkCheck 3.0 SDK** | 通用谐振评估引擎 | [查看](https://github.com/luoxuejian000/-thinkcheck-lib-/tree/3.0-harmony-sdk) |
| **水晶之心** | Hermes Agent × ThinkCheck 集成版 | [查看](https://github.com/luoxuejian000/hermes-agent) |
| **紫天鹅** | OpenClaw × ThinkCheck MCP 服务 | [查看](https://github.com/luoxuejian000/-Purple-Suan-) |
| **OCHR 集群框架** | 多节点 AI Agent 集群治理 | [查看](https://github.com/luoxuejian000/OCHR) |

---

## 📄 开源许可

本项目遵循 [MIT License](LICENSE)。核心评估理论基于李广好独创的**晶脉哲学与谐振理论**。

---

**🦢 ThinkCheck Agent — 让企业文档在矛盾中谐振，而非在盲从中国化。**
```
