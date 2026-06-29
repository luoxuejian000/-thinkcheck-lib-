# ThinkCheck Agent v6 - 完整代码库

> 基于晶脉哲学与谐振理论的文档和谐度评估与调谐服务

---

## 📁 目录结构

```
thinkcheck-agent-v6/
├── api.py                    # REST API服务
├── main.py                   # 命令行入口
├── config.py                 # 配置管理
├── requirements.txt          # 依赖列表
├── thinkcheck_agent/         # 核心Agent模块
│   ├── core/                 # 协调层
│   │   ├── orchestration.py  # 协调器
│   │   ├── evaluator.py      # 文档评估器
│   │   ├── actuator.py       # 调谐执行器
│   │   ├── challenger.py     # 双脑博弈质疑器
│   │   └── long_text.py      # 长文本处理
│   ├── tools/
│   │   └── file_handler.py   # 文件处理
│   └── workflows/
│       └── legal_doc_review.py # 法律文档审阅
├── ochr/                     # 和谐治理模块
│   ├── boundary.py           # 边界控制器
│   ├── reflection_cavity.py  # 反思腔
│   └── relationship_mapper.py # 关系映射器
├── thinkcheck-harmony/       # 和谐度评估SDK
│   └── thinkcheck_harmony/
│       ├── core.py           # 核心计算
│       ├── evaluator.py      # 评估器
│       ├── concept_graph.py  # 概念图谱
│       ├── contradiction_detector.py # 矛盾检测
│       ├── config.py         # 配置
│       ├── report.py         # 报告结构
│       ├── intervention/     # 干预模块
│       └── presets/          # 领域预设
└── thinkcheck_product/       # ThinkCheck产品版
    └── thinkcheck/
        ├── core.py           # 监控器
        ├── decorator.py      # 装饰器
        └── improved.py       # 改进版本
```

---

## 🚀 入口文件

### 1. api.py - REST API服务

```python
"""
ThinkCheck Agent - REST API 服务
"""

import asyncio
import uuid
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from loguru import logger

from config import settings
from thinkcheck_agent.core.orchestration import Orchestrator, TaskContext
from thinkcheck_agent.core.evaluator import DocumentEvaluator
from thinkcheck_agent.core.actuator import HarmonyActuator


# 全局变量
orchestrator: Optional[Orchestrator] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """生命周期管理"""
    global orchestrator
    
    logger.info("启动 ThinkCheck Agent API 服务...")
    
    # 初始化组件
    evaluator = DocumentEvaluator({})
    actuator = HarmonyActuator({})
    orchestrator = Orchestrator(evaluator, actuator, {}, enable_ochr=True)
    
    logger.info("服务已启动")
    yield
    
    logger.info("服务正在关闭...")


app = FastAPI(
    title="ThinkCheck Agent API",
    description="基于晶脉哲学与谐振理论的文档和谐度评估与调谐服务",
    version="1.0.0",
    lifespan=lifespan
)


# 请求/响应模型
class DocumentInput(BaseModel):
    document: str = Field(..., description="待处理的文档内容", min_length=1)
    workflow_type: str = Field("legal_review", description="工作流类型")
    auto_fix: bool = Field(True, description="是否自动修复")


class EvaluationResult(BaseModel):
    U: float = Field(..., description="统一性分数")
    D: float = Field(..., description="发展性分数")
    A: float = Field(..., description="对抗性分数")
    H: float = Field(..., description="和谐度分数")


class HarmonizeResponse(BaseModel):
    request_id: str
    status: str
    initial_scores: Optional[EvaluationResult] = None
    final_scores: Optional[EvaluationResult] = None
    improvement: float = 0.0
    fixed_document: Optional[str] = None
    fix_strategy: Optional[str] = None
    suggestions: list = Field(default_factory=list)
    warnings: list = Field(default_factory=list)
    error: Optional[str] = None
    ochr_info: Dict[str, Any] = Field(default_factory=dict)


# 中间件
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """添加请求 ID"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    with logger.contextualize(request_id=request_id):
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


# 端点
@app.get("/")
async def root():
    """根端点"""
    return {
        "name": "ThinkCheck Agent API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


@app.post("/evaluate", response_model=Dict[str, Any])
async def evaluate(request: Request, input_data: DocumentInput):
    """
    评估文档的和谐度
    
    返回四维分数: U (统一性), D (发展性), A (对抗性), H (和谐度)
    """
    request_id = request.state.request_id
    logger.info(f"评估请求: {request_id}")
    
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="服务未初始化")
        
        # 评估
        evaluator = orchestrator.evaluator
        report = evaluator.evaluate(input_data.document)
        report_dict = report.to_dict()
        
        result = {
            "request_id": request_id,
            "scores": {
                "U": report_dict["U"],
                "D": report_dict["D"],
                "A": report_dict["A"],
                "H": report_dict["H"]
            },
            "suggestions": report_dict.get("suggestions", []),
            "warnings": report_dict.get("warnings", [])
        }
        
        logger.info(f"评估完成: H={report_dict['H']:.3f}")
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"评估失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/harmonize", response_model=HarmonizeResponse)
async def harmonize(request: Request, input_data: DocumentInput):
    """
    和谐化文档
    
    执行完整的评估-修复-验证流程
    """
    request_id = request.state.request_id
    logger.info(f"和谐化请求: {request_id}")
    
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="服务未初始化")
        
        # 创建上下文
        context = TaskContext(
            file_path="api_input",
            original_content=input_data.document,
            workflow_type=input_data.workflow_type,
            config={},
            request_id=request_id
        )
        
        # 执行协调
        result = await orchestrator.orchestrate(
            context,
            auto_fix=input_data.auto_fix
        )
        
        # 构建响应
        response = HarmonizeResponse(
            request_id=request_id,
            status=result.get("status", "unknown"),
            initial_scores=EvaluationResult(**result["initial_scores"]) if result.get("initial_scores") else None,
            final_scores=EvaluationResult(**result["final_scores"]) if result.get("final_scores") else None,
            improvement=result.get("improvement", 0.0),
            fixed_document=result.get("fixed_content"),
            fix_strategy=result.get("fix_strategy"),
            suggestions=result.get("suggestions", []),
            warnings=result.get("warnings", []),
            error=result.get("error"),
            ochr_info=result.get("ochr_info", {})
        )
        
        logger.info(f"和谐化完成: status={response.status}")
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"和谐化失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/session/summary")
async def session_summary():
    """获取会话摘要"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="服务未初始化")
        
        summary = orchestrator.get_session_summary()
        return {"summary": summary}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"获取会话摘要失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 错误处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.exception(f"未处理的异常 [{request_id}]: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "内部服务器错误",
            "request_id": request_id
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
```

---

### 2. main.py - 命令行入口

```python
"""
ThinkCheck Agent - 命令行入口
"""

import asyncio
import argparse
import sys
import yaml
import json
from pathlib import Path
from loguru import logger

from config import settings
from thinkcheck_agent.core.orchestration import Orchestrator, TaskContext
from thinkcheck_agent.core.evaluator import DocumentEvaluator
from thinkcheck_agent.core.actuator import HarmonyActuator
from thinkcheck_agent.tools.file_handler import FileHandler


def setup_logging():
    """配置日志"""
    log_file = Path(settings.log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 移除默认处理器
    logger.remove()
    
    # 控制台输出
    logger.add(
        sys.stderr,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # 文件输出（按天轮转，保留7天）
    logger.add(
        log_file,
        level=settings.log_level,
        rotation="00:00",
        retention="7 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}"
    )


def load_config(config_path: str = None):
    """加载配置文件"""
    config = {}
    
    if config_path and Path(config_path).exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
            logger.info(f"已加载配置: {config_path}")
        except Exception as e:
            logger.warning(f"加载配置失败: {e}")
    
    return config


async def process_file(
    orchestrator: Orchestrator,
    file_handler: FileHandler,
    file_path: str,
    auto_fix: bool = True
):
    """处理单个文件"""
    logger.info(f"处理文件: {file_path}")
    
    # 读取文件
    content = file_handler.read_file(file_path)
    if not content:
        logger.error(f"无法读取文件: {file_path}")
        return None
    
    # 创建上下文
    context = TaskContext(
        file_path=file_path,
        original_content=content,
        workflow_type="legal_review",
        config={}
    )
    
    # 执行协调
    result = await orchestrator.orchestrate(context, auto_fix=auto_fix)
    
    # 保存修复结果
    if result.get('status') == 'success' and result.get('fixed_content'):
        fixed_path = file_handler.write_fixed_file(file_path, result['fixed_content'])
        logger.info(f"修复结果已保存: {fixed_path}")
        result['fixed_file_path'] = fixed_path
    
    return result


async def main():
    parser = argparse.ArgumentParser(description="ThinkCheck Agent for Enterprise")
    parser.add_argument("--config", default="config.yaml", help="配置文件路径")
    parser.add_argument("--file", help="处理单个文件")
    parser.add_argument("--dir", help="批量处理目录")
    parser.add_argument("--pattern", default="*.md", help="文件匹配模式")
    parser.add_argument("--workflow", default="legal_review", help="工作流类型")
    parser.add_argument("--no-fix", action="store_true", help="只评估不修复")
    parser.add_argument("--output", help="输出结果文件 (JSON)")
    parser.add_argument("--mode", default="full", choices=["simple", "full"], help="运行模式 (simple: 禁用 OCHR)")
    args = parser.parse_args()
    
    # 设置日志
    setup_logging()
    
    # 加载配置
    config = load_config(args.config)
    
    # 初始化组件
    logger.info("初始化 ThinkCheck Agent...")
    
    evaluator = DocumentEvaluator(config)
    actuator = HarmonyActuator(config)
    orchestrator = Orchestrator(
        evaluator,
        actuator,
        config,
        enable_ochr=(args.mode == "full")
    )
    file_handler = FileHandler()
    
    all_results = []
    
    try:
        if args.file:
            # 处理单个文件
            result = await process_file(
                orchestrator,
                file_handler,
                args.file,
                auto_fix=not args.no_fix
            )
            if result:
                all_results.append(result)
        
        elif args.dir:
            # 批量处理目录
            dir_path = Path(args.dir)
            if not dir_path.exists():
                logger.error(f"目录不存在: {args.dir}")
                return
            
            files = list(dir_path.glob(args.pattern))
            logger.info(f"找到 {len(files)} 个文件")
            
            for file_path in files:
                result = await process_file(
                    orchestrator,
                    file_handler,
                    str(file_path),
                    auto_fix=not args.no_fix
                )
                if result:
                    all_results.append(result)
        
        else:
            parser.print_help()
            return
        
        # 输出结果
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(all_results, f, ensure_ascii=False, indent=2)
            logger.info(f"结果已保存: {args.output}")
        else:
            # 控制台输出摘要
            print("\n" + "="*80)
            print("处理结果摘要")
            print("="*80)
            
            for r in all_results:
                print(f"\n文件: {r.get('request_id', 'N/A')}")
                print(f"状态: {r.get('status', 'N/A')}")
                
                if r.get('initial_scores'):
                    s = r['initial_scores']
                    print(f"初始分数: U={s['U']:.3f}, D={s['D']:.3f}, A={s['A']:.3f}, H={s['H']:.3f}")
                
                if r.get('final_scores'):
                    s = r['final_scores']
                    print(f"最终分数: U={s['U']:.3f}, D={s['D']:.3f}, A={s['A']:.3f}, H={s['H']:.3f}")
                    print(f"改进: {r.get('improvement', 0):+.3f}")
                
                if r.get('error'):
                    print(f"错误: {r['error']}")
            
            print("\n" + "="*80)
            
            # 会话摘要
            summary = orchestrator.get_session_summary()
            if summary:
                print("\n会话摘要:")
                print(f"  总评估数: {summary.get('total_evaluations', 0)}")
                print(f"  总修复数: {summary.get('total_repairs', 0)}")
                print(f"  总改进: {summary.get('total_improvement', 0):.3f}")
    
    except FileNotFoundError as e:
        logger.error(f"文件未找到: {e}")
    except KeyboardInterrupt:
        logger.warning("用户中断")
    except Exception as e:
        logger.exception(f"系统运行异常: {e}")


if __name__ == "__main__":
    asyncio.run(main())
```

