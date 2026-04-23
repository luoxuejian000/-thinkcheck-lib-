# ThinkCheck Harmony 3.0

> ⚖️ 通用谐振评估与调谐 SDK —— 从诊断到干预的完整闭环

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![GitHub issues](https://img.shields.io/github/issues/luoxuejian000/-thinkcheck-lib-)](https://github.com/luoxuejian000/-thinkcheck-lib-/issues)
[![GitHub stars](https://img.shields.io/github/stars/luoxuejian000/-thinkcheck-lib-?style=social)](https://github.com/luoxuejian000/-thinkcheck-lib-)

基于**晶脉哲学**四重公理（关系本体论、矛盾动力论、实践介入论、谐振调谐论）开发的下一代推理质量评估框架。它不仅诊断问题，更通过“矛盾捕获器”生成干预建议，实现从评估到调谐的范式跃迁。

基于**晶脉哲学**四重公理（关系本体论、矛盾动力论、实践介入论、谐振调谐论）开发的下一代推理质量评估框架。它不仅诊断问题，更通过“矛盾捕获器”生成干预建议，实现从评估到调谐的范式跃迁。

## ✨ 核心特性

- **🔍 四维评估体系**：统一性(U)、发展性(D)、对抗性(A)、和谐度(H)
- **📈 概念漂移检测**：基于语义嵌入，实时识别关键术语的含义偏移
- **🛠️ 矛盾捕获器**：从诊断到干预的范式跃迁，内置术语共识工作坊、权重协商会议等调谐微实验
- **⚖️ 可协商权重**：所有权重与阈值均开放配置，适配不同场景的价值偏好
- **🌐 多领域预设**：内置法律、医疗、通用领域词表与规则，可快速扩展
- **📊 三重嵌套报告**：微观（概念级）、中观（段落级）、宏观（价值锚定级）三层透视
- **⚡ 轻量级设计**：核心逻辑不依赖商业 LLM API，仅需开源嵌入模型

## 📦 安装

### 从源码安装（推荐）

```bash
# 克隆仓库并切换到 3.0 分支
git clone https://github.com/luoxuejian000/-thinkcheck-lib-.git
cd -thinkcheck-lib-
git checkout 3.0-harmony-sdk

# 以可编辑模式安装
pip install -e .
```

### 通过 PyPI 安装（待发布）

```bash
# 正式版发布后将支持
# pip install thinkcheck-harmony
```

## 🚀 快速开始

### 1. 基础评估

```python
from thinkcheck_harmony import HarmonyEvaluator

# 初始化评估器（使用法律领域预设，并启用调谐建议）
evaluator = HarmonyEvaluator(domain="legal", enable_suggestions=True)

# 待评估的推理文本
text = """
本案涉及善意取得制度。根据《民法典》第三百一十一条，善意取得需满足善意、合理价格、交付三要件。
张三在购买时不知李四系无权处分，且支付了市场价，手机已交付。故张三可善意取得该手机。
但是，我们必须指出，关于善意的判断存在重大争议。然而，张三的行为是否符合诚实信用原则，有待商榷。
"""

# 获取评估报告
report = evaluator.evaluate(text)

print(f"和谐度 H = {report.H:.3f}")
print(f"U(统一性) = {report.U:.3f}, D(发展性) = {report.D:.3f}, A(对抗性) = {report.A:.3f}")

# 查看语义漂移警告
for warn in report.drift_warnings:
    print(f"⚠️  术语'{warn['term']}' 一致性={warn['consistency']:.3f} (阈值 {warn['threshold']})")

# 查看调谐建议
for suggestion in report.suggestions:
    print(f"💡  {suggestion}")
```

### 2. 运行内置演示

```bash
cd examples
python intervention_demo.py
```

演示脚本会自动评估一段存在概念漂移的法律文本，并输出完整的评估报告与调谐建议。

## 🧠 理论背景

ThinkCheck Harmony 基于**晶脉哲学**的四重公理，将哲学思想工程化为可计算的评估维度：

| 公理 | 核心命题 | 工程映射 |
| :--- | :--- | :--- |
| **关系本体论** | 存在即关系，实在即关系网络。 | `ConceptGraph` 构建概念关系图，评估概念间的一致性。 |
| **矛盾动力论** | 矛盾是系统演进的内在动力，而非需要消除的缺陷。 | `ContradictionDetector` 识别对抗性，`ContradictionHarvester` 将矛盾转化为调谐建议。 |
| **实践介入论** | 评估者的介入本身改变被评估系统的状态。 | 所有评估结果附带 `audit` 字段，记录权重来源与介入历史。 |
| **谐振调谐论** | 最优状态是各维度间的动态平衡谐振。 | 和谐度公式 `H = λU·U + λD·D - λA·A`，权重通过协商确定。 |

这套框架源于一个长期观察：**大多数问题的根源，不是孤立事件，而是关系结构的失衡。**

## 📊 评估指标详解

| 指标 | 含义 | 计算方式 | 理想范围 | 调谐方向 |
| :--- | :--- | :--- | :--- | :--- |
| **U (统一性)** | 概念语义一致性 | 关键术语在不同上下文中的语义嵌入余弦相似度均值 | 0.7 - 1.0 | 过高可能僵化，过低则失焦 |
| **D (发展性)** | 新概念引入节奏 | 术语首次出现位置的归一化标准差 | 0.3 - 0.8 | 过高可能散漫，过低则停滞 |
| **A (对抗性)** | 内在矛盾程度 | 转折词密度 + 预定义矛盾规则匹配 | 0.0 - 0.3 | 适量可激发思考，过量则瓦解论证 |
| **H (和谐度)** | 综合推理健康度 | `H = λU·U + λD·D - λA·A` | 越高越好 | 追求动态平衡 |

## 🛠️ 矛盾捕获器：从诊断到干预

ThinkCheck Harmony 3.0 的核心创新是从“诊断”到“干预”的范式跃迁。内置的**矛盾捕获器 (Contradiction Harvester)** 将检测到的矛盾（高A值、概念漂移）转化为可执行的微实验建议。

### 内置捕获器

| 捕获器 | 触发条件 | 生成的微实验建议 |
| :--- | :--- | :--- |
| **术语共识工作坊** | 检测到关键术语概念漂移 | 提取术语所在的矛盾上下文片段，邀请相关方进行快速标注，形成临时定义共识。 |
| **权重协商会议** | 对抗性(A) 值持续超过阈值 | 召集相关方独立调整 U/D/A 的权重滑块，系统计算“妥协解”，生成新的评估配置。 |

### 自定义捕获器

您可以通过继承 `BaseHarvester` 基类实现自己的矛盾转化逻辑，并注册到评估器中。

```python
from thinkcheck_harmony.intervention.base import BaseHarvester
from thinkcheck_harmony import HarmonyEvaluator

class DevelopmentStimulator(BaseHarvester):
    """当发展性(D)过低时，建议引入外部信息。"""

    def analyze(self, report):
        # 当发展性分数低于0.4时触发
        return report.D < 0.4

    def generate_intervention(self, report):
        return [
            "建议引入一个跨领域类比或反例，以刺激新的信息维度。",
            "可尝试从历史、技术或社会等相邻领域寻找关联概念。"
        ]

    def get_name(self):
        return "发展性刺激器"

# 使用自定义捕获器
evaluator = HarmonyEvaluator(enable_suggestions=True)
evaluator.suggestion_engine.register_harvester(DevelopmentStimulator())
```

## ⚙️ 配置

所有权重、阈值和领域词表均可在初始化时配置，或通过 `thinkcheck_harmony/config.py` 修改默认值。

```python
from thinkcheck_harmony import HarmonyEvaluator, LegalConfig

# 方式1：通过领域预设快速启动
evaluator = HarmonyEvaluator(domain="medical")  # 可选: legal, medical, general

# 方式2：完全自定义配置
custom_config = {
    "weights": {"lambda_u": 0.5, "lambda_d": 0.3, "lambda_a": 0.2},  # 和谐度公式权重
    "thresholds": {"drift": 0.7, "high_A": 0.35, "low_D": 0.3},     # 各类阈值
    "enable_audit_trail": True,  # 是否记录评估过程
    "contradiction_harvesters": ["term_workshop", "weight_negotiation"]  # 启用的捕获器
}

evaluator = HarmonyEvaluator(config=custom_config)
```

## 🧭 版本演进

| 版本 | 里程碑 | 状态 |
| :--- | :--- | :--- |
| v1.0 | 谐振理论原型验证（词汇统计） | ✅ 已归档 |
| v2.0 | 法律场景深度落地（语义嵌入） | ✅ 已发布 |
| v2.0.1 | 工程结构修复与标准 pip 安装支持 | ✅ 最新稳定版 |
| **v3.0** | **通用谐振评估 SDK + 矛盾捕获器** | ✅ **当前版本** |
| v3.1 (规划) | 谐振导航场（权重可能性地图可视化） | 🚧 开发中 |
| v3.2 (规划) | 元规则共鸣器（动态阈值校准） | 📅 已规划 |
| v4.0 (愿景) | 多智能体协作和谐度评估框架 | 🔭 远期愿景 |

详细的路线图请参阅 ROADMAP.md。

## ⚠️ 已知局限与未来计划

我们诚实地记录当前版本的局限，并公开改进方向：

| 问题 | 状态 | 计划版本 | 说明 |
| :--- | :--- | :--- | :--- |
| A指标依赖转折词表，可能误伤正常论证转折 | 🔶 部分优化 | v3.2 | 正在引入上下文感知的对抗性分析。 |
| U/D指标存在启发式偏差，默认阈值可能不适合所有领域 | 🔶 调研中 | v3.2 | 将提供领域自适应校准工具。 |
| 多语言支持目前以中文为主，其他语言效果待验证 | 🔶 实验性支持 | v3.1 | 欢迎贡献其他语言的词表和规则。 |
| 尚未在真实、大规模的多智能体协作场景中充分验证 | 🔶 寻求合作 | v4.0 | 需要真实的复杂协作场景进行压力测试。 |

**欢迎通过 https://github.com/luoxuejian000/-thinkcheck-lib-/issues 提交反馈、报告问题或参与讨论。**

## 🤝 贡献指南

我们坚信，深刻的工具源于广泛的碰撞。欢迎任何形式的贡献：
- **报告错误**：在 Issues 中提交清晰的可复现步骤。
- **提议新功能**：描述使用场景与预期价值。
- **改进文档**：让思想更易被理解。
- **提交代码**：请先阅读 CONTRIBUTING.md 了解开发规范。

## 📄 许可证

本项目采用 LICENSE。

## 🙋 常见问题

**Q: ThinkCheck 与主流的 `LLM-as-judge` 评估方法有何本质区别？**  
**A:** `LLM-as-judge` 本质是“用一个黑盒评估另一个黑盒”，结果不稳定且不可解释。ThinkCheck 基于明确的数学规则（语义嵌入 + 余弦相似度 + 清晰公式）评估推理过程的**关系一致性**，结果是可复现、可解释、可审计的。

**Q: 我应该如何设置 U, D, A 的权重 (λU, λD, λA)？**  
**A:** 默认权重 `(0.4, 0.4, 0.2)` 是一个经过测试的“协商起点”。我们建议：**不要直接修改它，而是运行一次“权重协商会议”微实验**。让相关方独立调整滑块，系统会生成一个代表集体妥协的新配置。这是实践“谐振调谐论”的第一步。

**Q: 可以用于评估非法律文本（如技术方案、商业计划）吗？**  
**A:** 可以。3.0 版本是通用的。使用 `domain="general"` 预设，并通过 `custom_terms` 参数传入你领域的关键术语列表即可。我们正在收集各领域的预设配置，欢迎贡献。

---

**📮 联系与反馈**  
请优先使用 https://github.com/luoxuejian000/-thinkcheck-lib-/issues 进行技术讨论。  
对于更深度的思想交流，可通过项目主页的邮箱联系维护者。

**ThinkCheck Harmony 3.0 —— 让复杂的推理，在矛盾中谐振，而非在混沌中瓦解。**
```
