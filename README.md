# ThinkCheck Agent for Enterprise

> 🧠 基于晶脉哲学与谐振理论的企业级 AI 文档智能调谐系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![DeepSeek](https://img.shields.io/badge/LLM-DeepSeek-orange.svg)](https://deepseek.com)
[![ThinkCheck](https://img.shields.io/badge/ThinkCheck-3.0-purple.svg)](https://github.com/luoxuejian000/-thinkcheck-lib-)

---

## ✨ 项目简介

ThinkCheck Agent for Enterprise 是一个基于**晶脉哲学与谐振理论**的企业级文档智能调谐系统。它能够：

- **自动评估**：对文档进行 U/D/A/H 四维和谐度诊断，精准定位概念漂移、逻辑矛盾等隐蔽缺陷
- **智能调谐**：集成 DeepSeek 大模型，根据诊断结果自动修复文档问题，实现从“诊断”到“治疗”的闭环
- **企业集成**：支持 Git 自动化提交、批量处理、详细审计报告等企业级特性
- **多领域预设**：内置法律、医疗、金融等领域的专业术语库和矛盾规则

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

### 3. 放置 ThinkCheck SDK

将 `thinkcheck_harmony` 文件夹（ThinkCheck 3.0 核心引擎）复制到本项目根目录。

### 4. 运行测试

```bash
python main.py --file your_document.md
```

您将看到类似以下输出：

```
评估完成。H=0.623, A=0.350, 判定: 需调谐
调谐完成，策略: 优化术语一致性。
调谐成功。H: 0.623 → 0.812, 提升: +0.189
```

---

## 📊 评估指标说明

| 指标 | 含义 | 健康区间 | 说明 |
| :--- | :--- | :--- | :--- |
| **U (统一性)** | 概念语义一致性 | 0.7 - 1.0 | 关键术语在文中含义是否一致 |
| **D (发展性)** | 论证递进节奏 | 0.3 - 0.8 | 新信息引入的节奏是否合理 |
| **A (对抗性)** | 内在矛盾密度 | 0.0 - 0.3 | 过高则自相矛盾，过低则回避矛盾 |
| **H (和谐度)** | 综合推理健康度 | 越高越好 | H = λU·U + λD·D - λA·A |

---

## 📁 项目结构

```
thinkcheck-agent-v6/
├── main.py                    # 命令行入口
├── config.example.yaml        # 配置文件模板
├── requirements.txt           # 依赖清单
├── thinkcheck_agent/          # 核心模块
│   ├── core/
│   │   ├── evaluator.py       # 文档评估器（ThinkCheck 封装）
│   │   ├── actuator.py        # 调谐执行器（DeepSeek 集成）
│   │   └── orchestration.py   # OCHR 协调器（评估→决策→执行→验证）
│   ├── tools/
│   │   └── file_handler.py    # 文件处理工具
│   └── workflows/
│       └── legal_doc_review.py # 法律文档审阅工作流
└── thinkcheck_harmony/        # ThinkCheck 3.0 SDK（需手动放置）
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
