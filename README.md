# ThinkCheck Agent v9 —— 谐振评估引擎

基于**晶脉哲学四重公理**构建的 AI 推理质量评估引擎。通过 **U/D/A/H 四维量化模型**对文本进行深层语义诊断——检测概念漂移、逻辑矛盾与论证质量，并提供可操作的调谐建议。

> 📌 **社区验证**：本工具已在 DeepSeek 社区通过 @icophy、@qingkong66、@fkyah3 等独立研究者的严格技术审查。icophy 提出的 A 值“构造效度”批评已在 v9 中通过彻底的“去词库化”重构解决。详见 [#1386](https://github.com/deepseek-ai/DeepSeek-V3/issues/1386)。

---

## 核心函数

```
H = λᵤ·U + λᴅ·D - λₐ·A
```

| 维度 | 含义 | 哲学对应 | 计算方式 |
|------|------|---------|---------|
| **U (统一性)** | 语义一致性、概念在场强度 | 关系本体论 | 同术语一致性 + 跨术语一致性 |
| **D (发展性)** | 新信息价值、逻辑流动的连续性 | 谐振调谐论 | 真伪创新区分 + 分布均匀性 |
| **A (对抗性)** | 矛盾张力、关系网络中的冲突强度 | 矛盾动力论 | 语义对立检测 + 词汇矛盾 + 跨块追踪 |
| **H (和谐度)** | 整体推理质量 | 四重公理统一 | λᵤ·U + λᴅ·D - λₐ·A |

---

## 架构

```
thinkcheck-agent-v9/
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

---

## 关键特性

- **四维量化评估**：U/D/A/H 连续值，非二值判断
- **语义矛盾检测**：基于句子嵌入的向量对立检测，**不依赖任何预设词库**
- **构成分解暴露**：每条矛盾边的类型、权重、句子位置完全可追溯
- **长文本支持**：分块处理 + 跨块矛盾追踪，支持多轮对话
- **可配置权重**：λ 权重通过配置文件设置，支持运行时动态调整
- **全链路审计**：权重来源和修改历史可追溯
- **完全本地运行**：评估过程不调用任何外部 API，数据不出本机
- **优雅降级**：语义模型不可用时自动回退到基础逻辑

---

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
  "warnings": ["概念漂移风险"],
  "A_detail": {
    "total_edges": 2,
    "max_weight": 0.35,
    "avg_weight": 0.25,
    "interpretation": "一处强矛盾",
    "edges": [
      {"type": "contradiction", "weight": 0.35, "sentence_pair": [0, 1]},
      {"type": "semantic_opposition", "weight": 0.15, "sentence_pair": null}
    ]
  }
}
```

---

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
| 通用 | 0.4 | 0.4 | 0.2 | 平衡设置（默认） |

---

## 升级记录 (v9)

本版本是对 @icophy 在 DeepSeek 社区 #1386 提案中提出的“构造效度”批评的系统性回应：

1. **A 模块重构（去词库化）**：彻底移除预设语义对立词库，改为基于句子嵌入余弦相似度的关系网络检测。A 值在纯语义矛盾案例上从旧版 0.0000 跃升至 0.25
2. **法律案例突破**：成功检测“持有公司51%股权，因此该股东并未持有多数股权”的隐含矛盾，A 值达到 0.9991
3. **构成分解暴露**：A 值的每条矛盾边（类型、权重、句子位置）完全可追溯
4. **U 增强**：新增跨术语一致性检测 + 短文本连续评估
5. **D 增强**：新增真伪创新区分，过滤换说法重复旧观点的伪新信息
6. **H 审计**：λ 权重完全可配置，审计日志记录权重来源和修改历史
7. **长文本支持**：分块处理 + 跨块矛盾追踪 + 长句拆分编码

**关键验证数据**（完整报告见仓库 `UPGRADE_VERIFICATION_REPORT.md`）：

| 测试案例 | U值 | D值 | A值 | H值 | 病理判定 | 矛盾边数 |
|---------|-----|-----|-----|-----|---------|---------|
| 纯语义矛盾 | 0.1667 | 0.5165 | **0.2500** | 0.2233 | 需调谐 | 1 |
| 法律文书矛盾 | 0.2000 | 0.7600 | **0.9991** | **0.1842** | 高对抗性 | 6 |
| e租宝案长文本 | 0.2567 | 0.9764 | **0.9998** | **0.1076** | 高对抗性 | 6 |

---

## 社区验证

本工具在 DeepSeek 社区的演进过程：

- **@icophy**（#1386）：提出 A 值“构造效度”批评 → v9 通过彻底去词库化回应 → icophy 确认“I accept the theoretical reframe”
- **@qingkong66**（#1255, #1386, #1387）：三次将 ThinkCheck 收录进月度社区文摘，主动引荐与璇玑、语言漂移研究的连接
- **@fkyah3**（#1255）：独立设计控制实验验证语言漂移，与 ThinkCheck 的实验框架形成互补
- **极限验证**：e 租宝案（约 3000 字法律长文本）A 值达到 0.9998，6 条矛盾边全部可追溯，准确识别分布式张力

---

## 理论根基

ThinkCheck 建立在晶脉哲学的四重公理之上：

- **关系本体论**：意义在关系网络中被定义。U 度量概念在关系网络中的语义一致性。
- **矛盾动力论**：矛盾是系统演化的能量源。A 度量矛盾在关系场域中的连续张力，**不是二值分类器**。
- **谐振调谐论**：系统朝向更高和谐度自组织。H 度量系统的整体谐振质量。
- **实践介入论**：每次评估都是对语义场域的介入。审计日志记录每一次介入的痕迹，权重来源可追溯。

---

## 相关项目

- [OCHR（舟济）](https://github.com/luoxuejian000/OCHR) — 谐振龙虾集群，AI Agent 安全治理层
- [Resonance Inference](https://github.com/luoxuejian000/resonance-inference) — 谐振推理引擎，LLM 推理实时温度调度
- [CodeHarmony](https://github.com/luoxuejian000/code-harmony) — 代码和谐度审计工具
- [GitNarrative](https://github.com/luoxuejian000/chronos-resonance) — Git 演化自传生成器
- [Experiment Console × ThinkCheck](https://github.com/luoxuejian000/experiment-console-thinkcheck) — AI 实验控制台集成 ThinkCheck 评估

---

## 作者

**李广好** (luoxuejian000)

- DeepSeek 社区活跃贡献者（#1255, #1386, #1387）
- 晶脉哲学与谐振理论提出者
- 独立开发者，全部项目开源

---

## 协议

MIT License
```
