"""
审计日志系统
公理三：实践介入论 — 所有自动操作必须可追溯、可撤回、可被审查
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
from uuid import uuid4


class OperationType(Enum):
    """操作类型"""
    FLAG_CONTRADICTION = "flag_contradiction"
    FLAG_DRIFT = "flag_drift"
    CREATE_NODE = "create_node"
    CREATE_EDGE = "create_edge"
    FLIP_POINT_WARNING = "flip_point_warning"
    STAGE_TRANSITION = "stage_transition"
    PRESENT_DATA = "present_data"
    BOUNDARY_CHECK = "boundary_check"
    GOVERNANCE_REVIEW = "governance_review"


@dataclass
class AuditEntry:
    """审计条目 — 完整版"""
    entry_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    operation_type: OperationType = OperationType.CREATE_NODE
    motivation: str = ""                      # 操作动机（为什么触发）
    content: Dict[str, Any] = field(default_factory=dict)  # 操作内容快照
    alternatives: List[str] = field(default_factory=list)  # 替代方案列表
    rollback_path: str = ""                   # 撤回路径
    operator: str = "system"
    status: str = "active"                    # active | rolled_back
    rolled_back_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp.isoformat(),
            "operation_type": self.operation_type.value,
            "motivation": self.motivation,
            "content": self.content,
            "alternatives": self.alternatives,
            "rollback_path": self.rollback_path,
            "operator": self.operator,
            "status": self.status,
            "rolled_back_at": self.rolled_back_at,
        }


class AuditLog:
    """
    审计日志系统
    所有自动操作必须可追溯、可撤回、可被审查
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.entries: List[AuditEntry] = []
        self.created_at = datetime.now()

    def log(self, entry: AuditEntry) -> str:
        """记录一条审计条目（仅追加）"""
        self.entries.append(entry)
        return entry.entry_id

    def log_contradiction_flag(
        self,
        contradiction_id: str,
        a_value: float,
        motivation: str,
        rollback_path: str = "在价值档案面板中删除此矛盾标记"
    ) -> str:
        """记录矛盾标记操作"""
        entry = AuditEntry(
            operation_type=OperationType.FLAG_CONTRADICTION,
            motivation=motivation,
            content={
                "contradiction_id": contradiction_id,
                "a_value": a_value,
                "detected_at": datetime.now().isoformat(),
            },
            alternatives=[
                "也可以选择不标记，等待人工确认",
                "也可以提高A值阈值以减少敏感度",
            ],
            rollback_path=rollback_path,
            operator="system",
        )
        return self.log(entry)

    def log_flip_point_warning(
        self,
        position: int,
        u_value: float,
        d_value: float,
        h_value: float,
        motivation: str
    ) -> str:
        """记录翻转点预警"""
        entry = AuditEntry(
            operation_type=OperationType.FLIP_POINT_WARNING,
            motivation=motivation,
            content={
                "position": position,
                "u_value": u_value,
                "d_value": d_value,
                "h_value": h_value,
                "detected_at": datetime.now().isoformat(),
            },
            alternatives=[
                "也可以提高翻转点检测阈值以减少预警",
                "也可以禁用翻转点检测",
            ],
            rollback_path="通过 /audit/{id}/reject 端点驳回此预警",
            operator="system",
        )
        return self.log(entry)

    def log_stage_transition(
        self,
        contradiction_id: str,
        from_stage: str,
        to_stage: str,
        motivation: str
    ) -> str:
        """记录矛盾阶段转换"""
        entry = AuditEntry(
            operation_type=OperationType.STAGE_TRANSITION,
            motivation=motivation,
            content={
                "contradiction_id": contradiction_id,
                "from_stage": from_stage,
                "to_stage": to_stage,
                "transitioned_at": datetime.now().isoformat(),
            },
            alternatives=[
                "也可以保持当前阶段不转换",
                "也可以回退到前一阶段",
            ],
            rollback_path="通过 /audit/{id}/reject 端点驳回此转换",
            operator="system",
        )
        return self.log(entry)

    def log_governance_review(self, report_id: str, motivation: str) -> str:
        """记录元反思审视"""
        entry = AuditEntry(
            operation_type=OperationType.GOVERNANCE_REVIEW,
            motivation=motivation,
            content={
                "report_id": report_id,
                "reviewed_at": datetime.now().isoformat(),
            },
            alternatives=[
                "也可以延后审视",
                "也可以调整审视周期",
            ],
            rollback_path="通过 /audit/{id}/reject 端点驳回此次审视",
            operator="system",
        )
        return self.log(entry)

    def get_entries_by_type(self, op_type: OperationType) -> List[AuditEntry]:
        return [e for e in self.entries if e.operation_type == op_type]

    def get_entries_by_operator(self, operator: str) -> List[AuditEntry]:
        return [e for e in self.entries if e.operator == operator]

    def get_recent(self, limit: int = 50) -> List[AuditEntry]:
        return sorted(self.entries, key=lambda e: e.timestamp, reverse=True)[:limit]

    def rollback(self, entry_id: str) -> bool:
        """撤回一个操作（标记为已撤回，不删除历史）"""
        for entry in self.entries:
            if entry.entry_id == entry_id:
                entry.status = "rolled_back"
                entry.rolled_back_at = datetime.now().isoformat()
                return True
        return False

    def export_to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "total_entries": len(self.entries),
            "active_entries": len([e for e in self.entries if e.status == "active"]),
            "rolled_back_entries": len([e for e in self.entries if e.status == "rolled_back"]),
            "entries": [e.to_dict() for e in self.entries],
        }

    def export_to_json(self, filepath: str) -> None:
        import json
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.export_to_dict(), f, ensure_ascii=False, indent=2)
