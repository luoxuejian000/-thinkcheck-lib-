````markdown
# ThinkCheck Legal 2.0

基于晶脉哲学与谐振理论的法律推理质量评估工具。

## 核心理念

法律推理的质量不在于结论的"正确性"，而在于推理过程的"和谐度"。
本工具通过计算统一性(U)、发展性(D)、对抗性(A)三个维度，量化评估法律文本中
概念的语义一致性、论证的展开节奏以及内在矛盾程度。

## 快速开始

### 安装依赖
```bash
pip install sentence-transformers scikit-learn
````

### 基本使用

```python
from thinkcheck_legal import StandaloneLegalMonitor

monitor = StandaloneLegalMonitor()
text = "你的法律推理文本..."
score = monitor.evaluate(text)
report = monitor.get_report()

print(f"和谐度: {score}")
print(f"U={report['U']}, D={report['D']}, A={report['A']}")
for warn in report['drift_warnings']:
    print(f"警告: 术语'{warn['term']}'一致性低至{warn['consistency']}")
```

## 运行演示

```bash
cd thinkcheck_legal
python demo.py
```

## 理论背景

本工具是"晶脉哲学"与"谐振理论"的工程实现。详见：

- 公理1 关系本体论：检测概念在关系网络中的一致性
- 公理2 矛盾动力论：识别对抗性，作为系统调谐的动力
- 公理3 实践介入论：监控器介入推理过程，改变评估场域
- 公理4 谐振调谐论：和谐度函数引导系统向更优状态演化

```
```

