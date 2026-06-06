# ThinkCheck Agent for Enterprise

基于**晶脉哲学与谐振理论**的企业级文档和谐度评估与调谐系统。

## 核心特性

- 📊 **四维评估**: 统一性 (U)、发展性 (D)、对抗性 (A)、和谐度 (H)
- 🤖 **智能调谐**: 集成 DeepSeek AI，自动优化文档
- 🔒 **OCHR治理**: 关系映射、反思腔、边界控制
- ⚡ **高性能**: 支持长文档分块处理、并行计算
- 🌐 **REST API**: 完整的 API 服务
- 📝 **命令行工具**: 简单易用的 CLI
- 📈 **可观测性**: 完整的日志和审计

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并配置：

```bash
cp .env.example .env
# 编辑 .env，设置 DEEPSEEK_API_KEY
```

或者配置 `config.yaml`：

```bash
cp config.example.yaml config.yaml
# 编辑 config.yaml
```

### 3. 运行命令行工具

评估文档：

```bash
python main.py --file your_document.md --no-fix
```

评估并修复文档：

```bash
python main.py --file your_document.md
```

批量处理目录：

```bash
python main.py --dir ./docs --pattern "*.md"
```

### 4. 启动 API 服务

```bash
python api.py
```

或者使用 uvicorn：

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

访问 API 文档：http://localhost:8000/docs

### 5. 运行示例

```bash
python examples/real_world_example.py
```

## 项目结构

```
thinkcheck-agent-v6/
├── main.py                          # 命令行入口
├── api.py                           # REST API 服务
├── config.py                        # 配置管理
├── requirements.txt                 # 依赖列表
├── config.example.yaml              # 配置模板
├── .env.example                     # 环境变量模板
├── thinkcheck_harmony/              # 核心评估引擎
│   ├── __init__.py
│   ├── evaluator.py                 # 评估器
│   ├── metrics.py                   # 四维指标计算
│   └── utils.py                     # 工具函数
├── ochr/                            # OCHR 治理模块
│   ├── __init__.py
│   ├── relationship_mapper.py       # 关系映射
│   ├── reflection_cavity.py         # 反思腔（审计）
│   └── boundary.py                  # 边界控制
├── thinkcheck_agent/                # Agent 核心
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── evaluator.py             # 文档评估
│   │   ├── actuator.py              # DeepSeek 调谐
│   │   └── orchestration.py         # 协调器
│   ├── tools/
│   │   ├── __init__.py
│   │   └── file_handler.py          # 文件处理
│   ├── workflows/
│   │   ├── __init__.py
│   │   └── legal_doc_review.py      # 法律文档审阅
│   └── examples/
│       └── __init__.py
├── examples/                        # 示例代码
│   └── real_world_example.py
├── tests/                           # 测试
│   ├── __init__.py
│   └── test_harmony_metrics.py
├── logs/                            # 日志目录
└── README.md
```

## 架构说明

ThinkCheck Agent 由以下核心模块组成：

### 1. thinkcheck_harmony（四维评估引擎）

- **统一性 (U)**: 评估文档内容的一致性和连贯性
- **发展性 (D)**: 评估文档内容的丰富度和深度
- **对抗性 (A)**: 评估文档中的矛盾、冲突和负面内容
- **和谐度 (H)**: 综合评分，H = 0.4U + 0.4D - 0.2A

### 2. OCHR（和谐治理模块）

- **RelationshipMapper**: 分析文档各部分的依赖关系
- **ReflectionCavity**: 审计和记录文档处理过程
- **BoundaryController**: 保护敏感内容不被修改

### 3. Actuator（DeepSeek 调谐器）

使用 DeepSeek AI 根据评估结果优化文档，支持：
- 指数退避重试
- Token 使用统计
- 响应格式验证
- 结果缓存

### 4. Orchestrator（协调器）

管理完整的**评估-决策-执行-验证**闭环流程。

## API 使用

### 评估文档

```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{"document": "你的文档内容"}'
```

### 和谐化文档

```bash
curl -X POST http://localhost:8000/harmonize \
  -H "Content-Type: application/json" \
  -d '{
    "document": "你的文档内容",
    "auto_fix": true
  }'
```

## 运行测试

```bash
pytest tests/ -v
```

生成覆盖率报告：

```bash
pytest tests/ --cov=thinkcheck_harmony --cov=thinkcheck_agent --cov=ochr --cov-report=html
```

## 企业级特性

### 日志系统

使用 `loguru` 提供结构化日志：
- 控制台彩色输出
- 文件按天轮转
- 保留7天历史
- 自动压缩

### 审计追踪

所有操作都被记录到 `logs/audit/` 目录，包括：
- 评估记录
- 修复记录
- 边界检查记录

### 边界保护

自动识别和保护：
- 法律签字区域
- 合同当事人信息
- 金额信息
- 版权声明

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

详见 `CONTRIBUTING.md`。

## 许可证

MIT License

## 联系方式

- 项目地址: https://github.com/luoxuejian000/thinkcheck-agent-v6
- 问题反馈: https://github.com/luoxuejian000/thinkcheck-agent-v6/issues
