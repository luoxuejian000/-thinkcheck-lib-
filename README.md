```markdown
# ThinkCheck Agent V10

## 企业级文档场域诊断系统

**基于晶脉哲学（Crystal Vein Philosophy）与《镜渊》五重公理的企业级文档和谐度评估与智能调谐系统。**

ThinkCheck Agent V10 是一套以 **U/D/A/H 四维场域诊断框架** 为核心的企业级文档智能分析系统。它不替代人类判断，只提供诊断数据——让企业在合同审查、合规审计、内容质量管控等场景中，拥有可量化、可追溯、可审计的决策依据。


## 核心特性

### 1. 四维场域诊断（U/D/A/H 框架）

| 维度 | 全称 | 诊断内容 |
|------|------|----------|
| **U** | 统一性（Unity） | 文档核心概念、身份、主张的语义稳定性 |
| **D** | 发展性（Development） | 文档信息推进的深度与论证演进节奏 |
| **A** | 对抗性（Adversariality） | 文档内部矛盾的激烈程度与语义张力 |
| **H** | 和谐度（Harmony） | 综合 U/D/A 的场域整体健康度 |

### 2. 企业级能力

- **长文档支持**：单次处理 300 万字以内的超长文档（招股书、尽调资料包、合作协议等）
- **多格式兼容**：支持 `.txt`、`.doc`、`.docx`、`.pdf`、`.md` 等主流文档格式
- **REST API**：完整的 API 服务，可无缝集成到现有企业工作流
- **命令行工具**：简单易用的 CLI，适合快速批量处理
- **OCHR 治理模块**：关系映射、反思腔（审计日志）、边界控制
- **可观测性**：完整的审计日志与操作追溯

### 3. 商业化核心价值

| 场景 | 解决的问题 | 商业价值 |
|------|-----------|----------|
| **合同审查** | 条款间的隐形矛盾（如“30日” vs “45日”） | 降低法律风险，提升审查效率 70%+ |
| **尽职调查** | 尽调资料包中的逻辑断层与概念漂移 | 精准定位风险信号，缩短尽调周期 |
| **合规审计** | 内部文件的一致性检查与风险预警 | 建立可审计的合规证据链 |
| **内容质量管控** | 大规模文档内容质量的自动化评估 | 标准化内容生产流程，降低人工复核成本 |

**核心原则**：系统 **“只看病，不开方”** ——只输出诊断数据（矛盾点定位、概念漂移追踪、A 值累积轨迹），不给出任何修改建议或风险评级。最终判断权完全在用户手中。


## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，设置 DEEPSEEK_API_KEY
```

或配置 config.yaml：

```bash
cp config.example.yaml config.yaml
# 编辑 config.yaml
```

3. 运行命令行工具

```bash
# 评估文档（只诊断，不修改）
python main.py --file your_document.md --no-fix

# 评估并生成诊断报告
python main.py --file your_document.md

# 批量处理目录
python main.py --dir ./docs --pattern "*.md"
```

4. 启动 API 服务

```bash
python api.py
```

或使用 uvicorn：

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

访问 API 文档：http://localhost:8000/docs

5. 运行示例

```bash
python examples/real_world_example.py
```

项目结构

```
thinkcheck-agent-v6/
├── main.py                      # 命令行入口
├── api.py                       # REST API 服务
├── config.py                    # 配置管理
├── requirements.txt             # 依赖列表
├── config.example.yaml          # 配置模板
├── .env.example                 # 环境变量模板
├── thinkcheck_harmony/          # 核心评估引擎（U/D/A/H）
│   ├── __init__.py
│   ├── evaluator.py             # 评估器
│   ├── metrics.py               # 四维指标计算
│   └── utils.py                 # 工具函数
├── ochr/                        # OCHR 治理模块
│   ├── __init__.py
│   ├── relationship_mapper.py   # 关系映射
│   ├── reflection_cavity.py     # 反思腔（审计日志）
│   └── boundary.py              # 边界控制
├── thinkcheck_agent/            # Agent 核心
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── evaluator.py         # 文档评估
│   │   ├── actuator.py          # DeepSeek 调谐
│   │   └── orchestration.py     # 协调器
│   ├── tools/
│   │   ├── __init__.py
│   │   └── file_handler.py      # 文件处理
│   └── workflows/
│       ├── __init__.py
│       └── legal_doc_review.py  # 法律文档审阅
├── examples/                    # 示例代码
│   └── real_world_example.py
├── tests/                       # 测试
│   ├── __init__.py
│   └── test_harmony_metrics.py
├── logs/                        # 日志目录
└── README.md
```

架构说明

1. thinkcheck_harmony（四维评估引擎）

· 统一性 (U)：评估文档内容的一致性和连贯性
· 发展性 (D)：评估文档内容的丰富度和信息推进深度
· 对抗性 (A)：评估文档中的矛盾、冲突和语义张力
· 和谐度 (H)：综合评分，由 U/D/A 动态加权计算

2. OCHR（和谐治理模块）

· RelationshipMapper：分析文档各部分的依赖关系
· ReflectionCavity：审计和记录文档处理过程
· BoundaryController：边界控制与权限管理

许可证

```
Copyright © 2026 李广好 (luoxuejian000)

本软件根据 Apache License, Version 2.0 授权使用。
完整许可证文本请参见 LICENSE 文件。
```

重要声明

1. 理论独创权声明

U/D/A/H 四维场域诊断框架及其背后的晶脉哲学（Crystal Vein Philosophy）与《镜渊》五重公理，是李广好（luoxuejian000）的理论独创成果，受版权法保护。

· 晶脉哲学（Crystal Vein Philosophy）：宇宙数学几何本体论系统哲学
· 《镜渊》：基于晶脉哲学的非替代式人工智能场域诊断与工具理性批判框架
· U/D/A/H 四维指标：统一性（Unity）、发展性（Development）、对抗性（Adversariality）、和谐度（Harmony）

任何对本框架核心理论的学术引用、商业应用或衍生开发，均须注明原始出处并保留本声明。

2. 开源许可说明

本软件以 Apache 2.0 许可证开源，允许商业使用、修改和分发，但须保留版权声明和免责声明。Apache 2.0 许可证不授予对本软件名称、商标或贡献者名称的背书权利。

3. 免责声明

本软件按“现状”提供，不提供任何明示或暗示的担保。使用本软件所产生的任何风险由使用者自行承担。

联系方式

· 项目地址：https://github.com/luoxuejian000/-thinkcheck-lib-
· 问题反馈：Issues
· 理论体系：《晶脉哲学》与《镜渊：非替代式人工智能的场域诊断与工具理性批判》

“本系统仅呈现诊断数据，不构成任何行动建议。判断权在您手中。”

```
