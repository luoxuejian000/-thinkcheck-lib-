"""
矛盾生命周期管理
公理二：矛盾是演化燃料
DORMANT → EMERGENT → NOTICED → PROCESSING → RESOLVED / TRANSFORMED
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
from uuid import uuid4


class ContradictionStage(Enum):
    """矛盾六阶段"""
    DORMANT = "dormant"          # 潜伏：矛盾存在但未被检测
    EMERGENT = "emergent"        # 涌现：系统检测到矛盾信号
    NOTICED = "noticed"          # 被注意：矛盾已呈现给用户
    PROCESSING = "processing"    # 处理中：用户正在审视矛盾
    RESOLVED = "resolved"        # 已解决：用户做出决定
    TRANSFORMED = "transformed"  # 已转化：矛盾导致新的理解


@dataclass
class Contradiction:
    """矛盾实体"""
    id: str = field(default_factory=lambda: str(uuid4()))
    statement_a: str = ""
    statement_b: str = ""
    a_value: float = 0.0
    stage: ContradictionStage = ContradictionStage.DORMANT
    detected_at: datetime = field(default_factory=datetime.now)
    presented_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    user_decision: Optional[str] = None
    notes: List[str] = field(default_factory=list)
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)

    def transition_to(self, new_stage: ContradictionStage, note: str = "") -> None:
        """阶段转换，记录审计轨迹"""
        old_stage = self.stage
        self.stage = new_stage
        self.audit_trail.append({
            "timestamp": datetime.now().isoformat(),
            "from_stage": old_stage.value,
            "to_stage": new_stage.value,
            "note": note,
        })
        if new_stage == ContradictionStage.NOTICED and self.presented_at is None:
            self.presented_at = datetime.now()
        if new_stage in (ContradictionStage.RESOLVED, ContradictionStage.TRANSFORMED):
            self.resolved_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "statement_a": self.statement_a,
            "statement_b": self.statement_b,
            "a_value": self.a_value,
            "stage": self.stage.value,
            "detected_at": self.detected_at.isoformat(),
            "presented_at": self.presented_at.isoformat() if self.presented_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "user_decision": self.user_decision,
            "notes": self.notes,
            "audit_trail": self.audit_trail,
        }


class ContradictionLifecycleManager:
    """
    矛盾生命周期管理器
    核心原则：系统仅自主处理 DORMANT → EMERGENT 的转换
    所有后续阶段都需要用户参与
    系统绝不将矛盾转换至 RESOLVED 状态而无用户显式操作
    """

    def __init__(self):
        self.contradictions: Dict[str, Contradiction] = {}

    def create(self, stmt_a: str, stmt_b: str, a_value: float) -> str:
        """创建矛盾（DORMANT状态）"""
        c = Contradiction(
            statement_a=stmt_a,
            statement_b=stmt_b,
            a_value=a_value,
            stage=ContradictionStage.DORMANT,
        )
        self.contradictions[c.id] = c
        return c.id

    def detect(self, contradiction_id: str) -> None:
        """
        系统检测到矛盾 → EMERGENT
        这是系统唯一可以自主执行的阶段转换
        """
        c = self.contradictions.get(contradiction_id)
        if c and c.stage == ContradictionStage.DORMANT:
            c.transition_to(ContradictionStage.EMERGENT, "系统检测到矛盾信号")

    def present_to_user(self, contradiction_id: str) -> None:
        """呈现给用户 → NOTICED"""
        c = self.contradictions.get(contradiction_id)
        if c and c.stage == ContradictionStage.EMERGENT:
            c.transition_to(ContradictionStage.NOTICED, "矛盾已呈现在价值档案中")

    def user_views(self, contradiction_id: str) -> None:
        """用户查看矛盾 → PROCESSING"""
        c = self.contradictions.get(contradiction_id)
        if c and c.stage == ContradictionStage.NOTICED:
            c.transition_to(ContradictionStage.PROCESSING, "用户正在审视矛盾")

    def user_resolves(self, contradiction_id: str, decision: str) -> None:
        """
        用户解决矛盾 → RESOLVED 或 TRANSFORMED
        只有用户显式操作才能进入解决状态
        """
        c = self.contradictions.get(contradiction_id)
        if c and c.stage in (ContradictionStage.NOTICED, ContradictionStage.PROCESSING):
            c.user_decision = decision
            if "转化" in decision or "新理解" in decision:
                c.transition_to(ContradictionStage.TRANSFORMED, f"用户决策: {decision}")
            else:
                c.transition_to(ContradictionStage.RESOLVED, f"用户决策: {decision}")

    def get_active(self) -> List[Contradiction]:
        """获取未解决的矛盾"""
        active = {
            ContradictionStage.DORMANT,
            ContradictionStage.EMERGENT,
            ContradictionStage.NOTICED,
            ContradictionStage.PROCESSING,
        }
        return [c for c in self.contradictions.values() if c.stage in active]

    def get_by_stage(self, stage: ContradictionStage) -> List[Contradiction]:
        """按阶段获取矛盾"""
        return [c for c in self.contradictions.values() if c.stage == stage]

    def get_summary(self) -> Dict[str, int]:
        """获取矛盾状态分布摘要"""
        summary = {s.value: 0 for s in ContradictionStage}
        for c in self.contradictions.values():
            summary[c.stage.value] += 1
        return summary

    def get_audit_trail(self, contradiction_id: str) -> List[Dict[str, Any]]:
        """获取矛盾的完整审计轨迹"""
        c = self.contradictions.get(contradiction_id)
        return c.audit_trail if c else []
