# ThinkCheck 🔄

谐振理论推理监控库 - 让AI推理不再钻牛角尖

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-43%20passed-brightgreen)](tests/)

---

## 📋 目录

- [什么是ThinkCheck？](#什么是thinkcheck)
- [核心特性](#核心特性)
- [安装](#安装)
- [快速开始](#快速开始)
- [核心概念](#核心概念)
- [配置选项](#配置选项)
- [应用场景](#应用场景)
- [测试与验证](#测试与验证)
- [版本更新](#版本更新)

---

## 什么是ThinkCheck？

ThinkCheck是一个基于谐振理论的Python库，专门用于监控和优化大语言模型(LLM)的推理过程。它能自动检测推理质量下降，并在AI"钻牛角尖"时触发智能回溯。

---

## 核心特性

### 核心功能
✨ **实时监控** - 自动监控推理每一步的质量
⚡ **和谐度计算** - 基于U(新颖性)、D(探索性)、A(对抗性)的量化评分
🔄 **智能回溯** - 质量下降时自动触发回溯机制
🎯 **可配置策略** - 支持多种回溯和监控策略
📊 **详细分析** - 提供完整的推理过程分析报告

### 新增功能 (v2.1.0+)
🌐 **多语言支持** - 中文、英文、日文、韩文否定词检测
⚙️ **可配置触发** - 支持连续低H值才触发，避免误判
📊 **增强的摘要** - 完整的推理质量统计
📝 **标记回溯** - 每步记录是否触发回溯
🏷️ **语言特定分词** - 针对不同语言优化的预处理

---

## 安装

### 从本地安装

```bash
cd thinkcheck_product
pip install -e .
```

---

## 快速开始

### 方法1：使用装饰器（最简单）

```python
from thinkcheck import thinkcheck

@thinkcheck(h_threshold=0.4, max_backtracks=2, language='zh')
def your_ai_function(prompt: str) -> str:
    # 这里调用你的LLM
    response = call_llm(prompt)
    return response

# 正常使用，内部自动监控
result = your_ai_function("解释量子力学")
```

### 方法2：直接使用监控器

```python
from thinkcheck import HarmonicMonitor

# 创建监控器 (支持多语言)
monitor = HarmonicMonitor(
    h_threshold=0.3,
    verbose=True,
    language='zh',  # 可选: 'zh', 'en', 'ja', 'ko'
    consecutive_low_threshold=2  # 连续2次低H才触发
)

# 监控推理步骤
steps = ["第一步分析", "第二步推理", "第三步总结"]
for step in steps:
    h_score, needs_backtrack = monitor.add_step(step)
    if needs_backtrack:
        print("⚠️ 推理质量下降，建议调整思路")
        # 你的回溯逻辑

# 获取摘要报告
summary = monitor.get_summary()
print(f"总步数: {summary['total_steps']}")
print(f"平均H值: {summary['average_h']:.2f}")
print(f"触发回溯: {summary['backtrack_triggers']} 次")
```

### 方法3：使用重试策略

```python
from thinkcheck import thinkcheck_retry

@thinkcheck_retry(h_threshold=0.5, max_backtracks=3, language='en')
def reliable_ai(prompt: str) -> str:
    # 你的AI函数
    return ai_response

# 自动重试直到质量达标
result = reliable_ai("复杂问题")
```

---

## 核心概念

### 和谐度(H-score)

ThinkCheck通过计算和谐度来评估推理质量：

```
H = 0.4*U + 0.4*D - 0.2*A
```

- **U (Novelty 新颖性)**：新信息的比例
- **D (Exploration 探索性)**：与历史推理的差异度
- **A (Adversity 对抗性)**：重复和矛盾的程度

和谐度范围0-1，越高表示推理质量越好。

### 回溯策略

当和谐度低于阈值时，ThinkCheck提供多种回溯策略：

1. **简单回溯**：返回上一步结果
2. **重试回溯**：使用调整后的参数重新调用
3. **混合回溯**：结合多种策略

---

## 配置选项

### thinkcheck装饰器参数

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `h_threshold` | float | 0.3 | 和谐度阈值 |
| `max_backtracks` | int | 2 | 最大回溯次数 |
| `backtrack_strategy` | str | "simple" | 回溯策略 |
| `verbose` | bool | True | 显示详细信息 |
| `language` | str | "zh" | 语言 (zh/en/ja/ko) |
| `consecutive_low_threshold` | int | 1 | 连续低H触发次数 |

### HarmonicMonitor类参数

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `h_threshold` | float | 0.3 | 和谐度阈值 |
| `lookback_window` | int | 3 | 回溯窗口大小 |
| `verbose` | bool | True | 是否显示详细信息 |
| `language` | str | "zh" | 语言 (zh/en/ja/ko) |
| `consecutive_low_threshold` | int | 1 | 连续低H触发次数 |

---

## 应用场景

### 1. AI助手优化

```python
@thinkcheck(h_threshold=0.4)
def smart_assistant(question: str) -> str:
    # 你的AI助手逻辑
    return assistant_response
```

### 2. 代码生成质量监控

```python
@thinkcheck_retry(h_threshold=0.5, max_backtracks=3)
def code_generator(requirements: str) -> str:
    # 代码生成逻辑
    return generated_code
```

### 3. 学术研究分析

```python
# 研究AI推理行为
monitor = HarmonicMonitor()
```

---

## 测试与验证

### 运行单元测试

```bash
python -m pytest tests/test_core.py -v
python -m pytest tests/test_decorator.py -v
python -m pytest tests/ -v
```

### 运行真实功能测试

查看项目根目录的 `real_functionality_test.py` 文件。

### 测试覆盖

- ✅ 核心模块 (22个测试)
- ✅ 装饰器模块 (21个测试)
- ✅ 总计 43个测试，全部通过

---

## 版本更新

### v2.1.0 - 多语言与智能触发
- ✅ 新增多语言否定词检测 (中文、英文、日文、韩文)
- ✅ 新增 `consecutive_low_threshold` 配置项
- ✅ 新增 `language` 参数
- ✅ 新增 `ReasoningStep.is_backtrack_trigger` 字段
- ✅ 新增 `improved.py` 完全重写的改进版本
- ✅ 新增 `improved_example.py` 新功能示例
- ✅ 增强 `get_summary()` 返回数据
- ✅ 优化重复检测逻辑 (重复3次以上才算)
- ✅ 优化否定词权重
- 🐛 修复 `basic_usage.py` 导入路径问题

### v2.0.1 - 包结构修复
- ✅ 修复包结构与导入路径
- ✅ 增强测试覆盖
- ✅ 完善示例代码

---

## 性能考虑

ThinkCheck设计为轻量级：
- 和谐度计算复杂度: O(n)，n为历史长度
- 内存使用: 可配置历史窗口大小
- 回溯开销: 取决于策略，通常很小

---

## 贡献指南

欢迎贡献！请查看[CONTRIBUTING.md](CONTRIBUTING.md)。

---

## 许可证

MIT License - 详见[LICENSE](LICENSE)文件。

---

*谐振理论让AI推理更可靠，ThinkCheck让质量监控更简单* 🚀