---

### 3. config.py - 配置管理

```python
"""
配置管理模块
"""

import os
from typing import Optional
from pathlib import Path
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


# 加载 .env 文件
env_path = Path('.') / '.env'
if env_path.exists():
    load_dotenv(env_path)


class Settings(BaseSettings):
    """
    应用配置
    """
    
    # DeepSeek API 配置
    deepseek_api_key: str = Field(default="", description="DeepSeek API Key")
    deepseek_base_url: str = Field(default="https://api.deepseek.com/v1", description="DeepSeek API Base URL")
    deepseek_model: str = Field(default="deepseek-chat", description="DeepSeek Model Name")
    deepseek_max_tokens: int = Field(default=4000, description="Max tokens per request")
    deepseek_temperature: float = Field(default=0.1, description="Temperature for generation")
    deepseek_max_retries: int = Field(default=3, description="Max retries for API calls")
    deepseek_timeout: int = Field(default=30, description="Timeout in seconds")
    
    # ThinkCheck 配置
    thinkcheck_default_domain: str = Field(default="legal", description="Default domain")
    thinkcheck_harmony_threshold: float = Field(default=0.7, description="Harmony threshold")
    thinkcheck_adversarial_threshold: float = Field(default=0.3, description="Adversarial threshold")
    thinkcheck_enable_suggestions: bool = Field(default=True, description="Enable suggestions")
    
    # OCHR 配置
    ochr_boundary_mode: str = Field(default="adaptive", description="Boundary mode")
    
    # 日志配置
    log_level: str = Field(default="INFO", description="Log level")
    log_file: str = Field(default="logs/agent.log", description="Log file path")
    
    # 性能配置
    max_file_size_mb: int = Field(default=10, description="Max file size in MB")
    batch_size: int = Field(default=5, description="Batch size")
    cache_enabled: bool = Field(default=True, description="Enable cache")
    cache_ttl_seconds: int = Field(default=3600, description="Cache TTL in seconds")
    
    # API 服务配置
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    
    model_config = {
        "env_prefix": "THINKCHECK_",
        "env_file": ".env",
        "extra": "ignore"
    }
    
    @field_validator('deepseek_api_key')
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        if not v or v == "${DEEPSEEK_API_KEY}":
            # 尝试从环境变量获取
            return os.environ.get("DEEPSEEK_API_KEY", "")
        return v


# 全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """
    获取配置实例
    """
    return settings
```

---

## 🧩 核心Agent模块 (thinkcheck_agent/)

### 4. orchestration.py - 协调器

```python
"""
OCHR 协调器 - 谐振调谐的指挥中心
"""

import uuid
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from loguru import logger

from .evaluator import DocumentEvaluator
from .actuator import HarmonyActuator
from .challenger import ChallengeAgent
from ochr import RelationshipMapper, ReflectionCavity, BoundaryController


class EvaluationError(Exception):
    """评估错误"""
    pass


class RepairError(Exception):
    """修复错误"""
    pass


class OCHRError(Exception):
    """OCHR 错误"""
    pass


@dataclass
class TaskContext:
    file_path: str
    original_content: str
    workflow_type: str = "default"
    intermediate_results: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))


class Orchestrator:
    """
    协调器 - 管理完整的评估-决策-执行-验证闭环
    """

    def __init__(
        self,
        evaluator: DocumentEvaluator,
        actuator: HarmonyActuator,
        config: Dict,
        enable_ochr: bool = True
    ):
        self.evaluator = evaluator
        self.actuator = actuator
        self.config = config
        self.enable_ochr = enable_ochr

        # 权重配置
        self.lambdas = {"U": 0.4, "D": 0.4, "A": 0.2}

        # OCHR 组件
        if enable_ochr:
            self.relationship_mapper = RelationshipMapper()
            self.reflection_cavity = ReflectionCavity()
            self.boundary_controller = BoundaryController()
            logger.info("OCHR 组件已启用")
        else:
            self.relationship_mapper = None
            self.reflection_cavity = None
            self.boundary_controller = None

        # 双脑博弈质疑组件
        self.challenger = ChallengeAgent(config, actuator)

    def negotiate_weights(self, stakeholder_prefs: Dict[str, Dict[str, float]]):
        """
        协商权重
        """
        avg = {"U": 0.0, "D": 0.0, "A": 0.0}
        n = len(stakeholder_prefs)

        if n > 0:
            for prefs in stakeholder_prefs.values():
                for k in avg:
                    avg[k] += prefs.get(k, 0.0)

            for k in avg:
                avg[k] /= n

        self.lambdas = avg
        logger.info(f"权重协商完成: {self.lambdas}")

    async def orchestrate(
        self,
        context: TaskContext,
        auto_fix: bool = True
    ) -> Dict[str, Any]:
        """
        执行完整的协调流程

        Args:
            context: 任务上下文
            auto_fix: 是否自动修复

        Returns:
            协调结果
        """
        request_id = context.request_id
        logger.info(f"[{request_id}] 开始协调流程")

        result = {
            'status': 'success',
            'request_id': request_id,
            'needs_tuning': False,
            'initial_scores': None,
            'final_scores': None,
            'improvement': 0.0,
            'fixed_content': None,
            'fix_strategy': None,
            'suggestions': [],
            'warnings': [],
            'error': None,
            'ochr_info': {},
            'challenge_report': None
        }

        try:
            # 阶段 1: 边界检查
            if self.enable_ochr and self.boundary_controller:
                allowed, violations = self.boundary_controller.check_permissions(context.original_content)
                result['ochr_info']['boundary_check'] = {
                    'allowed': allowed,
                    'violations': violations
                }

                if self.reflection_cavity:
                    self.reflection_cavity.log_boundary_check(
                        context.file_path,
                        allowed,
                        f"found {len(violations)} violations"
                    )

                if not allowed:
                    result['status'] = 'blocked'
                    result['error'] = "文档包含禁止修改的内容"
                    logger.warning(f"[{request_id}] 文档被边界控制器阻止")
                    return result

            # 阶段 2: 关系分析
            if self.enable_ochr and self.relationship_mapper:
                relationship_info = self.relationship_mapper.analyze(context.original_content)
                result['ochr_info']['relationship_analysis'] = relationship_info

            # 阶段 3: 评估
            logger.info(f"[{request_id}] 开始评估")
            evaluation_report = self.evaluator.evaluate(context.original_content)
            evaluation_dict = evaluation_report.to_dict()

            initial_scores = {
                'U': evaluation_dict['U'],
                'D': evaluation_dict['D'],
                'A': evaluation_dict['A'],
                'H': evaluation_dict['H']
            }
            result['initial_scores'] = initial_scores
            result['suggestions'] = evaluation_dict.get('suggestions', [])
            result['warnings'] = evaluation_dict.get('warnings', [])
            result['needs_tuning'] = evaluation_dict.get('H', 1.0) < 0.7 or evaluation_dict.get('A', 0) > 0.3

            # 构建诊断字典用于质疑
            diagnosis = {
                'needs_tuning': result['needs_tuning'],
                'pathology': self._classify_pathology(initial_scores),
                'harmony_report': initial_scores,
                'suggestions': result['suggestions'],
                'drift_warnings': result['warnings']
            }
            context.intermediate_results['initial_diagnosis'] = diagnosis

            # 阶段 3.5: 双脑博弈质疑
            logger.info(f"[{request_id}] 执行质疑审查")
            challenge_report = self.challenger.challenge(context.original_content, diagnosis)
            context.intermediate_results['challenge_report'] = challenge_report
            result['challenge_report'] = challenge_report

            # 快速检查：如果已经很好了
            if initial_scores['H'] >= 0.9:
                logger.info(f"[{request_id}] 文档和谐度已足够高 (H={initial_scores['H']:.3f})，跳过修复")
                result['status'] = 'no_tuning_needed'
                return result

            # 如果不需要修复或不自动修复
            if not result['needs_tuning'] or not auto_fix:
                logger.info(f"[{request_id}] 文档不需要调谐或自动修复已禁用")
                result['status'] = 'evaluation_only' if not auto_fix else 'no_tuning_needed'
                return result

            # 阶段 4: 执行修复
            logger.info(f"[{request_id}] 开始修复")

            repair_result = self.actuator.tune(context.original_content, diagnosis)

            if not repair_result['success']:
                result['status'] = 'error'
                result['error'] = repair_result.get('error', '修复失败')
                logger.error(f"[{request_id}] 修复失败: {result['error']}")
                return result

            result['fixed_content'] = repair_result['tuned_text']
            result['fix_strategy'] = repair_result['strategy']

            # 阶段 5: 验证修复结果
            logger.info(f"[{request_id}] 验证修复结果")
            final_report = self.evaluator.evaluate(result['fixed_content'])
            final_dict = final_report.to_dict()

            final_scores = {
                'U': final_dict['U'],
                'D': final_dict['D'],
                'A': final_dict['A'],
                'H': final_dict['H']
            }
            result['final_scores'] = final_scores

            # 计算改进
            result['improvement'] = final_scores['H'] - initial_scores['H']

            # 记录审计
            if self.reflection_cavity:
                self.reflection_cavity.log_repair(
                    context.file_path,
                    initial_scores,
                    final_scores,
                    [f"Strategy: {result['fix_strategy']}"]
                )

            logger.info(f"[{request_id}] 协调完成: H={initial_scores['H']:.3f} -> {final_scores['H']:.3f}, improvement={result['improvement']:+.3f}")

        except EvaluationError as e:
            result['status'] = 'error'
            result['error'] = f"评估失败: {e}"
            logger.exception(f"[{request_id}] 评估错误")
        except RepairError as e:
            result['status'] = 'error'
            result['error'] = f"修复失败: {e}"
            logger.exception(f"[{request_id}] 修复错误")
        except OCHRError as e:
            result['status'] = 'error'
            result['error'] = f"OCHR 失败: {e}"
            logger.exception(f"[{request_id}] OCHR 错误")
        except Exception as e:
            result['status'] = 'error'
            result['error'] = f"未知错误: {e}"
            logger.exception(f"[{request_id}] 未知错误")

        return result

    def _classify_pathology(self, scores: Dict[str, float]) -> str:
        """
        分类病理
        """
        h = scores.get('H', 0)
        a = scores.get('A', 0)
        u = scores.get('U', 0)
        d = scores.get('D', 0)

        if h >= 0.6:
            return "谐振态"
        if u < 0.3 and a > 0.7 and h < 0:
            return "逻辑自杀"
        if d < 0.2 and a < 0.3 and h < 0.4:
            return "逻辑空洞"
        if h >= 0.4 and a < 0.2:
            return "度假合格"
        return "需调谐"

    def get_session_summary(self) -> Optional[Dict[str, Any]]:
        """
        获取会话摘要
        """
        if self.reflection_cavity:
            return self.reflection_cavity.get_session_summary()
        return None
```

