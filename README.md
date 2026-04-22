# ThinkCheck Legal 2.0

> ⚖️ 基于晶脉哲学谐振理论的法律推理质量评估工具
> 🔬 检测概念漂移、逻辑矛盾与论证和谐度

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![GitHub Issues](https://img.shields.io/github/issues/luoxuejian000/-thinkcheck-lib-)](https://github.com/luoxuejian000/-thinkcheck-lib-/issues)
[![GitHub Stars](https://img.shields.io/github/stars/luoxuejian000/-thinkcheck-lib-?style=social)](https://github.com/luoxuejian000/-thinkcheck-lib-)

## 🧠 理论背景

ThinkCheck 基于**晶脉哲学**的谐振理论，核心是量化系统在矛盾中达成动态平衡的能力：

**H = λU·U + λD·D - λA·A**

- **U (统一性)**：概念语义一致性
- **D (发展性)**：新信息引入节奏
- **A (对抗性)**：内部矛盾密度
- **H (和谐度)**：综合推理健康度

这套框架源于一个长期观察：**大多数问题的根源，不是孤立事件，而是关系结构的失衡。**

## ✨ 核心特性

- **四维评估体系**：统一性(U)、发展性(D)、对抗性(A)、和谐度(H)
- **概念漂移检测**：基于语义嵌入，实时识别法律术语的含义偏移
- **可解释性输出**：不只给分数，更定位具体术语、位置和相似度数值
- **可协商权重**：所有权重与阈值均开放配置，适配不同场景的价值偏好
- **轻量级设计**：核心逻辑不依赖商业 LLM API，仅需开源嵌入模型

## 📦 安装

<!---->
> **⚠️ 重要提示：** 当前 `2.0-legal` 分支存在一个已知的工程结构问题（https://github.com/luoxuejian000/-thinkcheck-lib-/issues/1），`pip install` 可能无法正常工作。建议暂时通过源码安装并手动运行。
<!---->

### 从源码安装与运行（当前推荐方式）

<!---->
1.  **克隆仓库并切换到 `2.0-legal` 分支**：
    ```bash
    git clone https://github.com/luoxuejian000/-thinkcheck-lib-.git
    cd -thinkcheck-lib-
    git checkout 2.0-legal
    ```
2.  **安装依赖**：
    ```bash
    pip install numpy scikit-learn sentence-transformers
    ```
3.  **运行评估**：
    进入 `thinkcheck_product` 目录，直接执行 Python 脚本：
    ```bash
    cd thinkcheck_product
    python your_script.py  # 将 your_script.py 替换为您的脚本
    ```
    或在脚本中通过相对路径导入：
    ```python
    import sys
    sys.path.append('..')  # 假设当前在 thinkcheck_product 目录
    from thinkcheck_product.legal_monitor import StandaloneLegalMonitor
    ```
<!---->

### 使用 pip 安装（等待 v2.0.1 修复后）

此功能将在 https://github.com/luoxuejian000/-thinkcheck-lib-/issues/1 修复后可用。

```bash
pip install thinkcheck-legal
```

## 🚀 快速开始

<!---->
> **💡 注意**：由于当前安装问题，以下示例假设您已通过上述“从源码安装”步骤，并在 `thinkcheck_product` 目录或已正确配置 Python 路径。
<!---->

### 1. 在代码中使用评估器

<!---->
```python
# 请确保在正确配置路径后导入
from thinkcheck_product.legal_monitor import StandaloneLegalMonitor
```
<!---->

```python
# 初始化监控器（权重可选，默认使用协商起点）
monitor = StandaloneLegalMonitor()

# 待评估的法律推理文本
text = """
本案涉及善意取得制度。根据《民法典》第三百一十一条，善意取得需满足以下要件：
（一）受让人受让该不动产或者动产时是善意；
（二）以合理的价格转让；
（三）转让的不动产或者动产依照法律规定应当登记的已经登记，不需要登记的已经交付给受让人。
张三在购买时不知李四系无权处分，且支付了市场价，手机已交付。故张三可善意取得该手机。
"""

# 获取和谐度分数
score = monitor.evaluate(text)
report = monitor.get_report()

print(f"和谐度 H = {score:.3f}")
print(f"U(统一性) = {report['U']:.3f}")
print(f"D(发展性) = {report['D']:.3f}")
print(f"A(对抗性) = {report['A']:.3f}")

# 查看漂移警告
for warn in report['drift_warnings']:
    print(f"⚠️ 术语 '{warn['term']}' 一致性={warn['consistency']} (阈值{warn['threshold']})")
```

### 2. 运行内置演示

<!---->
```bash
# 进入核心代码目录
cd thinkcheck_product
# 运行演示脚本
python demo.py
```
<!---->

演示脚本会自动对比“正常法律推理”与“概念漂移推理”的和谐度差异，并输出漂移警告。

## 📊 评估指标说明

| 指标 | 含义 | 计算方式 | 理想范围 |
| :--- | :--- | :--- | :--- |
| **U (统一性)** | 概念语义一致性 | 关键术语在不同上下文中的语义嵌入余弦相似度均值 | 0.7 - 1.0 |
| **D (发展性)** | 新概念引入节奏 | 术语首次出现位置的归一化标准差 | 0.3 - 0.8 |
| **A (对抗性)** | 内在矛盾程度 | 转折词密度 + 预定义矛盾规则匹配 | 0.0 - 0.3 |
| **H (和谐度)** | 综合推理健康度 | `H = λU·U + λD·D - λA·A` | 越高越好 |

## ⚙️ 配置

所有权重、阈值和领域词表均可在 `thinkcheck_product/legal_config.py` 中修改。常用配置项：

<!---->
```python
# 文件路径: thinkcheck_product/legal_config.py
# 和谐度权重（默认来自协商起点）
DEFAULT_LAMBDA_U = 0.4
DEFAULT_LAMBDA_D = 0.4
DEFAULT_LAMBDA_A = 0.2

# 语义漂移检测阈值
U_DRIFT_THRESHOLD = 0.65

# 法律术语词表（可扩展）
LEGAL_TERMS = ["善意取得", "违约责任", "不可抗力", ...]

# 矛盾规则库
CONTRADICTION_RULES = [
    ("善意取得", "明知无权处分"),
    ...
]
```
<!---->

修改后无需重新安装，直接生效。

## ⚠️ 已知问题与改进计划

当前 2.0 版本是一个**概念验证（PoC）**，我们正在积极迭代。以下是已知局限及规划：

| 问题 | 状态 | 计划版本 | 相关 Issue |
| :--- | :--- | :--- | :--- |
| 包结构与导入路径未完全对齐 | 🔴 修复中 | v2.0.1 | https://github.com/luoxuejian000/-thinkcheck-lib-/issues/1 |
| A指标依赖转折词表，可能误伤正常法律论证 | 🟡 调研中 | v2.1.0 | https://github.com/luoxuejian000/-thinkcheck-lib-/issues/2 |
| U/D指标存在启发式偏差，默认值可能偏高 | 🟡 调研中 | v3.0 | https://github.com/luoxuejian000/-thinkcheck-lib-/issues/3 |

欢迎通过 https://github.com/luoxuejian000/-thinkcheck-lib-/issues 提交反馈或参与讨论。

## 🧭 路线图

- **v2.0.1**：修复工程结构，对齐 `setup.py` 与导入路径
- **v2.1.0**：升级 A 指标，引入轻量 NLI 模型减少转折词误伤
- **v3.0.0**：重构为通用谐振评估 SDK，支持多领域预设与 Agent 框架集成

## 🤝 贡献指南

我们欢迎任何形式的贡献！请参阅 CONTRIBUTING.md 了解详情。

## 📄 许可证

本项目采用 LICENSE。

## 🙋 常见问题

**Q: 可以用于非法律文本吗？**  
A: 可以，但需要调整 `thinkcheck_product/legal_config.py` 中的术语词表和矛盾规则。3.0 版本将提供更便捷的跨领域支持。

**Q: 评估分数如何解读？**  
A: 和谐度(H) > 0.7 表示推理过程较为健康；0.5-0.7 可能存在一定问题；<0.5 建议人工复核。具体场景下可通过调整权重校准。

**Q: 为什么选择法律作为首个验证领域？**  
A: 法律文本对概念一致性要求极高，且“概念漂移”是法律 AI 的典型隐蔽缺陷，能最直观地体现谐振评估的价值。

---

📧 联系与反馈：请优先使用 https://github.com/luoxuejian000/-thinkcheck-lib-/issues 提交问题或建议。
```
