# ThinkCheck Legal 2.0.1

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Version](https://img.shields.io/badge/version-2.0.1-orange.svg)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)

基于晶脉哲学与谐振理论的法律推理质量评估工具包。

[![GitHub Issues](https://img.shields.io/github/issues/luoxuejian000/-thinkcheck-lib-.svg)](https://github.com/luoxuejian000/-thinkcheck-lib-/issues)
[![GitHub Stars](https://img.shields.io/github/stars/luoxuejian000/-thinkcheck-lib-.svg)](https://github.com/luoxuejian000/-thinkcheck-lib-/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/luoxuejian000/-thinkcheck-lib-.svg)](https://github.com/luoxuejian000/-thinkcheck-lib-/network/members)

## 📋 目录
- [概述](#概述)
- [✨ 核心特性](#-核心特性)
- [🚀 快速开始](#-快速开始)
  - [系统要求](#系统要求)
  - [安装步骤](#安装步骤)
  - [基本使用](#基本使用)
  - [运行演示](#运行演示)
- [🔧 API 参考](#-api-参考)
  - [StandaloneLegalMonitor 类](#standalonelegalmonitor-类)
  - [LegalConfig 配置类](#legalconfig-配置类)
- [📊 评估维度详解](#-评估维度详解)
  - [统一性 (U)](#统一性-u)
  - [发展性 (D)](#发展性-d)
  - [对抗性 (A)](#对抗性-a)
  - [和谐度 (H)](#和谐度-h)
- [🎯 理论背景](#-理论背景)
- [🔬 技术实现](#-技术实现)
- [📈 版本历史](#-版本历史)
- [⚠️ 局限与未来发展](#️-局限与未来发展)
- [🤝 贡献指南](#-贡献指南)
- [📄 许可证](#-许可证)
- [🙏 致谢](#-致谢)
- [📞 联系方式](#-联系方式)

## 概述

**ThinkCheck Legal** 是一个创新的法律文本质量评估工具，基于独特的"晶脉哲学"与"谐振理论"，通过计算**统一性(U)**、**发展性(D)** 和**对抗性(A)** 三个维度，量化评估法律文本的逻辑连贯性、论证展开节奏与内在矛盾程度。

不同于传统工具关注结论的"正确性"，ThinkCheck Legal 的核心价值在于衡量推理过程的"和谐度"，为法律文档分析、合同审查、法律文书质量评估等场景提供全新的量化视角。

https://img.shields.io/badge/Try%20it%20Online-Codespaces-blue?logo=github](https://github.com/luoxuejian000/-thinkcheck-lib-)
https://img.shields.io/badge/View-Demo-green](https://github.com/luoxuejian000/-thinkcheck-lib-/tree/2.0-legal#run-demo)

## ✨ 核心特性

| 特性 | 描述 | 应用场景 |
|------|------|----------|
| **🔍 三维度评估** | 统一性(U)、发展性(D)、对抗性(A)综合评分 | 法律文档质量评估、合同一致性检查 |
| **🎯 语义一致性检测** | 识别法律术语在上下文中的漂移与不一致 | 术语标准化检查、概念一致性验证 |
| **📈 论证节奏分析** | 评估论证的展开质量与逻辑推进 | 法律论证结构分析、论述质量评估 |
| **⚖️ 矛盾张力识别** | 检测文本内部的概念矛盾与论证张力 | 法律文书矛盾检测、论证逻辑验证 |
| **🌟 和谐度综合评分** | 提供0-1的整体质量评分，反映综合质量 | 文档质量排名、自动化评估 |
| **🔧 可扩展架构** | 支持自定义参数配置与评估规则 | 领域适应性调整、个性化评估需求 |

## 🚀 快速开始

### 系统要求
- **Python 3.8+** (推荐 3.9 或更高版本)
- 操作系统：Windows 10+, macOS 10.15+, Linux (Ubuntu 18.04+ 等)
- 内存：至少 2GB RAM
- 存储：至少 500MB 可用空间

### 安装步骤

#### 方式一：标准安装（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/luoxuejian000/-thinkcheck-lib-.git
cd -thinkcheck-lib-

# 2. 切换至 2.0-legal 分支
git checkout 2.0-legal

# 3. 安装项目及其依赖
pip install -e .
```

#### 方式二：分步安装（如遇到PyTorch兼容性问题）

```bash
# 1. 首先安装PyTorch（根据您的系统选择）
# 对于CPU版本
pip install torch --index-url https://download.pytorch.org/whl/cpu

# 或访问 https://pytorch.org/get-started/locally/ 获取适合您GPU的安装命令

# 2. 安装其他依赖
pip install sentence-transformers scikit-learn numpy>=1.24.0

# 3. 安装本工具包
pip install -e .
```

### 基本使用

```python
from thinkcheck_legal import StandaloneLegalMonitor

# 初始化监控器
monitor = StandaloneLegalMonitor()

# 评估法律文本
text = """
根据《民法典》第五百零九条规定，当事人应当按照约定全面履行自己的义务。
在合同履行过程中，如一方违约，守约方有权要求违约方承担违约责任。
然而，在本案中，被告虽存在履约瑕疵，但并未构成根本违约，故不应承担全部赔偿责任。
"""

# 评估文本和谐度
score = monitor.evaluate(text)
report = monitor.get_report()

# 输出评估结果
print(f"📊 评估报告")
print(f"和谐度: {score:.4f}")
print(f"统一性(U): {report['U']:.4f}")
print(f"发展性(D): {report['D']:.4f}")  
print(f"对抗性(A): {report['A']:.4f}")
print(f"综合和谐度: {report['harmony']:.4f}")

# 输出详细警告
if report['drift_warnings']:
    print("\n⚠️ 术语一致性警告:")
    for warn in report['drift_warnings']:
        print(f"  • 术语 '{warn['term']}' 一致性低至 {warn['consistency']:.4f}")

if report['development_warnings']:
    print("\n⚠️ 论证发展警告:")
    for warn in report['development_warnings']:
        print(f"  • {warn}")

if report['contradiction_warnings']:
    print("\n⚠️ 矛盾冲突警告:")
    for warn in report['contradiction_warnings']:
        print(f"  • {warn}")
```

### 运行演示

```bash
# 进入项目目录
cd -thinkcheck-lib-

# 运行演示脚本
python -m demo
```

演示脚本将展示如何使用工具评估示例法律文本，并输出详细的评估报告。您也可以在 https://github.com/luoxuejian000/-thinkcheck-lib-/blob/2.0-legal/demo.py 中查看完整的示例代码。

## 🔧 API 参考

### StandaloneLegalMonitor 类

主监控器类，负责法律文本的和谐度评估。

#### 初始化
```python
monitor = StandaloneLegalMonitor(config=None)
```
- **参数**:
  - `config` (LegalConfig, 可选): 自定义配置对象。如为None，则使用默认配置。
- **返回**: StandaloneLegalMonitor 实例

#### 主要方法

**`evaluate(text)`**
```python
score = monitor.evaluate(text)
```
评估文本的和谐度，返回综合评分（0-1）。

- **参数**:
  - `text` (str): 待评估的法律文本
- **返回**: float，综合和谐度分数（0-1之间）

**`get_report()`**
```python
report = monitor.get_report()
```
获取详细的评估报告，包含所有维度的分数和警告信息。

- **返回**: dict，包含以下键：
  - `U`: 统一性得分 (float)
  - `D`: 发展性得分 (float)  
  - `A`: 对抗性得分 (float)
  - `harmony`: 综合和谐度 (float)
  - `drift_warnings`: 术语漂移警告列表 (list)
  - `development_warnings`: 论证发展警告列表 (list)
  - `contradiction_warnings`: 矛盾冲突警告列表 (list)

**`get_detailed_analysis()`**
```python
analysis = monitor.get_detailed_analysis()
```
获取更详细的分析数据，包括原始向量、相似度矩阵等。

- **返回**: dict，包含原始分析数据

### LegalConfig 配置类

用于自定义评估参数。

```python
from thinkcheck_legal.legal_config import LegalConfig

# 创建自定义配置
config = LegalConfig(
    U_WEIGHT=0.5,      # 统一性权重 (默认: 0.4)
    D_WEIGHT=0.3,      # 发展性权重 (默认: 0.4)
    A_WEIGHT=0.2,      # 对抗性权重 (默认: 0.2)
    U_THRESHOLD=0.85,  # 统一性阈值 (默认: 0.8)
    D_THRESHOLD=0.7,   # 发展性阈值 (默认: 0.7)
    A_THRESHOLD=0.6,   # 对抗性阈值 (默认: 0.5)
    MIN_TERM_LENGTH=2, # 最小术语长度 (默认: 2)
    MAX_TERMS=50,      # 最大术语数 (默认: 50)
    MODEL_NAME='all-MiniLM-L6-v2'  # 使用的模型 (默认: 'all-MiniLM-L6-v2')
)

# 使用自定义配置初始化监控器
monitor = StandaloneLegalMonitor(config=config)
```

## 📊 评估维度详解

### 统一性 (U)
衡量核心法律术语在全文中的语义一致性。低分表示术语使用存在漂移或不一致。

**计算公式**：
```
U = 1 - (术语平均漂移度)
```

其中术语漂移度通过以下步骤计算：
1. 提取文本中的所有法律术语
2. 使用sentence-transformers将每个术语的每次出现转换为向量
3. 计算同一术语不同出现之间的余弦相似度
4. 对每个术语计算平均相似度，然后对所有术语求平均

**阈值设置**：
- 默认阈值：0.8
- 低于此值将触发术语漂移警告
- 建议范围：0.7-0.9（根据文本长度和复杂度调整）

**应用场景**：
- 合同术语一致性检查
- 法律文书概念标准化评估
- 多章节文档术语统一性验证

### 发展性 (D)
评估论证逻辑的展开质量与推进节奏。高分表示论证结构清晰、递进合理。

**评估因素**：
1. **论证层次性**：是否有清晰的论点-分论点结构
2. **逻辑递进关系**：论证是否按逻辑顺序展开
3. **结构完整性**：是否有引言、正文、结论等完整结构
4. **节奏合理性**：各部分长度比例是否合理

**评估方法**：
- 基于结构熵模型分析文本层次
- 检测论证标记词（如"首先"、"其次"、"因此"等）
- 分析段落间的逻辑连接关系

**阈值设置**：
- 默认阈值：0.7
- 低于此值将触发论证发展警告
- 建议范围：0.6-0.8（根据文本类型调整）

**应用场景**：
- 法律论证结构评估
- 诉讼文书逻辑性检查
- 法律意见书结构优化

### 对抗性 (A)
检测文本内部的概念矛盾与论证张力。适当程度的对抗性有助于论证的辩证性，但过度矛盾会损害说服力。

**评估因素**：
1. **转折词密度**：检测"但是"、"然而"、"尽管"等转折词的出现频率
2. **对立概念识别**：识别相互矛盾或对立的法律概念
3. **论证张力分析**：评估不同论点之间的冲突程度

**评估方法**：
- 基于预定义的转折词表进行模式匹配
- 使用语义分析检测概念对立关系
- 计算文本内部的论证张力强度

**阈值设置**：
- 最佳范围：0.4-0.6
- 过低（<0.3）：可能表示论证缺乏辩证性
- 过高（>0.7）：可能表示论证存在内部矛盾
- 超出最佳范围将触发矛盾冲突警告

**应用场景**：
- 法律文书矛盾检测
- 辩论性文本质量评估
- 法律论证辩证性分析

### 和谐度 (H)
综合三个维度的加权评分，反映文本的整体论证质量。

**计算公式**：
```
H = λU * U + λD * D + λA * A
```

其中：
- `λU`、`λD`、`λA` 为权重系数，默认分别为0.4、0.4、0.2
- 满足：`λU + λD + λA = 1`
- 权重可根据具体应用场景调整

**评分解读**：
- **0.9+**：优秀，论证高度和谐
- **0.7-0.9**：良好，论证基本和谐
- **0.5-0.7**：一般，存在可改进空间
- **0.5以下**：需要显著改进

## 🎯 理论背景

ThinkCheck Legal 是"晶脉哲学"与"谐振理论"的工程实现，基于以下四个核心公理：

### 公理1：关系本体论
> "存在即关系，实在即关系网络。"

法律概念的意义不在于其本质，而在于其在法律关系网络中的位置。工具通过检测术语在上下文中的语义一致性，评估其关系稳定性。当一个法律术语在不同上下文中保持稳定的语义关系时，我们认为它具有高度统一性。

**工程体现**：统一性(U)维度，通过术语向量相似度计算实现。

### 公理2：矛盾动力论
> "矛盾是系统演进的内在动力，而非需要消除的缺陷。"

文本中的矛盾不是简单的错误，而是系统向更高层次发展的契机。适当的矛盾能够推动论证深化，激发新的理解维度。工具识别文本中的对抗性，将其视为调谐与发展的动力源泉。

**工程体现**：对抗性(A)维度，通过转折词和概念对立分析实现。

### 公理3：实践介入论
> "评估者的介入本身改变被评估系统的状态。"

评估工具不仅是外在的衡量标尺，更是介入推理过程的参与者。监控器的存在本身就会改变评估场域，创造新的观测条件。这种介入性评估能够揭示传统静态分析无法发现的问题。

**工程体现**：评估过程与文本的互动性，通过实时分析和反馈机制实现。

### 公理4：谐振调谐论
> "最优状态是各维度间的动态平衡谐振。"

单一维度的最大化并非理想状态，真正的优质论证是在统一性、发展性、对抗性之间达到动态平衡的谐振状态。和谐度函数引导系统向更高级别的谐振状态演进。

**工程体现**：和谐度(H)计算，通过加权平衡三个维度实现。

## 🔬 技术实现

### 架构设计

```
ThinkCheck Legal 架构图
┌─────────────────────────────────────────────────────┐
│                   应用层 (Application)               │
│  ┌─────────────────────────────────────────────┐  │
│  │               StandaloneLegalMonitor         │  │
│  │  • evaluate(text) → 和谐度评分               │  │
│  │  • get_report() → 详细评估报告              │  │
│  └─────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────┤
│                   服务层 (Service)                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │ 统一性分析  │  │ 发展性分析  │  │ 对抗性分析  │ │
│  │ • 术语提取  │  │ • 结构分析  │  │ • 矛盾检测  │ │
│  │ • 向量化    │  │ • 节奏评估  │  │ • 张力计算  │ │
│  │ • 相似计算  │  │ • 逻辑验证  │  │ • 辩证评估  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────────┤
│                   核心层 (Core)                     │
│  ┌─────────────────────────────────────────────┐  │
│  │              Harmonic Evaluator              │  │
│  │  • 维度权重配置                            │  │
│  │  • 分数计算与整合                          │  │
│  │  • 阈值检查与警告生成                      │  │
│  └─────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────┤
│                   基础层 (Infrastructure)           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │  NLP模型    │  │  配置管理    │  │  工具函数   │ │
│  │ • sentence- │  │ • LegalConfig│  │ • 文本处理  │ │
│  │   transformers│ • 参数验证    │  │ • 数学计算  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────┘
```

### 核心算法

#### 1. 统一性计算算法
```python
def calculate_uniformity(text):
    # 步骤1: 术语提取与清洗
    terms = extract_legal_terms(text)
    
    # 步骤2: 术语向量化
    term_vectors = embed_terms(terms)
    
    # 步骤3: 相似度矩阵计算
    similarity_matrix = compute_cosine_similarity(term_vectors)
    
    # 步骤4: 漂移度计算
    drift_scores = compute_term_drift(similarity_matrix)
    
    # 步骤5: 统一性分数计算
    uniformity = 1.0 - np.mean(drift_scores)
    
    return uniformity, drift_scores
```

#### 2. 发展性评估算法
```python
def calculate_development(text):
    # 步骤1: 结构分析
    structure = analyze_text_structure(text)
    
    # 步骤2: 逻辑标记检测
    markers = detect_logical_markers(text)
    
    # 步骤3: 节奏分析
    rhythm = analyze_development_rhythm(text)
    
    # 步骤4: 发展性分数计算
    development = combine_scores(structure, markers, rhythm)
    
    return development, structure, markers, rhythm
```

#### 3. 对抗性检测算法
```python
def calculate_adversity(text):
    # 步骤1: 转折词检测
    transition_words = detect_transition_words(text)
    
    # 步骤2: 对立概念识别
    opposing_concepts = identify_opposing_concepts(text)
    
    # 步骤3: 论证张力分析
    tension = analyze_argument_tension(text)
    
    # 步骤4: 对抗性分数计算
    adversity = combine_adversity_scores(
        len(transition_words),
        len(opposing_concepts),
        tension
    )
    
    return adversity, transition_words, opposing_concepts
```

### 性能优化

1. **向量化缓存机制**
   ```python
   # 缓存术语向量，避免重复计算
   term_vector_cache = {}
   def get_term_vector(term):
       if term not in term_vector_cache:
           term_vector_cache[term] = model.encode(term)
       return term_vector_cache[term]
   ```

2. **增量评估支持**
   ```python
   # 支持分块处理长文本
   def evaluate_incremental(text_chunks):
       results = []
       for chunk in text_chunks:
           result = monitor.evaluate(chunk)
           results.append(result)
       return aggregate_results(results)
   ```

3. **批处理优化**
   ```python
   # 批量处理多个文档
   def batch_evaluate(texts):
       with ThreadPoolExecutor() as executor:
           results = list(executor.map(monitor.evaluate, texts))
       return results
   ```

## 📈 版本历史

### v2.0.1 (当前版本) - 2024年4月
**工程修复与优化**
- ✅ 修复包结构问题，标准化为 `thinkcheck_legal` Python包
- ✅ 统一导入路径，彻底解决 `ModuleNotFoundError`
- ✅ 完善 `setup.py` 和 `pyproject.toml`，支持标准 `pip install -e .`
- ✅ 更新文档与示例代码，确保一致性
- ✅ 优化配置管理，提高可扩展性

https://github.com/luoxuejian000/-thinkcheck-lib-/releases/tag/v2.0.1

### v2.0.0 - 2024年3月
**初始功能版本**
- ✅ 实现核心三维度评估算法
- ✅ 提供完整的API接口
- ✅ 包含示例代码和演示
- ✅ 基础配置系统
- ✅ 初步文档

### v1.x 系列
**原型与概念验证**
- 🔄 晶脉哲学理论验证
- 🔄 谐振理论工程化探索
- 🔄 算法原型开发

## ⚠️ 局限与未来发展

### 当前版本局限

1. **A指标依赖转折词表**
   - 当前版本通过预定义的转折词表检测对抗性
   - 可能误伤正常法律论证中的合理转折
   - **解决方案（v3.0规划）**：引入上下文感知的对抗性检测

2. **U/D指标启发式偏差**
   - 统一性和发展性计算包含启发式规则
   - 默认阈值可能不适合所有法律文本类型
   - **解决方案**：提供领域自适应配置

3. **领域特异性限制**
   - 当前模型主要针对通用法律文本优化
   - 特定领域（如专利法、国际法）可能需要调整
   - **解决方案**：提供领域定制接口

4. **多语言支持有限**
   - 主要支持中文法律文本
   - 其他语言评估效果未经充分验证
   - **解决方案**：扩展多语言模型支持

### 未来发展路线图

#### ThinkCheck 3.0 (开发中)
**通用谐振评估SDK**
- 🚀 扩展至多领域评估（金融、医疗、教育等）
- 🚀 深度学习增强评估精度
- 🚀 实时调谐与优化建议
- 🚀 可视化分析界面
- 🚀 API服务化部署

#### 长期愿景
**认知调谐操作系统**
- 🌟 从评估到调谐的范式跃迁
- 🌟 人机协同论证优化
- 🌟 自适应学习与进化
- 🌟 产业级解决方案
- 🌟 标准化与生态建设

## 🤝 贡献指南

我们热烈欢迎社区贡献！无论是代码改进、文档完善、Bug报告还是新功能建议，都是对项目的重要支持。

### 贡献流程

1. **Fork仓库**
   ```bash
   # 点击GitHub页面的Fork按钮
   # 或使用命令行
   git clone https://github.com/luoxuejian000/-thinkcheck-lib-.git
   cd -thinkcheck-lib-
   ```

2. **创建功能分支**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **提交更改**
   ```bash
   git add .
   git commit -m "Add amazing feature"
   git push origin feature/amazing-feature
   ```

4. **发起Pull Request**
   - 访问您的Fork仓库
   - 点击"Compare & pull request"
   - 描述您的更改内容和原因
   - 提交Pull Request

### 贡献领域

- **🐛 Bug修复**：提交详细的Bug报告和修复方案
- **✨ 新功能**：实现新功能或改进现有功能
- **📚 文档**：改进文档、添加示例、修复错别字
- **🔧 测试**：添加测试用例，提高代码覆盖率
- **🌍 国际化**：多语言支持或本地化改进
- **🎨 用户体验**：改进API设计或用户体验

### 开发环境设置

```bash
# 1. 克隆仓库
git clone https://github.com/luoxuejian000/-thinkcheck-lib-.git
cd -thinkcheck-lib-

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 3. 安装开发依赖
pip install -e ".[dev]"

# 4. 运行测试
python -m pytest tests/

# 5. 运行代码风格检查
python -m flake8 thinkcheck_legal/
```

### 代码规范

- 遵循 https://www.python.org/dev/peps/pep-0008/ 代码风格
- 使用类型注解提高代码可读性
- 为函数和类添加清晰的文档字符串
- 保持测试覆盖率在80%以上

## 📄 许可证

本项目采用 **MIT 许可证** - 详情请参阅 https://github.com/luoxuejian000/-thinkcheck-lib-/blob/2.0-legal/LICENSE 文件。

```
MIT License

Copyright (c) 2024 ThinkCheck Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🙏 致谢

ThinkCheck Legal 的发展离不开以下开源项目、研究工作和社区支持：

### 核心技术依赖
- **https://github.com/UKPLab/sentence-transformers** - 提供高质量的文本向量化能力
- **https://scikit-learn.org/** - 机器学习算法基础
- **https://pytorch.org/** - 深度学习框架支持
- **https://numpy.org/** - 数值计算基础库

### 理论奠基
- **晶脉哲学** - 为本工具提供哲学基础
- **谐振理论** - 指导评估框架的设计
- **法律论证理论** - 提供法律文本分析的专业视角

### 社区贡献者
感谢所有为项目做出贡献的开发者、测试者和文档编写者。特别感谢早期用户的反馈和建议，这些宝贵的意见帮助项目不断完善。

### 相关研究
- 法律文本分析的前沿研究
- 自然语言处理在法律领域的应用
- 论证质量评估的相关工作

## 📞 联系方式

### 项目维护者
- **李广好** - 项目创始人 & 主要开发者
- **邮箱**: [请在GitHub Issues中联系]
- **GitHub**: https://github.com/luoxuejian000

### 问题与支持
- **📋 问题报告**: https://github.com/luoxuejian000/-thinkcheck-lib-/issues
- **💬 讨论区**: https://github.com/luoxuejian000/-thinkcheck-lib-/discussions (如有)
- **📧 邮件联系**: 通过GitHub Issues联系

### 社区与资源
- **🌐 项目主页**: https://github.com/luoxuejian000/-thinkcheck-lib-
- **📖 文档**: https://github.com/luoxuejian000/-thinkcheck-lib-/blob/2.0-legal/README.md
- **🚀 最新版本**: https://github.com/luoxuejian000/-thinkcheck-lib-/releases/tag/v2.0.1
- **🐛 已知问题**: https://github.com/luoxuejian000/-thinkcheck-lib-/issues

### 技术交流
欢迎加入我们的技术交流社区：
- 提交Issue进行问题讨论
- 通过Pull Request贡献代码
- 分享使用案例和经验

---

<div align="center">

**ThinkCheck 3.0 通用谐振评估SDK正在积极开发中，敬请期待！**

https://img.shields.io/github/followers/luoxuejian000?label=Follow%20%40luoxuejian000&style=social](https://github.com/luoxuejian000)
https://img.shields.io/github/stars/luoxuejian000/-thinkcheck-lib-?style=social](https://github.com/luoxuejian000/-thinkcheck-lib-/stargazers)
https://img.shields.io/github/watchers/luoxuejian000/-thinkcheck-lib-?style=social](https://github.com/luoxuejian000/-thinkcheck-lib-/subscription)

</div>