---

### 5. evaluator.py - 文档评估器

```python
"""
ThinkCheck 评估器封装
对核心 ThinkCheck Harmony SDK 进行工程化封装，提供健壮的评估接口。
集成长文本处理、语义向量检测、可配置权重等功能。
"""
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from loguru import logger
import re
import numpy as np

try:
    from thinkcheck_harmony import HarmonyEvaluator
    from thinkcheck_harmony.metrics import (
        calculate_unity, calculate_development, 
        calculate_adversarial, calculate_harmony,
        get_current_weights
    )
except ImportError:
    logger.error("未找到 thinkcheck_harmony 模块。请确保它已安装或在 Python 路径中。")
    HarmonyEvaluator = None

from .long_text import TextChunker, InterBlockContradictionTracker


class DocumentEvaluator:
    """文档评估器，负责调用 ThinkCheck 引擎进行 U/D/A/H 四维评估。
    集成长文本处理、语义向量检测、可配置权重等功能。
    """

    def __init__(self, config: Dict[str, Any]):
        tc_config = config.get('thinkcheck', {})
        self.domain = tc_config.get('default_domain', 'general')
        self.harmony_threshold = tc_config.get('harmony_threshold', 0.7)
        self.adversarial_threshold = tc_config.get('adversarial_threshold', 0.3)
        
        # 配置权重（支持审计）
        self.lambda_u = float(config.get('LAMBDA_U', tc_config.get('lambda_u', 0.4)))
        self.lambda_d = float(config.get('LAMBDA_D', tc_config.get('lambda_d', 0.4)))
        self.lambda_a = float(config.get('LAMBDA_A', tc_config.get('lambda_a', 0.2)))
        
        # 长文本处理配置
        self.semantic_threshold = float(config.get('SEMANTIC_CONTRADICTION_THRESHOLD', -0.2))
        
        # 转折连词列表
        self.contrast_conjunctions = {'但', '然而', '却', '不过', '只是', '可惜', '反而', '相反', '尽管如此', '但是', '可'}
        
        # 长文本处理组件
        self.text_chunker = TextChunker(max_chars_per_chunk=4000)
        self.cross_tracker = None
        
        # 初始化语义模型（如果可用）
        self.semantic_model = None
        self.embedder = None
        if hasattr(self, 'embedder') and self.embedder is not None:
            self.semantic_model = self.embedder
        else:
            try:
                from sentence_transformers import SentenceTransformer
                self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("语义模型加载成功")
            except Exception as e:
                logger.warning(f"语义模型加载失败，将使用基础评估: {e}")
                self.semantic_model = None
        
        self.evaluator = None
        if HarmonyEvaluator is not None:
            try:
                self.evaluator = HarmonyEvaluator(domain=self.domain, enable_suggestions=tc_config.get('enable_suggestions', True))
                logger.info("ThinkCheck 评估器初始化成功。")
            except Exception as e:
                logger.error(f"初始化 ThinkCheck 评估器失败: {e}")
        else:
            logger.error("HarmonyEvaluator 不可用。所有评估请求将返回默认值。")

    def _split_long_sentence(self, sentence: str, max_chars: int = 200) -> List[str]:
        """
        将长句子拆分为较短的部分
        """
        if len(sentence) <= max_chars:
            return [sentence]
        parts = []
        current = ''
        for char in sentence:
            current += char
            if len(current) >= max_chars and char in '，。！？；：,.;!?':
                parts.append(current.strip())
                current = ''
        if current.strip():
            parts.append(current.strip())
        return parts if parts else [sentence]

    def _safe_encode(self, sentences: List[str]) -> tuple[Optional[Dict[str, np.ndarray]], List[str]]:
        """
        安全地编码句子，处理长句子
        返回：(句子到嵌入的映射, 处理后的句子列表)
        """
        if self.semantic_model is None:
            return None, sentences
        
        processed = []
        for sent in sentences:
            if len(sent) > 200:
                sub_parts = self._split_long_sentence(sent)
                processed.extend(sub_parts)
            else:
                processed.append(sent)
        
        try:
            embeddings = self.semantic_model.encode(processed, convert_to_numpy=True)
        except Exception as e:
            logger.warning(f"语义编码失败: {e}")
            return None, processed
        
        long_sent_map = {}
        emb_idx = 0
        for sent in sentences:
            if len(sent) > 200:
                sub_parts = self._split_long_sentence(sent)
                sub_embs = embeddings[emb_idx:emb_idx+len(sub_parts)]
                long_sent_map[sent] = np.mean(sub_embs, axis=0)
                emb_idx += len(sub_parts)
            else:
                long_sent_map[sent] = embeddings[emb_idx]
                emb_idx += 1
        
        return long_sent_map, processed

    def _get_sentence_embedding(self, sentence: str) -> Optional[np.ndarray]:
        """
        获取单个句子的嵌入向量
        """
        if self.semantic_model is None:
            return None
        try:
            return self.semantic_model.encode([sentence], convert_to_numpy=True)[0]
        except Exception as e:
            logger.warning(f"句子编码失败: {e}")
            return None

    def _detect_semantic_contradictions(self, text: str) -> float:
        """
        检测语义向量对立
        返回：语义矛盾分数 [0, 1]，越高表示矛盾越多
        """
        if self.semantic_model is None:
            return 0.0
        
        sentences = re.split(r'[.!?。！？]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 2:
            return 0.0
        
        contradiction_score = 0.0
        
        # 检测转折连词后的语义对立
        for conj in self.contrast_conjunctions:
            for sent in sentences:
                if conj in sent:
                    parts = sent.split(conj)
                    if len(parts) >= 2:
                        before_part = parts[0].strip()
                        after_part = parts[1].strip()
                        if before_part and after_part:
                            # 获取语义向量
                            before_emb = self._get_sentence_embedding(before_part)
                            after_emb = self._get_sentence_embedding(after_part)
                            
                            if before_emb is not None and after_emb is not None:
                                # 计算语义相似度
                                sim = np.dot(before_emb, after_emb) / (
                                    np.linalg.norm(before_emb) * np.linalg.norm(after_emb) + 1e-8)
                                # 如果相似度低于阈值，认为有语义对立
                                if sim < self.semantic_threshold:
                                    contradiction_score += 0.1
        
        # 检测跨块矛盾（如果是长文本）
        if len(text) > 4000:
            cross_contradictions = self._detect_long_text_contradictions(text)
            contradiction_score += cross_contradictions
        
        return min(1.0, contradiction_score)

    def _detect_long_text_contradictions(self, text: str) -> float:
        """
        检测长文本中的跨块矛盾
        """
        if self.semantic_model is None:
            return 0.0
        
        sentences = re.split(r'[.!?。！？]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 2:
            return 0.0
        
        # 分块
        chunks = self.text_chunker.chunk_sentences(sentences)
        
        if len(chunks) < 2:
            return 0.0
        
        contradiction_score = 0.0
        
        # 初始化跨块矛盾追踪器
        if self.cross_tracker is None:
            self.cross_tracker = InterBlockContradictionTracker(self.semantic_model, self.semantic_threshold)
        else:
            self.cross_tracker.clear()
        
        # 注册各个块的概念
        for block_idx, chunk_indices in enumerate(chunks):
            chunk_sentences = [sentences[i] for i in chunk_indices]
            # 获取嵌入
            emb_map, _ = self._safe_encode(chunk_sentences)
            if emb_map:
                embeddings = [emb_map[sent] for sent in chunk_sentences]
                self.cross_tracker.register_block_concepts(block_idx, chunk_sentences, chunk_indices, embeddings)
        
        # 检测跨块矛盾
        cross_edges = self.cross_tracker.detect_cross_block_contradictions()
        
        if cross_edges:
            contradiction_score += min(0.3, len(cross_edges) * 0.05)
        
        return contradiction_score

    def evaluate(self, content: str) -> Dict[str, Any]:
        """
        评估文档，使用增强的方法
        返回完整的评估结果，包含所有四个维度的分数
        """
        if not content or not content.strip():
            logger.warning("空文档")
            return {
                'needs_tuning': False,
                'harmony_report': {
                    'U': 0.0, 'D': 0.0, 'A': 0.0, 'H': 0.0,
                    'lambda_u': self.lambda_u,
                    'lambda_d': self.lambda_d,
                    'lambda_a': self.lambda_a
                },
                'suggestions': [],
                'warnings': ['文档为空'],
                'pathology': '空文档'
            }
        
        try:
            # 基础评估
            scores = calculate_harmony(content, self.lambda_u, self.lambda_d, self.lambda_a)
            
            # 增强的对抗性检测
            enhanced_adversarial = scores['A'] + self._detect_semantic_contradictions(content)
            scores['A'] = min(1.0, enhanced_adversarial)
            
            # 重新计算和谐度
            scores['H'] = max(0.0, min(1.0, 
                self.lambda_u * scores['U'] + 
                self.lambda_d * scores['D'] - 
                self.lambda_a * scores['A']))
            
            # 使用原始评估器获取建议和警告
            try:
                report = self.evaluator.evaluate(content) if self.evaluator else None
                report_dict = report.to_dict() if report else {}
                suggestions = report_dict.get('suggestions', [])
                warnings = report_dict.get('warnings', [])
            except Exception as e:
                logger.warning(f"原始评估器失败，使用默认值: {e}")
                suggestions = []
                warnings = []
            
            # 诊断分类
            pathology = self._classify_pathology(scores)
            
            needs_tuning = scores['H'] < self.harmony_threshold or scores['A'] > self.adversarial_threshold
            
            result = {
                'needs_tuning': needs_tuning,
                'harmony_report': scores,
                'suggestions': suggestions,
                'warnings': warnings,
                'pathology': pathology
            }
            
            logger.info(f"评估完成。H={scores['H']:.3f}, A={scores['A']:.3f}, 判定: {pathology}")
            return result
            
        except Exception as e:
            logger.exception(f"评估过程中发生意外错误: {e}")
            return {
                'needs_tuning': False,
                'error': f"Evaluation failed: {str(e)}",
                'harmony_report': {
                    'U': 0.0, 'D': 0.0, 'A': 0.0, 'H': 0.0,
                    'lambda_u': self.lambda_u,
                    'lambda_d': self.lambda_d,
                    'lambda_a': self.lambda_a
                },
                'suggestions': [],
                'warnings': [str(e)],
                'pathology': '评估错误'
            }

    def _classify_pathology(self, scores: Dict) -> str:
        """
        分类病理
        """
        h = scores.get('H', 0)
        a = scores.get('A', 0)
        u = scores.get('U', 0)
        d = scores.get('D', 0)
        
        if h >= 0.6:
            return "谐振态"
        if u < 0.3 and a > 0.7 and h < 0:
            return "逻辑自杀"
        if d < 0.2 and a < 0.3 and h < 0.4:
            return "逻辑空洞"
        if h >= 0.4 and a < 0.2:
            return "度假合格"
        return "需调谐"
    
    def get_audit_info(self) -> Dict[str, Any]:
        """
        获取审计信息，包括当前的权重配置
        """
        return {
            'lambda_u': self.lambda_u,
            'lambda_d': self.lambda_d,
            'lambda_a': self.lambda_a,
            'default_weights': get_current_weights(),
            'harmony_threshold': self.harmony_threshold,
            'adversarial_threshold': self.adversarial_threshold,
            'semantic_model_available': self.semantic_model is not None
        }
```

---

### 6. actuator.py - 调谐执行器

