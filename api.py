"""
ThinkCheck Agent - REST API 服务
"""

import asyncio
import uuid
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent / 'thinkcheck-harmony'))

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
    auto_fix: bool = Field(False, description="是否自动修复（默认关闭，需用户显式启用）")


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
        
        # 处理返回类型（可能是dict或有to_dict方法的对象）
        if hasattr(report, 'to_dict'):
            report_dict = report.to_dict()
        elif isinstance(report, dict):
            report_dict = report
        else:
            report_dict = {"U": 0.0, "D": 0.0, "A": 0.0, "H": 0.0}
        
        # 提取分数
        scores = report_dict.get("scores", report_dict.get("harmony_report", report_dict))
        u = scores.get("U", scores.get("u", 0.0))
        d = scores.get("D", scores.get("d", 0.0))
        a = scores.get("A", scores.get("a", 0.0))
        h = scores.get("H", scores.get("h", 0.0))
        
        # 提取动态参数（诊断参数透明化）
        diagnostic_params = {
            "lambda_u": scores.get("lambda_u", 0.4),
            "lambda_d": scores.get("lambda_d", 0.4),
            "lambda_a": scores.get("lambda_a", 0.2),
            "method": scores.get("method", "rule_based"),
            "u_source": scores.get("u_source", "lexical_repetition"),
            "d_source": scores.get("d_source", "position_distribution"),
            "a_source": scores.get("a_source", "sentence_structure_change")
        }
        
        result = {
            "request_id": request_id,
            "scores": {
                "U": u,
                "D": d,
                "A": a,
                "H": h
            },
            "diagnostic_parameters": diagnostic_params,
            "suggestions": report_dict.get("suggestions", []),
            "warnings": report_dict.get("warnings", [])
        }
        
        logger.info(f"评估完成: H={h:.3f}")
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


# ============================================
# 审计日志端点（公理三：实践介入论）
# ============================================

@app.get("/audit/{session_id}")
async def get_audit_log(session_id: str):
    """获取完整审计日志"""
    from thinkcheck_agent.core.orchestration import get_orchestrator
    try:
        orchestrator = get_orchestrator(session_id)
        cavity = orchestrator.reflection_cavity
        if not cavity:
            raise HTTPException(404, "Reflection cavity not found")
        return {
            "session_id": session_id,
            "entries": [e.__dict__ for e in cavity.history] if hasattr(cavity, 'history') else []
        }
    except Exception as e:
        return {"session_id": session_id, "entries": [], "error": str(e)}


@app.get("/audit/{session_id}/{entry_id}")
async def get_audit_entry(session_id: str, entry_id: str):
    """获取单条审计条目"""
    from thinkcheck_agent.core.orchestration import get_orchestrator
    orchestrator = get_orchestrator(session_id)
    cavity = orchestrator.reflection_cavity
    if not cavity:
        raise HTTPException(404, "Reflection cavity not found")
    for entry in cavity.history:
        if entry.entry_id == entry_id:
            return entry.__dict__
    raise HTTPException(404, "Entry not found")


@app.post("/audit/{session_id}/{entry_id}/reject")
async def reject_audit_entry(session_id: str, entry_id: str):
    """撤回/驳回审计条目"""
    from thinkcheck_agent.core.orchestration import get_orchestrator
    orchestrator = get_orchestrator(session_id)
    cavity = orchestrator.reflection_cavity
    if not cavity:
        raise HTTPException(404, "Reflection cavity not found")
    if hasattr(cavity, 'rollback_entry'):
        success = cavity.rollback_entry(entry_id)
        if not success:
            raise HTTPException(404, "Entry not found")
        return {"status": "rolled_back", "entry_id": entry_id}
    # 兼容模式：手动标记
    for entry in cavity.history:
        if entry.entry_id == entry_id:
            entry.status = "rolled_back"
            entry.rolled_back_at = datetime.now().isoformat()
            return {"status": "rolled_back", "entry_id": entry_id}
    raise HTTPException(404, "Entry not found")


@app.get("/audit/{session_id}/export")
async def export_audit_log(session_id: str):
    """导出审计日志为JSON"""
    from thinkcheck_agent.core.orchestration import get_orchestrator
    import json
    orchestrator = get_orchestrator(session_id)
    cavity = orchestrator.reflection_cavity
    if not cavity:
        raise HTTPException(404, "Reflection cavity not found")
    export_data = {
        "session_id": session_id,
        "exported_at": datetime.now().isoformat(),
        "entries": [e.__dict__ for e in cavity.history]
    }
    return Response(
        content=json.dumps(export_data, ensure_ascii=False, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=audit_{session_id}.json"}
    )


# ============================================
# L3 元反思治理端点（公理五：元反思律）
# ============================================

@app.get("/governance/report/{session_id}")
async def get_governance_report(session_id: str):
    """获取L3治理健康度报告"""
    from thinkcheck_agent.core.orchestration import get_orchestrator
    orchestrator = get_orchestrator(session_id)
    if not hasattr(orchestrator, 'l3_engine'):
        return {"status": "not_available", "message": "L3 engine not initialized"}
    report = orchestrator.l3_engine.get_latest_report()
    if not report:
        return {"status": "not_available", "message": "No report available"}
    return report.to_dict()


@app.post("/governance/review/{session_id}")
async def trigger_governance_review(session_id: str):
    """触发元反思审视"""
    from thinkcheck_agent.core.orchestration import get_orchestrator
    from l3_reflection import L3ReflectionEngine
    orchestrator = get_orchestrator(session_id)
    if not hasattr(orchestrator, 'l3_engine'):
        orchestrator.l3_engine = L3ReflectionEngine()
    cavity = orchestrator.reflection_cavity
    rule_stats = {}
    if cavity and hasattr(cavity, 'history'):
        for entry in cavity.history:
            op_type = getattr(entry, 'operation', 'unknown')
            if op_type not in rule_stats:
                rule_stats[op_type] = {"name": op_type, "total_triggers": 0, "confirmed": 0, "dismissed": 0, "pending": 0, "trend": []}
            rule_stats[op_type]["total_triggers"] += 1
            status = getattr(entry, 'status', 'active')
            if status == "rolled_back":
                rule_stats[op_type]["dismissed"] += 1
            elif status == "confirmed":
                rule_stats[op_type]["confirmed"] += 1
            else:
                rule_stats[op_type]["pending"] += 1
    report = orchestrator.l3_engine.generate_report(rule_stats)
    return report.to_dict()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
