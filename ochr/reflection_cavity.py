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