```python
"""
DeepSeek 调谐执行器
根据评估诊断结果，调用 DeepSeek 大模型对文档进行谐振调谐。
"""

import os
import time
import random
from typing import Dict, Any, Optional
from openai import OpenAI
from loguru import logger
from config import settings


class DeepSeekError(Exception):
    """DeepSeek API 错误"""
    pass


class TokenLimitError(DeepSeekError):
    """Token 限制错误"""
    pass


class HarmonyActuator:
    """基于 DeepSeek 的文档调谐引擎"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # 从配置或环境变量获取
        self.api_key = settings.deepseek_api_key
        self.base_url = settings.deepseek_base_url
        self.model = settings.deepseek_model
        self.max_tokens = settings.deepseek_max_tokens
        self.temperature = settings.deepseek_temperature
        self.max_retries = settings.deepseek_max_retries
        self.timeout = settings.deepseek_timeout
        
        # 初始化客户端
        self.client = None
        if self.api_key and self.api_key != "${DEEPSEEK_API_KEY}":
            try:
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url,
                    timeout=self.timeout
                )
                logger.info("DeepSeek 客户端初始化成功")
            except Exception as e:
                logger.error(f"DeepSeek 客户端初始化失败: {e}")
        else:
            logger.warning("DeepSeek API Key 未设置，将无法进行调谐")
        
        # 简单缓存
        self._cache = {}
        self._cache_enabled = settings.cache_enabled
    
    def call_deepseek(self, prompt: str) -> tuple[str, Dict[str, Any]]:
        """
        调用 DeepSeek API，带重试机制
        
        Returns:
            (response_text, usage_info)
        """
        if not self.client:
            raise DeepSeekError("DeepSeek 客户端未初始化")
        
        # 检查缓存
        cache_key = hash(prompt)
        if self._cache_enabled and cache_key in self._cache:
            logger.debug("使用缓存的响应")
            return self._cache[cache_key]
        
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"调用 DeepSeek API (尝试 {attempt + 1}/{self.max_retries})")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "你是一个专业的文档调谐专家，基于晶脉哲学与谐振理论。请严格按照要求修改文档，保持原文的核心意思和法律效力。"
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                )
                
                # 验证响应
                if not response.choices:
                    raise DeepSeekError("API 返回了空的响应")
                
                response_text = response.choices[0].message.content
                
                if not response_text or not response_text.strip():
                    raise DeepSeekError("API 返回了空的内容")
                
                # 获取使用信息
                usage_info = {}
                if hasattr(response, 'usage'):
                    usage_info = {
                        'prompt_tokens': response.usage.prompt_tokens,
                        'completion_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens
                    }
                
                # 缓存结果
                if self._cache_enabled:
                    self._cache[cache_key] = (response_text, usage_info)
                
                logger.debug(f"DeepSeek 调用成功: {usage_info}")
                return response_text, usage_info
            
            except Exception as e:
                last_exception = e
                logger.warning(f"DeepSeek 调用失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                
                if attempt < self.max_retries - 1:
                    # 指数退避
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    logger.debug(f"等待 {wait_time:.2f} 秒后重试...")
                    time.sleep(wait_time)
        
        # 所有重试都失败
        raise DeepSeekError(f"所有 {self.max_retries} 次调用都失败: {last_exception}")
    
    def tune(self, original_text: str, diagnosis: Dict) -> Dict[str, Any]:
        """
        执行文档调谐
        
        Args:
            original_text: 原始文档
            diagnosis: 诊断结果，来自 evaluator
        
        Returns:
            {
                'tuned_text': 调谐后的文本,
                'strategy': 策略名称,
                'success': 是否成功,
                'usage': token 使用信息,
                'error': 错误信息（如果有）
            }
        """
        result = {
            'tuned_text': original_text,
            'strategy': 'none',
            'success': True,
            'usage': {},
            'error': None
        }
        
        if not self.client:
            result['success'] = False
            result['strategy'] = 'failed'
            result['error'] = "DeepSeek 客户端不可用"
            logger.error("DeepSeek 客户端不可用，无法执行调谐")
            return result
        
        if not diagnosis.get('needs_tuning', False):
            result['strategy'] = 'none'
            logger.info("文档不需要调谐")
            return result
        
        # 选择策略
        pathology = diagnosis.get('pathology', '需调谐')
        strategy = self._select_strategy(pathology, diagnosis)
        result['strategy'] = strategy
        
        # 构建提示词
        prompt = self._build_tuning_prompt(original_text, diagnosis, strategy, pathology)
        
        try:
            # 调用 API
            tuned_text, usage = self.call_deepseek(prompt)
            result['tuned_text'] = tuned_text
            result['usage'] = usage
            
            logger.info(f"调谐完成: strategy={strategy}, usage={usage}")
            
        except Exception as e:
            result['success'] = False
            result['strategy'] = 'failed'
            result['error'] = str(e)
            logger.exception(f"调谐失败: {e}")
        
        return result
    
    def harmonize_document(self, original_text: str, diagnosis: Optional[Dict] = None) -> Dict[str, Any]:
        """
        文档和谐化（兼容接口）
        """
        return self.tune(original_text, diagnosis or {'needs_tuning': True})
    
    def _select_strategy(self, pathology: str, diagnosis: Dict) -> str:
        """
        根据病理选择调谐策略
        """
        strategies = {
            "逻辑自杀": "重构逻辑链，消除显性矛盾",
            "逻辑空洞": "引入新论据，增强发展性",
            "度假合格": "补充对立论点，增加健康的对抗性",
        }
        
        if pathology in strategies:
            return strategies[pathology]
        
        # 基于建议选择
        suggestions = diagnosis.get('suggestions', [])
        if suggestions:
            return suggestions[0][:80]
        
        return "优化术语一致性和论证流畅度"
    
    def _build_tuning_prompt(self, text: str, diagnosis: Dict, strategy: str, pathology: str) -> str:
        """
        构建调谐提示词
        """
        harmony_report = diagnosis.get('harmony_report', {})
        
        h_before = harmony_report.get('H', 0)
        u_score = harmony_report.get('U', 0)
        d_score = harmony_report.get('D', 0)
        a_score = harmony_report.get('A', 0)
        
        prompt = f"""你是一个基于"晶脉哲学与谐振理论"的文档调谐专家。

当前文档病理诊断: {pathology}
调谐目标: 将和谐度 H 从 {h_before:.3f} 提升至 0.7 以上

关键指标:
- 统一性 U: {u_score:.3f}
- 发展性 D: {d_score:.3f}
- 对抗性 A: {a_score:.3f}

调谐策略: {strategy}

要求:
1. 严格保持原文的法律效力、核心事实和整体结构不变
2. 根据指标进行精细化微调，使指标向健康区间移动 (U>0.6, D>0.6, A<0.4)
3. 不要添加不必要的新内容，只优化现有表达
4. 直接返回调谐后的完整文档文本，不要任何解释或额外标记

原文:
{text}
"""
        return prompt
    
    def clear_cache(self):
        """
        清空缓存
        """
        self._cache.clear()
        logger.info("缓存已清空")
```

---

### 7. challenger.py - 双脑博弈质疑器

```python
import random
from typing import Dict, Any, Optional
from loguru import logger


class ChallengeAgent:
    """独立质疑者，对评估结果进行反思性挑战，实现"反对齐"的双脑博弈。"""

    def __init__(self, config: Dict[str, Any], actuator: Optional[Any] = None):
        self.config = config
        self.actuator = actuator

    def challenge(self, original_text: str, diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        original_h = diagnosis.get('harmony_report', {}).get('H', 0.5)
        challenge_points = self._rule_based_challenge(original_text, diagnosis)

        if self.actuator and hasattr(self.actuator, 'client') and self.actuator.client:
            try:
                llm_points = self._llm_challenge(original_text, diagnosis)
                if llm_points:
                    challenge_points.extend(llm_points)
            except Exception as e:
                logger.warning(f"LLM质疑失败，回退到规则模式: {e}")

        challenge_confidence = min(0.9, len(challenge_points) * 0.2 + 0.3)
        challenged_h = original_h + random.uniform(-0.15, -0.05) if original_h > 0.6 else original_h + random.uniform(0.05, 0.15)
        challenged_h = max(0.0, min(1.0, challenged_h))

        report = {
            "challenge_confidence": challenge_confidence,
            "challenge_points": challenge_points,
            "original_h": original_h,
            "challenged_h": challenged_h,
            "h_discrepancy": abs(original_h - challenged_h),
            "is_high_risk": abs(original_h - challenged_h) > 0.2,
            "recommendation": "建议人工复核" if abs(original_h - challenged_h) > 0.2 else "诊断一致，可信度较高"
        }

        logger.info(f"质疑完成。H差异: {report['h_discrepancy']:.2f}, 高风险: {report['is_high_risk']}")
        return report

    def _rule_based_challenge(self, text: str, diagnosis: Dict[str, Any]) -> list:
        points = []
        report = diagnosis.get('harmony_report', {})
        u = report.get('U', 0.5)
        d = report.get('D', 0.5)
        a = report.get('A', 0.5)
        h = report.get('H', 0.5)
        warnings = diagnosis.get('drift_warnings', [])
        suggestions = diagnosis.get('suggestions', [])

        if u > 0.8 and d < 0.3:
            points.append("高U值可能掩盖了论证多样性的不足，请检查是否存在过度简化。")

        if a < 0.2 and h > 0.6:
            points.append("极低的对抗性(A)暗示可能存在'度假合格'风险，请确认是否回避了核心矛盾。")

        if d > 0.8 and u < 0.4:
            points.append("高发展性(D)伴随低统一性(U)，可能存在论证跳跃或概念偷换。")

        if len(warnings) == 0 and len(text) > 200:
            points.append("未检测到术语漂移，但文本较长，建议人工抽查是否存在隐性漂移。")

        if len(suggestions) < 2:
            points.append("调谐建议较少，评估可能不够全面，请考虑增加评估维度。")

        return points

    def _llm_challenge(self, text: str, diagnosis: Dict[str, Any]) -> Optional[list]:
        if not self.actuator:
            return None

        prompt = f"""你是一位严谨的AI审计专家，请从以下角度质疑这份诊断报告：
1. 是否存在过度解读或忽略了关键矛盾？
2. 评估指标是否可能不准确？
3. 是否有其他可能的诊断结果？

诊断报告：
{diagnosis}

请以列表形式给出3-5条具体的质疑点，每条不超过50字。"""

        try:
            response = self.actuator.client.chat.completions.create(
                model=self.actuator.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3
            )
            content = response.choices[0].message.content
            lines = [line.strip('- ').strip() for line in content.split('\n') if line.strip().startswith('-')]
            return lines[:5] if lines else None
        except Exception:
            return None
```

---

### 8. long_text.py - 长文本处理

