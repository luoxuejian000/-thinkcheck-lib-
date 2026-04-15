# ThinkCheck-lib 🔄

谐振理论LLM推理监控框架 - 自动检测AI推理质量下降并触发回溯

![Python Version](https://img.shields.io/badge/python-3.7+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![GitHub Issues](https://img.shields.io/github/issues/luoxuejian000/thinkcheck-lib)
![GitHub Stars](https://img.shields.io/github/stars/luoxuejian000/thinkcheck-lib)

## ✨ 特性
- 实时监控LLM推理和谐度
- 自动检测推理质量下降
- 智能触发回溯机制
- 轻量级Python库，易于集成
- 支持主流AI模型接口
- 基于谐振理论的创新算法

## 🚀 快速开始

### 安装
bash
直接从GitHub安装

pip install git+https://github.com/luoxuejian000/thinkcheck-lib.git


### 基本使用
python
from thinkcheck import thinkcheck

@thinkcheck(h_threshold=0.4, max_backtracks=2)
def your_ai_function(prompt):
    # 您的AI调用代码
    response = call_your_llm(prompt)
    return response


## 📖 详细使用

### 1. 装饰器模式
python
from thinkcheck import thinkcheck_retry

@thinkcheck_retry(h_threshold=0.5, max_backtracks=3)
def generate_code(task_description):
    # 您的代码生成逻辑
    return generated_code


### 2. 手动监控模式
python
from thinkcheck import HarmonicMonitor

创建监控器

monitor = HarmonicMonitor(h_threshold=0.3, verbose=True)

监控推理步骤

h_score, needs_backtrack = monitor.add_step("第一步推理")
if needs_backtrack:
    print("⚠️ 推理质量下降，建议调整策略")


## 📁 项目结构

thinkcheck-lib/
├── thinkcheck/          # 核心库
│   ├── __init__.py
│   ├── core.py         # 谐振理论核心算法
│   └── decorator.py    # 装饰器实现
├── examples/           # 使用示例
│   └── basic_usage.py
├── tests/              # 测试文件
├── README.md           # 本文档
├── LICENSE             # MIT许可证
└── pyproject.toml      # 项目配置


## 🔧 配置选项

### thinkcheck装饰器参数
- `h_threshold`: 和谐度阈值 (默认: 0.3)
- `max_backtracks`: 最大回溯次数 (默认: 2)
- `backtrack_strategy`: 回溯策略 (默认: "simple")
- `verbose`: 显示详细信息 (默认: True)

### HarmonicMonitor类参数
- `h_threshold`: 和谐度阈值 (默认: 0.3)
- `max_history`: 最大历史记录数 (默认: 20)
- `verbose`: 是否显示详细信息 (默认: True)

## 🤝 贡献指南

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细指南。

1. **报告问题**：在GitHub Issues中创建新issue
2. **提交代码**：
   bash
   # Fork项目
   # 创建特性分支
   git checkout -b feature/AmazingFeature
   # 提交更改
   git commit -m 'Add some AmazingFeature'
   # 推送到分支
   git push origin feature/AmazingFeature
   # 创建Pull Request


## 📄 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件。

## 💖 支持这个项目

如果您觉得ThinkCheck对您有帮助：

- ⭐ **Star这个仓库** - 这是对我们最大的支持！
- 🔧 **报告问题** - 帮助我们改进
- 📢 **分享给朋友** - 让更多人受益
- 💬 **加入讨论** - 分享您的使用场景

## 📞 联系我们

- **GitHub Issues**: [问题讨论](https://github.com/luoxuejian000/thinkcheck-lib/issues)
- **项目主页**: [https://github.com/luoxuejian000/thinkcheck-lib](https://github.com/luoxuejian000/thinkcheck-lib)

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和用户！

---
*谐振理论让AI推理更可靠，ThinkCheck让质量监控更简单* 🚀
