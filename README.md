# ThinkCheck Agent v8 —— 谐振评估引擎

基于**晶脉哲学四重公理**构建的 AI 推理质量评估引擎。通过 U/D/A/H 四维量化模型，对文本进行深层语义诊断——检测概念漂移、逻辑矛盾、论证质量，并提供可操作的调谐建议。

## 核心函数

**H = λᵤ·U + λᴅ·D - λₐ·A**

| 维度 | 含义 | 哲学对应 | 计算方式 |
|------|------|---------|---------|
| U (统一性) | 语义一致性、概念在场强度 | 关系本体论 | 同术语一致性 + 跨术语一致性 |
| D (发展性) | 新信息价值、逻辑流动的连续性 | 谐振调谐论 | 真伪创新区分 + 分布均匀性 |
| A (对抗性) | 矛盾张力、关系网络中的冲突强度 | 矛盾动力论 | 语义对立检测 + 词汇矛盾 + 跨块追踪 |
| H (和谐度) | 整体推理质量 | 四重公理统一 | λᵤ·U + λᴅ·D - λₐ·A |

## 架构

```
thinkcheck-agent-v8/
├── api.py                        # FastAPI 服务入口
├── config.py                     # 可配置权重与阈值
├── thinkcheck_agent/
│   └── core/
│       ├── evaluator.py          # 核心评估器
│       ├── long_text.py          # 长文本分块与跨块矛盾追踪
│       ├── concepts.py           # 概念图构建
│       └── contradictions.py     # 矛盾检测
├── thinkcheck_harmony/
│   ├── evaluator.py              # 和谐度评估器（可配置权重）
│   └── metrics.py                # U/D/A/H 核心计算
└── examples/
    └── quickstart.py             # 快速开始
```

## 关键特性

- **四维量化评估**：U/D/A/H 连续值，不是二值判断
- **语义矛盾检测**：基于句子嵌入的向量对立检测，不依赖否定词词库
- **长文本支持**：分块处理 + 跨块矛盾追踪，支持多轮对话
- **可配置权重**：λ 权重通过配置文件设置，支持运行时动态调整
- **全链路审计**：权重来源和修改历史可追溯
- **完全本地运行**：评估过程不调用任何外部 API，数据不出本机
- **优雅降级**：语义模型不可用时自动回退到基础逻辑

## 快速开始

```bash
pip install -r requirements.txt
python api.py
```

服务启动后访问 `http://localhost:8000/docs` 查看完整 API 文档。

### 评估文本

```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{"document": "要评估的文本内容", "domain": "general"}'
```

### 返回示例

```json
{
  "h": 0.42,
  "u": 0.75,
  "d": 0.76,
  "a": 0.35,
  "pathology": "需调谐",
  "suggestions": ["检测到语义矛盾，建议检查论证一致性"],
  "warnings": ["概念漂移风险"]
}
```

## 权重配置

在 `config.py` 中修改 λ 权重：

```python
LAMBDA_U = 0.4  # 统一性权重
LAMBDA_D = 0.4  # 发展性权重
LAMBDA_A = 0.2  # 对抗性权重
SEMANTIC_CONTRADICTION_THRESHOLD = -0.2  # 语义矛盾阈值
```

不同领域的推荐权重：

| 领域 | λ_U | λ_D | λ_A | 说明 |
|------|-----|-----|-----|------|
| 法律 | 0.6 | 0.2 | 0.2 | 高度强调概念一致性 |
| 金融 | 0.3 | 0.4 | 0.3 | 鼓励创新，关注风险 |
| 通用 | 0.4 | 0.4 | 0.2 | 平衡设置 |

## 升级记录 (v8)

1. **A 模块重构**：从否定词正则匹配升级为语义向量对立检测 + 共现约束
2. **U 增强**：新增跨术语一致性检测
3. **D 增强**：新增真伪创新区分
4. **H 审计**：λ 权重完全可配置
5. **长文本支持**：分块处理 + 跨块矛盾追踪 + 长句拆分编码

## 理论根基

ThinkCheck 建立在晶脉哲学的四重公理之上：

- **关系本体论**：意义在关系网络中被定义
- **矛盾动力论**：矛盾是系统演化的能量源
- **谐振调谐论**：系统朝向更高和谐度自组织
- **实践介入论**：每次评估都是对语义场域的介入

## 相关项目

- [OCHR（舟济）](https://github.com/luoxuejian000/OCHR) - 谐振龙虾集群
- [Resonance Inference](https://github.com/luoxuejian000/resonance-inference) - 谐振推理引擎
- [CodeHarmony](https://github.com/luoxuejian000/code-harmony) - 代码和谐度审计
- [GitNarrative](https://github.com/luoxuejian000/chronos-resonance) - Git 演化自传

## 作者

**李广好** (luoxuejian000)

## 协议

MIT License
```