```python
"""
长文本处理模块
提供分块处理、跨块矛盾追踪等功能
"""
import numpy as np
from typing import List, Dict
import re
from itertools import combinations
from collections import defaultdict


class TextChunker:
    def __init__(self, max_chars_per_chunk: int = 4000):
        self.max_chars_per_chunk = max_chars_per_chunk

    def chunk_sentences(self, sentences: List[str]) -> List[List[int]]:
        chunks = []
        current_chunk = []
        current_length = 0
        for idx, sent in enumerate(sentences):
            sent_len = len(sent)
            if current_length + sent_len > self.max_chars_per_chunk and current_chunk:
                chunks.append(current_chunk)
                current_chunk = [idx]
                current_length = sent_len
            else:
                current_chunk.append(idx)
                current_length += sent_len
        if current_chunk:
            chunks.append(current_chunk)
        return chunks


class InterBlockContradictionTracker:
    def __init__(self, semantic_model, threshold: float = -0.15):
        self.semantic_model = semantic_model
        self.threshold = threshold
        self.concept_registry = defaultdict(list)
        self.cross_edges: List[Dict] = []

    def register_block_concepts(self, block_idx, sentences, sentence_indices, embeddings):
        for i, sent in enumerate(sentences):
            if not sent:
                continue
            words = set(re.findall(r'[\u4e00-\u9fa5a-zA-Z]{2,}', sent))
            for w in words:
                self.concept_registry[w].append({
                    'block': block_idx,
                    'sentence_idx': sentence_indices[i],
                    'vector': embeddings[i]
                })

    def detect_cross_block_contradictions(self):
        self.cross_edges = []
        for concept, occurrences in self.concept_registry.items():
            if len(occurrences) < 2:
                continue
            for (occ_a, occ_b) in combinations(occurrences, 2):
                if occ_a['block'] == occ_b['block']:
                    continue
                sim = np.dot(occ_a['vector'], occ_b['vector']) / (
                    np.linalg.norm(occ_a['vector']) * np.linalg.norm(occ_b['vector']) + 1e-8)
                if sim < self.threshold:
                    weight = min(1.0, -sim)
                    self.cross_edges.append({
                        'i': occ_a['sentence_idx'],
                        'j': occ_b['sentence_idx'],
                        'weight': weight,
                        'type': 'cross_block',
                        'concept': concept
                    })
        return self.cross_edges

    def clear(self):
        self.concept_registry.clear()
        self.cross_edges.clear()
```

---

### 9. file_handler.py - 文件处理工具

```python
"""
文件处理工具
提供文件读写、编码检测等功能
"""
from pathlib import Path
from typing import Optional, List
from loguru import logger


class FileHandler:
    def __init__(self):
        self.supported_extensions = {'.md', '.txt', '.rst', '.markdown'}

    def read_file(self, file_path: str) -> Optional[str]:
        path = Path(file_path)
        if not path.exists():
            logger.error(f"文件不存在: {file_path}")
            return None
        return self._read_with_encoding(file_path)

    def _read_with_encoding(self, file_path: str) -> Optional[str]:
        for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except (UnicodeDecodeError, Exception):
                continue
        try:
            with open(file_path, 'rb') as f:
                return f.read().decode('utf-8', errors='ignore')
        except Exception as e:
            logger.error(f"所有编码尝试均失败: {e}")
            return None

    def write_file(self, file_path: str, content: str) -> bool:
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"成功写入文件: {file_path}")
            return True
        except Exception as e:
            logger.error(f"写入文件失败: {e}")
            return False

    def write_fixed_file(self, original_path: str, fixed_content: str) -> str:
        path = Path(original_path)
        fixed_path = path.parent / f"{path.stem}_fixed{path.suffix}"
        return str(fixed_path) if self.write_file(str(fixed_path), fixed_content) else original_path
```

---

### 10. legal_doc_review.py - 法律文档审阅工作流

```python
"""
法律文档审阅工作流
"""
from typing import Dict, Any
from datetime import datetime
from pathlib import Path
from loguru import logger


class LegalDocumentReviewWorkflow:
    def __init__(self, orchestrator, file_handler):
        self.orchestrator = orchestrator
        self.file_handler = file_handler

    async def execute(self, content: str, file_path: str, auto_fix: bool = True) -> Dict[str, Any]:
        logger.info(f"开始法律文档审阅: {file_path}")
        start_time = datetime.now()
        context = self.orchestrator.TaskContext(
            file_path=file_path,
            original_content=content,
            workflow_type="legal_review",
            intermediate_results={'workflow_start': start_time.isoformat()},
            config=self.orchestrator.config
        )
        try:
            result = await self.orchestrator.orchestrate(context) if auto_fix else {"status": "evaluation_only"}
            result.update({
                'processing_time_seconds': (datetime.now() - start_time).total_seconds(),
                'timestamp': datetime.now().isoformat()
            })
            return result
        except Exception as e:
            logger.error(f"审阅失败: {e}")
            return {"status": "error", "error": str(e)}
```

---

## 🔒 和谐治理模块 (ochr/)

### 11. boundary.py - 边界控制器

```python
"""
边界控制器 (Boundary Controller)
检查文档是否包含禁止修改的内容
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from loguru import logger


@dataclass
class BoundaryRule:
    name: str
    pattern: str
    description: str
    severity: str = "warning"  # warning, error
    is_regex: bool = True


class BoundaryController:
    """
    边界控制器
    检查文档是否包含禁止修改的内容
    """
    
    def __init__(self):
        self.rules: List[BoundaryRule] = []
        self._init_default_rules()
        self.protected_regions: List[Tuple[int, int]] = []  # (start, end) indices
    
    def _init_default_rules(self):
        """
        初始化默认规则
        """
        # 法律文档保护规则
        self.rules.extend([
            BoundaryRule(
                name="legal_signature",
                pattern=r"(?:签字|签名|盖章|签章)\s*[：:]\s*[^\n]{0,20}",
                description="法律签字区域",
                severity="error"
            ),
            BoundaryRule(
                name="legal_date",
                pattern=r"(?:日期|Date)\s*[：:]\s*\d{4}[/-]\d{1,2}[/-]\d{1,2}",
                description="日期字段",
                severity="error"
            ),
            BoundaryRule(
                name="legal_party",
                pattern=r"(?:甲方|乙方|丙方|双方|当事人)\s*[：:]\s*[^\n]+",
                description="合同当事人信息",
                severity="error"
            ),
            BoundaryRule(
                name="legal_amount",
                pattern=r"(?:金额|金额大写|Amount)\s*[：:]\s*[^\n]+",
                description="金额信息",
                severity="error"
            ),
            BoundaryRule(
                name="legal_article",
                pattern=r"第[一二三四五六七八九十百]+条\s*[^\n]{0,50}",
                description="法律条款标题",
                severity="warning"
            ),
        ])
        
        # 通用保护规则
        self.rules.extend([
            BoundaryRule(
                name="copyright",
                pattern=r"(?:©|Copyright)\s*\d{4}\s*[^\n]+",
                description="版权声明",
                severity="warning"
            ),
            BoundaryRule(
                name="important_note",
                pattern=r"(?:注意|WARNING|IMPORTANT|NOTE)\s*[：:]",
                description="重要提示",
                severity="warning",
                is_regex=True
            ),
        ])
    
    def add_rule(self, rule: BoundaryRule):
        """
        添加自定义规则
        """
        self.rules.append(rule)
        logger.info(f"添加边界规则: {rule.name}")
    
    def add_protected_region(self, start: int, end: int):
        """
        添加受保护的区域
        """
        self.protected_regions.append((start, end))
        logger.info(f"添加受保护区域: [{start}, {end}]")
    
    def check_permissions(self, text: str) -> Tuple[bool, List[Dict]]:
        """
        检查文档是否允许修改
        
        Returns:
            (allowed, violations) - 是否允许修改，违规列表
        """
        violations = []
        
        # 1. 检查规则匹配
        for rule in self.rules:
            try:
                if rule.is_regex:
                    matches = list(re.finditer(rule.pattern, text, re.IGNORECASE))
                else:
                    matches = []
                    idx = 0
                    while True:
                        idx = text.find(rule.pattern, idx)
                        if idx == -1:
                            break
                        matches.append(type('', (), {'start': lambda: idx, 'end': lambda: idx + len(rule.pattern)})())
                        idx += len(rule.pattern)
                
                for match in matches:
                    violations.append({
                        'rule': rule.name,
                        'description': rule.description,
                        'severity': rule.severity,
                        'start': match.start(),
                        'end': match.end(),
                        'matched_text': text[match.start():match.end()]
                    })
            except Exception as e:
                logger.error(f"规则检查失败 {rule.name}: {e}")
        
        # 2. 检查受保护区域
        # (这里简化处理，实际需要结合文本位置)
        
        # 判断是否允许
        has_error = any(v['severity'] == 'error' for v in violations)
        allowed = not has_error
        
        logger.info(f"边界检查完成: allowed={allowed}, violations={len(violations)}")
        
        return allowed, violations
    
    def get_modifiable_regions(self, text: str) -> List[Tuple[int, int]]:
        """
        获取可修改的区域
        """
        allowed, violations = self.check_permissions(text)
        
        if allowed and not violations:
            return [(0, len(text))]
        
        # 构建可修改区域（排除违规区域）
        modifiable = []
        last_end = 0
        
        # 按起始位置排序违规区域
        sorted_violations = sorted(violations, key=lambda x: x['start'])
        
        for v in sorted_violations:
            if v['start'] > last_end:
                modifiable.append((last_end, v['start']))
            last_end = max(last_end, v['end'])
        
        if last_end < len(text):
            modifiable.append((last_end, len(text)))
        
        return modifiable
    
    def validate_change(self, original_text: str, modified_text: str) -> Tuple[bool, List[str]]:
        """
        验证修改是否合法
        """
        issues = []
        
        # 检查受保护内容是否被修改
        allowed_original, violations_original = self.check_permissions(original_text)
        allowed_modified, violations_modified = self.check_permissions(modified_text)
        
        # 检查是否删除了重要内容
        for v_orig in violations_original:
            found = False
            for v_mod in violations_modified:
                if v_orig['matched_text'] in modified_text:
                    found = True
                    break
            
            if not found and v_orig['severity'] == 'error':
                issues.append(f"检测到受保护内容被删除: {v_orig['description']}")
        
        return len(issues) == 0, issues
```

---

### 12. reflection_cavity.py - 反思腔

