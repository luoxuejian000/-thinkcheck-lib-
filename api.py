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
