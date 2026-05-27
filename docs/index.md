# ThinkCheck 3.0 — 给你的AI推理做个"逻辑CT"

> **一个通用谐振评估与调谐SDK**，不评判AI答案"对不对"，只诊断它的"推理过程是否健康"。

## 🚀 30秒快速体验

```bash
pip install https://github.com/luoxuejian000/-thinkcheck-lib-/releases/download/v3.0.0/thinkcheck-harmony-3.0.0.tar.gz
```

```python
from thinkcheck_harmony import HarmonyEvaluator

evaluator = HarmonyEvaluator(domain="legal")
report = evaluator.evaluate("你的AI生成的文本")
print(f"H(和谐度) = {report.H:.3f}")
```

## 📊 它能做什么？

- **四维诊断**：统一性(U)、发展性(D)、对抗性(A)、和谐度(H)
- **概念漂移检测**：精准定位术语含义偏移
- **矛盾捕获器**：从诊断到干预的完整闭环
- **多领域预设**：内置法律、医疗、金融等场景的权重与术语库
- **可协商权重**：所有评估参数开放配置，适配你的价值偏好

## 🧠 理论基础

ThinkCheck 基于**晶脉哲学与谐振理论**，将AI推理过程建模为动态关系场域中的自组织调谐过程。

- 📖 `https://osf.io/2zwtk/`
- 💻 `https://github.com/luoxuejian000/-thinkcheck-lib-/tree/3.0-harmony-sdk`
- 📦 `https://github.com/luoxuejian000/-thinkcheck-lib-/releases/tag/v3.0.0`