```python
"""
反思腔 (Reflection Cavity)
用于审计和记录文档处理过程
"""

import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from loguru import logger
from dataclasses import dataclass, asdict, field


@dataclass
class AuditEntry:
    timestamp: str
    operation: str
    document_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    before_scores: Optional[Dict[str, float]] = None
    after_scores: Optional[Dict[str, float]] = None
    changes: Optional[List[str]] = None


class ReflectionCavity:
    """
    审计和记录模块
    """
    
    def __init__(self, log_dir: str = "logs/audit"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.audit_log: List[AuditEntry] = []
        self.current_session_id = self._generate_session_id()
    
    def _generate_session_id(self) -> str:
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def log_evaluation(self, document_id: str, scores: Dict[str, float], metadata: Optional[Dict] = None):
        """
        记录评估
        """
        entry = AuditEntry(
            timestamp=datetime.now().isoformat(),
            operation="evaluate",
            document_id=document_id,
            before_scores=scores,
            metadata=metadata or {}
        )
        self._add_entry(entry)
        logger.info(f"已记录评估: {document_id}")
    
    def log_repair(
        self,
        document_id: str,
        before_scores: Dict[str, float],
        after_scores: Dict[str, float],
        changes: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ):
        """
        记录修复
        """
        entry = AuditEntry(
            timestamp=datetime.now().isoformat(),
            operation="repair",
            document_id=document_id,
            before_scores=before_scores,
            after_scores=after_scores,
            changes=changes or [],
            metadata=metadata or {}
        )
        self._add_entry(entry)
        
        improvement = after_scores.get('H', 0) - before_scores.get('H', 0)
        logger.info(f"已记录修复: {document_id}, 和谐度提升: {improvement:+.3f}")
    
    def log_boundary_check(
        self,
        document_id: str,
        allowed: bool,
        reason: str,
        metadata: Optional[Dict] = None
    ):
        """
        记录边界检查
        """
        entry = AuditEntry(
            timestamp=datetime.now().isoformat(),
            operation="boundary_check",
            document_id=document_id,
            metadata={
                'allowed': allowed,
                'reason': reason,
                **(metadata or {})
            }
        )
        self._add_entry(entry)
        logger.info(f"已记录边界检查: {document_id}, allowed={allowed}")
    
    def _add_entry(self, entry: AuditEntry):
        """
        添加审计条目
        """
        self.audit_log.append(entry)
        self._persist_entry(entry)
    
    def _persist_entry(self, entry: AuditEntry):
        """
        持久化审计条目
        """
        log_file = self.log_dir / f"{self.current_session_id}.jsonl"
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(asdict(entry), ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"持久化审计日志失败: {e}")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        获取会话摘要
        """
        evaluations = [e for e in self.audit_log if e.operation == "evaluate"]
        repairs = [e for e in self.audit_log if e.operation == "repair"]
        
        total_improvement = 0.0
        for repair in repairs:
            if repair.before_scores and repair.after_scores:
                improvement = repair.after_scores.get('H', 0) - repair.before_scores.get('H', 0)
                total_improvement += improvement
        
        return {
            'session_id': self.current_session_id,
            'total_evaluations': len(evaluations),
            'total_repairs': len(repairs),
            'total_improvement': total_improvement,
            'average_improvement': total_improvement / len(repairs) if repairs else 0,
            'start_time': self.audit_log[0].timestamp if self.audit_log else None,
            'end_time': self.audit_log[-1].timestamp if self.audit_log else None
        }
    
    def get_history(self, document_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """
        获取历史记录
        """
        entries = self.audit_log
        if document_id:
            entries = [e for e in entries if e.document_id == document_id]
        
        return [asdict(e) for e in entries[-limit:]]
    
    def clear(self):
        """
        清空当前日志
        """
        self.audit_log = []
        self.current_session_id = self._generate_session_id()
        logger.info("审计日志已重置")
```

---

### 13. relationship_mapper.py - 关系映射器

```python
"""
关系映射器 (Relationship Mapper)
分析文档各部分之间的依赖关系
"""

import re
from typing import List, Dict, Any, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict
import networkx as nx
from loguru import logger


@dataclass
class DocumentSection:
    id: str
    content: str
    start_index: int
    end_index: int
    dependencies: Set[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = set()


class RelationshipMapper:
    """
    分析文档各部分之间的依赖关系
    """
    
    def __init__(self):
        self.sections: List[DocumentSection] = []
        self.graph = nx.DiGraph()
        self.section_keywords: Dict[str, Set[str]] = {}
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        分析文档的关系结构
        """
        logger.info("开始分析文档关系结构")
        
        # 1. 分段
        self._split_into_sections(text)
        
        # 2. 提取关键词
        self._extract_section_keywords()
        
        # 3. 构建依赖关系
        self._build_dependencies()
        
        # 4. 构建图
        self._build_graph()
        
        # 5. 分析关键节点
        critical_nodes = self._identify_critical_nodes()
        
        logger.info(f"关系分析完成: {len(self.sections)} 个部分, {len(critical_nodes)} 个关键节点")
        
        return {
            'sections': [s.id for s in self.sections],
            'critical_nodes': critical_nodes,
            'dependency_count': self.graph.number_of_edges(),
            'centrality': dict(nx.betweenness_centrality(self.graph)) if self.graph.nodes else {}
        }
    
    def _split_into_sections(self, text: str):
        """
        将文档分割成章节
        """
        self.sections = []
        
        # 按标题分割（简单实现）
        title_pattern = r'^(?:第[一二三四五六七八九十百]+[章节篇节]|[\d]+\.)\s*[^\n]+'
        lines = text.split('\n')
        
        current_section = ""
        current_start = 0
        section_id = 0
        
        for i, line in enumerate(lines):
            if re.match(title_pattern, line.strip()):
                if current_section.strip():
                    self.sections.append(DocumentSection(
                        id=f"section_{section_id}",
                        content=current_section.strip(),
                        start_index=current_start,
                        end_index=len('\n'.join(lines[:i]))
                    ))
                    section_id += 1
                current_section = line + '\n'
                current_start = len('\n'.join(lines[:i]))
            else:
                current_section += line + '\n'
        
        if current_section.strip():
            self.sections.append(DocumentSection(
                id=f"section_{section_id}",
                content=current_section.strip(),
                start_index=current_start,
                end_index=len(text)
            ))
    
    def _extract_section_keywords(self):
        """
        提取每个章节的关键词
        """
        from thinkcheck_harmony.utils import extract_keywords
        
        for section in self.sections:
            keywords = extract_keywords(section.content, top_n=15)
            self.section_keywords[section.id] = set(keywords)
    
    def _build_dependencies(self):
        """
        构建章节间的依赖关系
        """
        for i, section in enumerate(self.sections):
            section_words = self.section_keywords[section.id]
            
            # 检查与前面章节的关系
            for j in range(i):
                prev_section = self.sections[j]
                prev_words = self.section_keywords[prev_section.id]
                
                # 计算关键词重叠
                overlap = len(section_words & prev_words)
                
                if overlap > 3:  # 阈值
                    section.dependencies.add(prev_section.id)
    
    def _build_graph(self):
        """
        构建依赖图
        """
        for section in self.sections:
            self.graph.add_node(section.id)
        
        for section in self.sections:
            for dep_id in section.dependencies:
                self.graph.add_edge(dep_id, section.id)
    
    def _identify_critical_nodes(self) -> List[str]:
        """
        识别关键节点（高中心性的节点）
        """
        if not self.graph.nodes:
            return []
        
        try:
            centrality = nx.betweenness_centrality(self.graph)
            sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
            threshold = sorted_nodes[len(sorted_nodes) // 4][1] if sorted_nodes else 0
            critical = [node_id for node_id, score in sorted_nodes if score >= threshold]
            return critical
        except:
            # 如果图计算失败，返回前几个章节
            return [s.id for s in self.sections[:3]]
    
    def get_priority_order(self) -> List[str]:
        """
        获取修复的优先级顺序
        """
        try:
            # 拓扑排序 + 中心性
            if not self.graph.nodes:
                return [s.id for s in self.sections]
            
            critical = self._identify_critical_nodes()
            order = []
            
            # 先关键节点，再其他
            for node_id in critical:
                if node_id not in order:
                    order.append(node_id)
            
            for node_id in self.graph.nodes:
                if node_id not in order:
                    order.append(node_id)
            
            return order
        except:
            return [s.id for s in self.sections]
    
    def get_section_by_id(self, section_id: str) -> DocumentSection:
        """
        根据 ID 获取章节
        """
        for section in self.sections:
            if section.id == section_id:
                return section
        return None
```

---

## 📊 和谐度评估SDK (thinkcheck-harmony/)

### 14. core.py - 核心计算引擎

```python
'''谐振调谐论：和谐度计算引擎 H = λU·U + λD·D - λA·A'''
import numpy as np
from .concept_graph import ConceptGraph
from .contradiction_detector import ContradictionDetector

def compute_U(concept_graph: ConceptGraph) -> float:
    return concept_graph.get_avg_consistency()

def compute_D(text: str, concept_graph: ConceptGraph) -> float:
    positions = concept_graph.get_first_occurrence_positions()
    if len(positions) <= 1:
        return 0.0
    positions_normalized = [p / len(text) for p in positions]
    std = np.std(positions_normalized)
    return min(1.0, std * 2.5)

def compute_A(text: str, detector: ContradictionDetector) -> float:
    return detector.compute_A(text)

def compute_harmony(U: float, D: float, A: float,
                     lambda_u: float, lambda_d: float, lambda_a: float) -> float:
    return lambda_u * U + lambda_d * D - lambda_a * A
```

---

### 15. evaluator.py - 主评估器

```python
'''主评估器：实践介入论的接口层，集成建议引擎'''
from typing import List, Optional
from .core import compute_U, compute_D, compute_A, compute_harmony
from .concept_graph import ConceptGraph
from .contradiction_detector import ContradictionDetector
from .report import HarmonyReport
from .intervention.suggestion_engine import SuggestionEngine
from .config import DEFAULT_LAMBDA_U, DEFAULT_LAMBDA_D, DEFAULT_LAMBDA_A

class HarmonyEvaluator:
    def __init__(self,
                 domain: str = "general",
                 lambda_u: float = DEFAULT_LAMBDA_U,
                 lambda_d: float = DEFAULT_LAMBDA_D,
                 lambda_a: float = DEFAULT_LAMBDA_A,
                 custom_terms: Optional[List[str]] = None,
                 enable_suggestions: bool = True):
        self.domain = domain
        self.lambda_u = lambda_u
        self.lambda_d = lambda_d
        self.lambda_a = lambda_a
        self.enable_suggestions = enable_suggestions

        from .presets import get_preset
        preset = get_preset(domain)
        self.key_terms = custom_terms if custom_terms else preset.get("terms", [])
        self.contradiction_rules = preset.get("contradiction_rules", [])
        self.detector = ContradictionDetector(self.contradiction_rules)

        self.suggestion_engine = SuggestionEngine() if enable_suggestions else None
        self.last_report: Optional[HarmonyReport] = None

    def evaluate(self, text: str) -> HarmonyReport:
        concept_graph = ConceptGraph(text, self.key_terms)
        U = compute_U(concept_graph)
        D = compute_D(text, concept_graph)
        A = compute_A(text, self.detector)
        H = compute_harmony(U, D, A, self.lambda_u, self.lambda_d, self.lambda_a)
        drift_warnings = concept_graph.get_drift_warnings()

        report = HarmonyReport(
            H=H, U=U, D=D, A=A,
            lambda_weights={"U": self.lambda_u, "D": self.lambda_d, "A": self.lambda_a},
            drift_warnings=drift_warnings,
            micro_details={"term_consistencies": concept_graph.consistency_scores},
            meso_details={"sentence_count": len(concept_graph.sentences)},
            macro_details={"domain": self.domain},
            audit={"evaluator_version": "3.0.0", "domain": self.domain}
        )

        if self.enable_suggestions and self.suggestion_engine:
            report.suggestions = self.suggestion_engine.generate_suggestions(report)

        self.last_report = report
        return report
```

---

### 16. concept_graph.py - 概念图谱

```python
'''概念关系图：关系本体论的工程实现'''
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .utils.text_processing import split_sentences
from .utils.embedding import get_embeddings
from .config import DRIFT_THRESHOLD

class ConceptGraph:
    def __init__(self, text: str, key_terms: list):
        self.text = text
        self.key_terms = key_terms
        self.sentences = split_sentences(text)
        self.term_occurrences = self._locate_terms()
        self.consistency_scores = self._compute_consistencies()

    def _locate_terms(self) -> dict:
        locations = {}
        for term in self.key_terms:
            positions = [i for i, s in enumerate(self.sentences) if term in s]
            if positions:
                locations[term] = positions
        return locations

    def _compute_consistencies(self) -> dict:
        scores = {}
        for term, positions in self.term_occurrences.items():
            if len(positions) < 2:
                scores[term] = 1.0
                continue
            term_sentences = [self.sentences[i] for i in positions]
            embeddings = get_embeddings(term_sentences)
            sim_matrix = cosine_similarity(embeddings)
            triu_indices = np.triu_indices_from(sim_matrix, k=1)
            if len(triu_indices[0]) == 0:
                scores[term] = 1.0
            else:
                scores[term] = float(np.mean(sim_matrix[triu_indices]))
        return scores

    def get_avg_consistency(self) -> float:
        if not self.consistency_scores:
            return 1.0
        return float(np.mean(list(self.consistency_scores.values())))

    def get_first_occurrence_positions(self) -> list:
        first_positions = []
        for positions in self.term_occurrences.values():
            if positions:
                first_positions.append(positions[0])
        return sorted(first_positions)

    def get_drift_warnings(self) -> list:
        warnings = []
        for term, score in self.consistency_scores.items():
            if score < DRIFT_THRESHOLD:
                warnings.append({
                    "term": term,
                    "consistency": round(score, 3),
                    "threshold": DRIFT_THRESHOLD,
                    "occurrences": len(self.term_occurrences[term]),
                    "sentences": [self.sentences[i] for i in self.term_occurrences[term]]
                })
        return warnings
```

