# ThinkCheck Agent V7 — 企业级AI文档谐振调谐系统

> 🧠 基于晶脉哲学与谐振理论 | 具备“自我审视”能力的企业级智能体

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![DeepSeek](https://img.shields.io/badge/LLM-DeepSeek-orange.svg)](https://deepseek.com)
[![ThinkCheck](https://img.shields.io/badge/ThinkCheck-3.0-purple.svg)](https://github.com/luoxuejian000/-thinkcheck-lib-)

---

## ✨ V7 版本核心升级

V7 在 V6 的基础上，集成了 **“双脑博弈质疑模块” (Challenge Module)**，这是基于晶脉哲学“矛盾动力论”的工程实现——Agent 内部拥有两个独立的推理视角：一个构建诊断，一个质疑诊断。当两个视角出现显著分歧时，系统自动标记为“高风险逻辑不确定性”。

**这使 ThinkCheck Agent 从一个“评估者”进化为一个能在自己的推理场域中进行“谐振思辨”的反思者。**

---

## 🧠 理论基础：晶脉哲学与谐振理论

ThinkCheck Agent 是基于 **晶脉哲学四重公理** 构建的企业级文档智能调谐系统：

| 公理 | 核心命题 | 工程映射 |
| :--- | :--- | :--- |
| **关系本体论** | 存在即关系，实在即关系网络 | **U（统一性）**：检测概念在关系网络中的语义一致性 |
| **矛盾动力论** | 矛盾是系统演化的内在动力 | **D（发展性）+ A（对抗性）+ 质疑模块**：度量矛盾并利用矛盾驱动思辨 |
| **实践介入论** | 评估者的介入改变被评估系统的状态 | 所有评估附带审计记录，权重可协商，介入痕迹可追溯 |
| **谐振调谐论** | 最优状态是各维度间的动态平衡谐振 | **H = λU·U + λD·D - λA·A**，系统朝向更高和谐度演化 |

---

## 🏗️ 系统架构

```
用户文档
    │
    ▼
┌──────────────────────────────────────────────────────────┐
│              ThinkCheck Agent V7                         │
│                                                          │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐    │
│  │  Document   │   │  Harmony    │   │  Challenge  │    │
│  │  Evaluator  │──▶│  Actuator   │──▶│   Agent     │    │
│  │  (评估器)    │   │  (执行器)    │   │  (质疑模块)  │    │
│  └─────────────┘   └─────────────┘   └─────────────┘    │
│         │                 │                  │            │
│         ▼                 ▼                  ▼            │
│  ┌──────────────────────────────────────────────────┐   │
│  │           OCHR Orchestrator                      │   │
│  │  (评估 → 决策 → 执行 → 质疑 → 验证)               │   │
│  │  + RelationshipMapper + ReflectionCavity         │   │
│  │  + BoundaryController                            │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
    │
    ▼
调谐后的文档 + 审计报告 + 质疑报告
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

### 3. 运行文档评估与调谐

```bash
python main.py --file your_document.md
```

输出示例：
```
评估完成。H=0.623, A=0.350, 判定: 需调谐
调谐完成，策略: 优化术语一致性。
质疑完成。H差异: 0.18, 高风险: False
调谐成功。H: 0.623 → 0.812, 提升: +0.189
```

### 4. 启动 API 服务

```bash
python api.py
```

然后访问 `http://localhost:8000/docs` 查看交互式文档。

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
thinkcheck-agent-v7/
├── main.py                    # 命令行入口
├── api.py                     # REST API 服务 (FastAPI)
├── config.py                  # 配置管理 (pydantic-settings)
├── config.example.yaml        # 配置文件模板
├── requirements.txt           # 依赖清单
├── .env.example               # 环境变量模板
├── thinkcheck_harmony/        # 四维评估引擎
│   ├── __init__.py
│   ├── evaluator.py           # 核心评估器 (支持长文档分块)
│   ├── metrics.py             # U/D/A/H 指标计算
│   └── utils.py               # 文本处理工具
├── ochr/                      # OCHR 治理模块
│   ├── __init__.py
│   ├── relationship_mapper.py # 关系映射分析
│   ├── reflection_cavity.py   # 审计腔 (操作审计)
│   └── boundary.py            # 边界控制器 (敏感内容保护)
├── thinkcheck_agent/          # Agent 核心
│   ├── core/
│   │   ├── evaluator.py       # 文档评估器封装
│   │   ├── actuator.py        # DeepSeek 调谐执行器 (含重试/缓存)
│   │   ├── orchestrator.py    # OCHR 协调器 (评估→决策→执行→质疑→验证)
│   │   └── challenger.py      # 双脑博弈质疑模块 (V7 新增)
│   ├── tools/
│   │   └── file_handler.py    # 文件处理工具
│   └── workflows/
│       └── legal_doc_review.py # 法律文档审阅工作流
├── examples/
│   └── real_world_example.py  # 真实文档示例
├── tests/
│   └── test_harmony_metrics.py # 四维指标单元测试
└── logs/                      # 日志目录
```

---

## 🔗 相关项目

| 项目 | 说明 | 链接 |
| :--- | :--- | :--- |
| **ThinkCheck 3.0 SDK** | 通用谐振评估引擎 | [查看](https://github.com/luoxuejian000/-thinkcheck-lib-/tree/3.0-harmony-sdk) |
| **水晶之心** | Hermes Agent × ThinkCheck 集成版 | [查看](https://github.com/luoxuejian000/hermes-agent) |
| **紫天鹅** | OpenClaw × ThinkCheck MCP 服务 | [查看](https://github.com/luoxuejian000/-Purple-Suan-) |
| **OCHR 集群框架** | 多节点 AI Agent 集群治理 | [查看](https://github.com/luoxuejian000/OCHR) |
| **ThinkCheck Lite** | 零门槛浏览器插件 | [查看](https://github.com/luoxuejian000/thinkcheck-lite) |

---

## 📄 开源许可

本项目遵循 [MIT License](LICENSE)。核心评估理论基于李广好独创的**晶脉哲学与谐振理论**。

---

**🦢 ThinkCheck Agent V7 — 让企业文档在矛盾中谐振，而非在盲从中国化。**
```
