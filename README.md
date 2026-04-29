# ThinkCheck 4.0 — 鸿蒙原生AI推理诊断引擎（竞赛版）

🚩 基于晶脉哲学谐振理论，端侧原生实现的AI推理质量评估与调谐系统

2026 HarmonyOS 创新赛·极客赛道 参赛作品

<a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
<a href="https://developer.harmonyos.com"><img src="https://img.shields.io/badge/HarmonyOS-6.0.0-blue.svg" alt="HarmonyOS"></a>
<a href="https://github.com/luoxuejian000/-thinkcheck-lib-"><img src="https://img.shields.io/github/stars/luoxuejian000/-thinkcheck-lib-?style=social" alt="GitHub stars"></a>

## 🧠 理论背景
## 🧠 理论背景

ThinkCheck 基于**晶脉哲学**的四重公理与工程映射：

| 公理 | 核心命题 | 工程映射 |
| :--- | :--- | :--- |
| **关系本体论** | 存在即关系，实在即关系网络。 | **U（统一性）**：检测概念在关系网络中的语义一致性。 |
| **矛盾动力论** | 矛盾是系统演进的内在动力，而非需要消除的缺陷。 | **D（发展性）**：度量新信息引入的节奏；<br>**A（对抗性）**：量化内在矛盾的密度。 |
| **实践介入论** | 评估者介入本身改变了被评估系统的状态。 | 诊断报告透明化，权重可协商，介入痕迹可审计。 |
| **谐振调谐论** | 最优状态是各维度间的动态平衡谐振。 | **H = λU·U + λD·D - λA·A**，权重通过社会协商确定。 |

这套框架源于一个长期观察：**大多数问题的根源，不是孤立事件，而是关系结构的失衡。**

## ✨ 核心特性

-   **四维评估体系**：统一性(U)、发展性(D)、对抗性(A)、和谐度(H)
-   **概念漂移检测**：基于语义嵌入，端侧实时识别术语含义偏移
-   **矛盾捕获器**：从诊断到干预，内置术语共识工作坊、权重协商会议等调谐微实验
-   **可协商权重**：所有权重与阈值均开放配置，适配不同场景的价值偏好
-   **多领域预设**：内置法律、医疗、金融、通用领域词表与规则
-   **鸿蒙原生集成**：HiAI Foundation 端侧推理、MindSpore Lite NPU加速、服务卡片、分布式流转

## 📁 项目结构

```
ThinkCheck4/
├── build-profile.json5           # 项目构建配置
├── entry/
│   ├── src/main/ets/
│   │   ├── common/               # 常量与类型定义
│   │   ├── engine/               # 核心诊断引擎
│   │   │   ├── DiagnosisEngine.ets      # 核心评估逻辑（U/D/A/H计算）
│   │   │   ├── VectorCache.ets          # 端侧向量缓存（LRU淘汰策略）
│   │   │   └── HistoryManager.ets       # 诊断历史与H值趋势追踪
│   │   ├── intervention/         # 矛盾捕获器模块
│   │   │   ├── base.py                  # 捕获器抽象接口
│   │   │   ├── term_alignment.py        # 术语共识工作坊
│   │   │   └── weight_negotiation.py    # 权重协商会议
│   │   ├── pages/               # 应用页面
│   │   │   ├── Index.ets                # 主诊断页面
│   │   │   ├── DiagnosisPage.ets        # 诊断详情页
│   │   │   ├── ReportPage.ets           # 历史对比页
│   │   │   └── SettingsPage.ets         # 权重配置页
│   │   ├── utils/               # 工具类
│   │   ├── presets/             # 领域预设
│   │   └── widget/              # 服务卡片组件
│   └── src/main/resources/      # 资源文件
├── docs/                        # 竞赛文档
│   ├── COMPETITION.md           # 作品介绍
│   └── TEST_REPORT.md           # 测试对比报告
└── README.md                    # 本文档
```

## 🚀 快速开始

### 环境要求
- DevEco Studio 6.0.0+
- HarmonyOS SDK 6.0.0
- 华为账号（用于云端构建）

### 使用云端构建（推荐，绕过本地环境问题）
```bash
# 1. 克隆项目
git clone https://github.com/luoxuejian000/-thinkcheck-lib-.git
cd -thinkcheck-lib-
git checkout thinkcheck-4.0-competition

# 2. 上传到华为云开发环境
# 3. 在云端 DevEco Studio 中打开项目
# 4. 点击 Sync 同步
# 5. Build → Build Hap(s) 生成 HAP 包
```

### 使用本地构建（需要完整鸿蒙开发环境）
```bash
# 1. 克隆项目并切换到 4.0 分支
# 步骤同上
# 2. 使用 DevEco Studio 本地打开项目
# 3. 连接真机或模拟器
# 4. 点击运行
```