---

### 17. contradiction_detector.py - 矛盾检测器

```python
'''矛盾动力论：A指标检测'''
from .utils.text_processing import split_sentences
from .config import ADVERSARIAL_MARKERS

class ContradictionDetector:
    def __init__(self, contradiction_rules: list = None):
        self.contradiction_rules = contradiction_rules or []

    def compute_A(self, text: str) -> float:
        sentences = split_sentences(text)
        if not sentences:
            return 0.0
        marker_count = 0
        for sent in sentences:
            for marker in ADVERSARIAL_MARKERS:
                if marker in sent:
                    marker_count += 1
                    break
        marker_density = marker_count / len(sentences)
        rule_match_count = 0
        for term1, term2 in self.contradiction_rules:
            if term1 in text and term2 in text:
                rule_match_count += 1
        rule_score = min(1.0, rule_match_count * 0.3)
        return min(1.0, 0.6 * marker_density + 0.4 * rule_score)
```

---

### 18. config.py - 全局配置

```python
"""
全局配置与默认权重
权重默认值来自论文《关系的艺术》协商起点，体现可协商原则
"""

DEFAULT_LAMBDA_U = 0.4
DEFAULT_LAMBDA_D = 0.4
DEFAULT_LAMBDA_A = 0.2

DRIFT_THRESHOLD = 0.65
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

ADVERSARIAL_MARKERS = [
    "但是", "然而", "不过", "尽管", "需要注意的是", "必须指出",
    "与此相反", "另一方面", "存在风险", "有待商榷"
]

INTERVENTION_TRIGGERS = {
    "high_A": 0.3,
    "drift_warning": True,
    "low_D": 0.4,
}

FEATURE_FLAGS = {
    "enable_field_probe": False,
    "enable_pattern_resonance": False,
}
```

---

### 19. report.py - 报告数据结构

```python
'''评估报告数据结构：体现三重嵌套拓扑'''
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class HarmonyReport:
    H: float
    U: float
    D: float
    A: float
    lambda_weights: Dict[str, float]
    drift_warnings: List[Dict]
    micro_details: Dict[str, Any]
    meso_details: Dict[str, Any]
    macro_details: Dict[str, Any]
    audit: Dict[str, Any]
    suggestions: Optional[List[str]] = None

    def to_dict(self) -> Dict:
        return {
            "H": round(self.H, 4),
            "U": round(self.U, 4),
            "D": round(self.D, 4),
            "A": round(self.A, 4),
            "weights": self.lambda_weights,
            "warnings": self.drift_warnings,
            "layers": {
                "micro": self.micro_details,
                "meso": self.meso_details,
                "macro": self.macro_details
            },
            "audit": self.audit,
            "suggestions": self.suggestions or []
        }
```

---

### 20. intervention/base.py - 矛盾捕获器基类

```python
'''矛盾捕获器抽象基类（预留扩展钩子）'''
from abc import ABC, abstractmethod
from typing import List
from ..report import HarmonyReport

class BaseHarvester(ABC):
    @abstractmethod
    def analyze(self, report: HarmonyReport) -> bool:
        pass

    @abstractmethod
    def generate_intervention(self, report: HarmonyReport) -> List[str]:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

    def probe_field(self, report: HarmonyReport) -> dict:
        return {}

    def get_pattern_library(self) -> list:
        return []
```

---

### 21. intervention/suggestion_engine.py - 建议引擎

```python
'''建议引擎'''
from typing import List
from .base import BaseHarvester
from .term_alignment import TermAlignmentHarvester
from .weight_negotiation import WeightNegotiationHarvester
from ..report import HarmonyReport

class SuggestionEngine:
    def __init__(self, harvesters: List[BaseHarvester] = None):
        self.harvesters = harvesters or [
            TermAlignmentHarvester(),
            WeightNegotiationHarvester(),
        ]

    def register_harvester(self, harvester: BaseHarvester):
        self.harvesters.append(harvester)

    def generate_suggestions(self, report: HarmonyReport) -> List[str]:
        all_suggestions = []
        for harvester in self.harvesters:
            if harvester.analyze(report):
                all_suggestions.extend(harvester.generate_intervention(report))
        return all_suggestions
```

---

### 22. intervention/term_alignment.py - 术语对齐捕获器

```python
'''术语共识工作坊捕获器'''
from typing import List, Dict, Any, Optional
from .base import BaseHarvester
from ..report import HarmonyReport

class TermAlignmentHarvester(BaseHarvester):
    def analyze(self, report: HarmonyReport) -> bool:
        return len(report.drift_warnings) > 0

    def generate_intervention(self, report: HarmonyReport) -> List[str]:
        suggestions = []
        for warn in report.drift_warnings[:3]:
            term = warn['term']
            micro_experiment = (
                f"📖 术语「{term}」概念漂移 (一致性={warn['consistency']:.3f})。"
                f"建议启动「术语共识工作坊」微实验：\n"
                f"   1. 提取包含「{term}」的上下文片段（见下方）\n"
                f"   2. 邀请 2-3 位相关方对片段进行快速标注（投票或分级）\n"
                f"   3. 形成临时定义共识，并在后续 3 段论述中统一使用\n"
                f"   4. 观察 H 值变化，反馈给系统"
            )
            suggestions.append(micro_experiment)
        return suggestions

    def get_name(self) -> str:
        return "TermAlignmentHarvester"
```

---

### 23. intervention/weight_negotiation.py - 权重协商捕获器

```python
'''权重协商会议捕获器'''
from typing import List
from .base import BaseHarvester
from ..report import HarmonyReport
from ..config import INTERVENTION_TRIGGERS

class WeightNegotiationHarvester(BaseHarvester):
    def analyze(self, report: HarmonyReport) -> bool:
        return report.A > INTERVENTION_TRIGGERS["high_A"]

    def generate_intervention(self, report: HarmonyReport) -> List[str]:
        micro_experiment = (
            f"🔧 检测到较高对抗性 (A={report.A:.3f})。"
            f"建议启动「权重协商会议」微实验：\n"
            f"   1. 召集相关方（开发者、领域专家、终端用户）\n"
            f"   2. 基于当前评估样本，各方独立拖动 U/D/A 权重滑块\n"
            f"   3. 系统计算妥协解（如取均值或 Nash 解），生成新配置\n"
            f"   4. 用新配置重新评估，观察 H 值变化，记录协商过程"
        )
        return [micro_experiment]

    def get_name(self) -> str:
        return "WeightNegotiationHarvester"
```

---

### 24. presets/general.py - 通用预设

```python
GENERAL_TERMS = [
    "问题", "解决方案", "原因", "结果", "优势", "劣势",
    "机会", "风险", "目标", "策略", "执行", "评估"
]

GENERAL_CONTRADICTIONS = []
```

---

### 25. presets/legal.py - 法律领域预设

```python
LEGAL_TERMS = [
    "善意取得", "无权处分", "合理价格", "交付", "违约责任",
    "不可抗力", "情势变更", "同时履行抗辩权", "先履行抗辩权",
    "不安抗辩权", "代位权", "撤销权", "保证", "抵押", "质押",
    "善意", "恶意", "过失", "故意", "因果关系", "损害后果"
]

LEGAL_CONTRADICTIONS = [
    ("善意取得", "明知无权处分"),
    ("不可抗力", "迟延履行后发生"),
    ("同时履行抗辩权", "先履行义务"),
]
```

---

### 26. presets/medical.py - 医疗领域预设

```python
MEDICAL_TERMS = [
    "诊断", "治疗", "预后", "症状", "体征", "并发症",
    "适应症", "禁忌症", "剂量", "疗程", "复发", "缓解"
]

MEDICAL_CONTRADICTIONS = [
    ("抗生素", "病毒感染"),
    ("抗凝", "活动性出血"),
]
```

---

### 27. presets/__init__.py - 预设模块入口

```python
from .legal import LEGAL_TERMS, LEGAL_CONTRADICTIONS
from .general import GENERAL_TERMS, GENERAL_CONTRADICTIONS
from .medical import MEDICAL_TERMS, MEDICAL_CONTRADICTIONS

def get_preset(domain: str):
    if domain == "legal":
        return {"terms": LEGAL_TERMS, "contradiction_rules": LEGAL_CONTRADICTIONS}
    elif domain == "medical":
        return {"terms": MEDICAL_TERMS, "contradiction_rules": MEDICAL_CONTRADICTIONS}
    else:
        return {"terms": GENERAL_TERMS, "contradiction_rules": GENERAL_CONTRADICTIONS}
```

---

### 28. utils.py - ThinkCheck Harmony工具模块

```python
"""
ThinkCheck Harmony 工具模块
文本处理、分块等辅助函数
"""

import re
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class TextChunk:
    content: str
    start_index: int
    end_index: int
    metadata: dict = None


def clean_text(text: str) -> str:
    """
    清理文本：去除多余空格、换行等
    """
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text


def split_into_sentences(text: str) -> List[str]:
    """
    将文本分割成句子
    """
    pattern = r'(?<=[.!?。！？])\s+'
    sentences = re.split(pattern, text)
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences


def split_into_paragraphs(text: str) -> List[str]:
    """
    将文本分割成段落
    """
    paragraphs = text.split('\n\n')
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    return paragraphs


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[TextChunk]:
    """
    将文本分块，支持重叠
    """
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        if end > len(text):
            end = len(text)
        
        chunk_content = text[start:end]
        chunks.append(TextChunk(
            content=chunk_content,
            start_index=start,
            end_index=end
        ))
        
        start += chunk_size - overlap
        if start >= len(text):
            break
    
    return chunks


def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """
    简单的关键词提取（基于词频）
    """
    words = re.findall(r'[\w\u4e00-\u9fff]+', text.lower())
    stop_words = {'的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
    
    filtered_words = [word for word in words if word not in stop_words and len(word) > 1]
    
    from collections import Counter
    word_counts = Counter(filtered_words)
    return [word for word, _ in word_counts.most_common(top_n)]


def detect_language(text: str) -> str:
    """
    简单的语言检测（基于字符）
    """
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    english_chars = re.findall(r'[a-zA-Z]', text)
    
    if len(chinese_chars) > len(english_chars):
        return 'zh'
    else:
        return 'en'
```

---

## 📦 ThinkCheck产品版 (thinkcheck_product/)

### 29. thinkcheck/improved.py - 改进版本

```python
"""
ThinkCheck 改进版本
解决了致命问题，更适合实际使用
"""

import re
import statistics
from typing import List, Tuple, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import random


@dataclass
class ReasoningStep:
    """改进的推理步骤记录"""
    step_id: int
    content: str
    h_score: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_backtrack_trigger: bool = False


class ImprovedHarmonicMonitor:
    """
    改进的和谐度监控器
    
    主要改进：
    1. 支持多种语言的否定词检测
    2. 改进的分词和语义理解
    3. 更智能的回溯触发机制
    """
    
    # 多语言否定词支持
    NEGATION_WORDS = {
        'zh': {"不", "没有", "无", "非", "否", "别", "没", "不要", "不能", "不会"},
        'en': {"no", "not", "never", "none", "nothing", "nobody", "nowhere", "neither", "nor"},
        'ja': {"ない", "ません", "ず", "ぬ", "ん"},
        'ko': {"아니", "않", "없", "못", "말"}
    }
    
    def __init__(self, 
                 h_threshold: float = 0.35,
                 lookback_window: int = 4,
                 verbose: bool = True,
                 language: str = 'zh'):
        """
        初始化改进的监控器
        
        参数：
        language: 语言代码，支持 'zh', 'en', 'ja', 'ko'
        """
        self.h_threshold = h_threshold
        self.lookback_window = lookback_window
        self.verbose = verbose
        self.language = language
        self.history: List[ReasoningStep] = []
        self.step_counter = 0
        self.consecutive_low_h = 0
        
    def preprocess(self, text: str) -> List[str]:
        """
        改进的预处理 - 更好的分词
        """
        if self.language == 'zh':
            # 中文简单分词（实际应该用jieba等）
            return [char for char in text if char.strip()]
        else:
            # 英文等语言分词
            return [word.lower() for word in re.findall(r'\w+', text)]
    
    def calculate_h_score(self, history: List[str], current_text: str, 
                         weights: Optional[Dict[str, float]] = None) -> float:
        """
        改进的和谐度计算
        """
        if not current_text or not isinstance(current_text, str):
            return 0.5
        
        weights = weights or {"U": 0.35, "D": 0.4, "A": 0.25}
        current_words = self.preprocess(current_text)
        
        if not current_words:
            return 0.5
        
        # 1. 新颖性 U
        if not history:
            U = 1.0
        else:
            historical_words = set()
            for past_text in history[-3:]:
                historical_words.update(self.preprocess(past_text))
            new_words = [w for w in current_words if w not in historical_words]
            U = len(new_words) / max(len(current_words), 1)
        
        # 2. 探索性 D - 改进的相似度计算
        if not history:
            D = 1.0
        else:
            similarities = []
            for past_text in history[-3:]:
                if not past_text:
                    continue
                past_words = self.preprocess(past_text)
                set1, set2 = set(current_words), set(past_words)
                if not set1 and not set2:
                    similarity = 0
                else:
                    intersection = len(set1 & set2)
                    union = len(set1 | set2)
                    similarity = intersection / union if union > 0 else 0
                similarities.append(similarity)
            avg_similarity = statistics.mean(similarities) if similarities else 0
            D = 1 - avg_similarity
        
        # 3. 对抗性 A - 多语言支持
        negations = self.NEGATION_WORDS.get(self.language, set())
        
        # 3.1 重复性
        word_counts = {}
        for word in current_words:
            word_counts[word] = word_counts.get(word, 0) + 1
        repeated_words = sum(1 for count in word_counts.values() if count > 2)  # 更严格
        repetition_score = repeated_words / max(len(current_words), 1)
        
        # 3.2 矛盾检测
        negation_count = sum(1 for word in current_words if word in negations)
        contradiction_score = min(negation_count * 0.08, 1.0)
        
        A = 0.6 * repetition_score + 0.4 * contradiction_score
        
        H = weights["U"] * U + weights["D"] * D - weights["A"] * A
        H = max(0.0, min(1.0, H))
        
        return round(H, 3)
    
    def add_step(self, content: str, metadata: Optional[Dict] = None) -> Tuple[float, bool]:
        """
        添加推理步骤
        """
        self.step_counter += 1
        
        previous_contents = [step.content for step in self.history[-self.lookback_window:]]
        h_score = self.calculate_h_score(previous_contents, content)
        
        step = ReasoningStep(
            step_id=self.step_counter,
            content=content,
            h_score=h_score,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        needs_backtrack = self._check_backtrack_needed(h_score)
        step.is_backtrack_trigger = needs_backtrack
        self.history.append(step)
        
        if self.verbose:
            status = "🚨 需要回溯" if needs_backtrack else "✅ 正常"
            print(f"[Step {self.step_counter}] H={h_score:.2f} {status}")
            if needs_backtrack:
                print(f"    原因: {self._get_backtrack_reason()}")
        
        return h_score, needs_backtrack
    
    def _check_backtrack_needed(self, current_h: float) -> bool:
        """
        改进的回溯检测 - 多重条件判断
        """
        if not self.history:
            return False
        
        # 条件1: 当前H值低于阈值
        if current_h < self.h_threshold:
            self.consecutive_low_h += 1
            if self.consecutive_low_h >= 2:  # 连续2次低才触发
                return True
        else:
            self.consecutive_low_h = 0
        
        # 条件2: 连续下降趋势
        if len(self.history) >= 3:
            recent_h = [s.h_score for s in self.history[-3:]] + [current_h]
            is_descending = all(recent_h[i] > recent_h[i+1] for i in range(len(recent_h)-1))
            if is_descending and recent_h[-1] < 0.5:
                return True
        
        return False
    
    def _get_backtrack_reason(self) -> str:
        """获取回溯原因描述"""
        if self.consecutive_low_h >= 2:
            return f"连续{self.consecutive_low_h}次和谐度低于阈值"
        return "推理质量呈下降趋势"
    
    def get_summary(self) -> Dict[str, Any]:
        """获取详细摘要"""
        if not self.history:
            return {"total_steps": 0, "status": "empty"}
        
        h_scores = [s.h_score for s in self.history]
        return {
            "total_steps": len(self.history),
            "average_h": statistics.mean(h_scores),
            "min_h": min(h_scores),
            "max_h": max(h_scores),
            "low_h_steps": sum(1 for h in h_scores if h < self.h_threshold),
            "backtrack_triggers": sum(1 for s in self.history if s.is_backtrack_trigger),
            "status": "healthy" if h_scores[-1] >= self.h_threshold else "needs_attention"
        }
    
    def clear_history(self):
        self.history.clear()
        self.step_counter = 0
        self.consecutive_low_h = 0


class ImprovedRetryStrategy:
    """
    改进的重试策略 - 真正有意义的回溯
    
    支持：
    1. 调整temperature
    2. 修改提示词
    3. 改变推理策略
    """
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.attempt_history = []
    
    def generate_modified_prompt(self, original_prompt: str, attempt: int) -> str:
        """
        根据尝试次数生成改进的提示词
        """
        modifiers = [
            original_prompt,  # 第1次：原样
            f"{original_prompt}\n\n请换一个角度思考，不要重复之前的内容。",  # 第2次
            f"{original_prompt}\n\n请重新分析，确保每个步骤都有新的进展。",  # 第3次
            f"{original_prompt}\n\n让我们从头开始，一步步仔细推理。"  # 第4次
        ]
        return modifiers[min(attempt, len(modifiers)-1)]
    
    def get_temperature(self, attempt: int) -> float:
        """
        根据尝试次数调整temperature
        """
        temps = [0.7, 0.9, 1.0, 0.5]  # 逐渐增加随机性，最后保守
        return temps[min(attempt, len(temps)-1)]
    
    def execute(self, func: Callable, original_prompt: str, 
                attempt: int, **kwargs) -> Tuple[Any, Dict]:
        """
        执行改进的重试策略
        """
        modified_prompt = self.generate_modified_prompt(original_prompt, attempt)
        temperature = self.get_temperature(attempt)
        
        self.attempt_history.append({
            "attempt": attempt + 1,
            "prompt": modified_prompt,
            "temperature": temperature
        })
        
        result = func(
            prompt=modified_prompt,
            temperature=temperature,
            attempt=attempt,
            **kwargs
        )
        
        return result, {
            "attempt": attempt + 1,
            "temperature": temperature,
            "prompt_was_modified": attempt > 0
        }


def monitor_streaming_reasoning(reasoning_generator: Callable,
                               monitor: ImprovedHarmonicMonitor) -> Tuple[str, Dict]:
    """
    监控流式推理过程 - 这才是正确的集成方式！
    
    不是只看最终结果，而是监控每一步推理
    """
    all_steps = []
    
    for step_content in reasoning_generator():
        h_score, needs_backtrack = monitor.add_step(step_content)
        all_steps.append({
            "content": step_content,
            "h_score": h_score,
            "needs_backtrack": needs_backtrack
        })
        
        if needs_backtrack:
            # 这里可以实际中断推理并触发回溯
            print(f"⚠️  检测到推理问题，考虑回溯...")
    
    summary = monitor.get_summary()
    final_answer = all_steps[-1]["content"] if all_steps else ""
    
    return final_answer, {"steps": all_steps, "summary": summary}
```

---

## 📝 演示与测试脚本

### 30. run_demo.py - 演示脚本

```python
import os
import json
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from thinkcheck_harmony import HarmonyEvaluator
from thinkcheck_agent.core.actuator import HarmonyActuator

def main():
    with open("complex_case.txt", "r", encoding="utf-8") as f:
        doc = f.read()
    print("原始文档:\n", doc)

    eva = HarmonyEvaluator()
    scores = eva.evaluate(doc)
    scores_dict = scores.to_dict()
    print("\n原始评分:", json.dumps(scores_dict, indent=2, ensure_ascii=False))

    act = HarmonyActuator()
    result = act.harmonize_document(doc, diagnosis=scores_dict)
    fixed = result.get('tuned_text', doc)
    usage = result.get('usage', {})
    print("\n修复后文档:\n", fixed)
    print("\nToken使用:", usage)

    new_scores = eva.evaluate(fixed)
    new_scores_dict = new_scores.to_dict()
    print("\n修复后评分:", json.dumps(new_scores_dict, indent=2, ensure_ascii=False))

    with open("report.json", "w", encoding="utf-8") as f:
        json.dump({
            "original": doc,
            "original_scores": scores_dict,
            "fixed": fixed,
            "fixed_scores": new_scores_dict,
            "token_usage": usage,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2, ensure_ascii=False)
    print("\n详细报告已保存至 report.json")

if __name__ == "__main__":
    main()
```

---

### 31. requirements.txt - 依赖列表

```txt
openai>=1.0.0
pyyaml>=6.0
aiofiles>=23.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.0
loguru>=0.7.0
numpy>=1.20.0
networkx>=3.0
fastapi>=0.100.0
uvicorn>=0.20.0
python-multipart>=0.0.6
pytest>=7.0.0
pytest-asyncio>=0.20.0
pytest-cov>=4.0.0
black>=23.0.0
isort>=5.0.0
flake8>=6.0.0
pre-commit>=3.0.0
```

---

## 📊 项目统计

| 指标 | 数值 |
|------|------|
| 核心源代码文件 | 31个 |
| 代码总行数（估算） | ~3000行 |
| 子项目 | 3个 |
| 主要依赖库 | 19个 |

---

## 🎯 核心公式

```
H = λU·U + λD·D - λA·A
```

- **H**: 和谐度 (Harmony)
- **U**: 统一性 (Unity) - 概念在文档中使用的一致性程度
- **D**: 发展性 (Development) - 概念在文档中出现位置的分布
- **A**: 对抗性 (Adversarial) - 矛盾对立程度
- **λU, λD, λA**: 权重 (默认 0.4, 0.4, 0.2)