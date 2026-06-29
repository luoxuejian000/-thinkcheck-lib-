"""
诊断报告生成器
公理三：只看病，不开方
输出纯诊断数据，不包含任何行动建议
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional


@dataclass
class DiagnosticReport:
    """纯诊断报告 — 不包含任何建议或行动方案"""
    session_id: str
    generated_at: datetime = field(default_factory=datetime.now)
    u_trajectory: List[float] = field(default_factory=list)
    d_trajectory: List[float] = field(default_factory=list)
    a_trajectory: List[float] = field(default_factory=list)
    h_trajectory: List[float] = field(default_factory=list)
    resonant_window_status: Dict[str, Any] = field(default_factory=dict)
    contradiction_points: List[Dict[str, Any]] = field(default_factory=list)
    flip_points: List[Dict[str, Any]] = field(default_factory=list)
    silent_dissonance_note: Optional[str] = None
    unresolved_contradictions: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "generated_at": self.generated_at.isoformat(),
            "u_trajectory": self.u_trajectory,
            "d_trajectory": self.d_trajectory,
            "a_trajectory": self.a_trajectory,
            "h_trajectory": self.h_trajectory,
            "resonant_window_status": self.resonant_window_status,
            "contradiction_points": self.contradiction_points,
            "flip_points": self.flip_points,
            "silent_dissonance_note": self.silent_dissonance_note,
            "unresolved_contradictions": self.unresolved_contradictions,
        }

    def to_markdown(self) -> str:
        """生成Markdown格式报告（不含建议）"""
        lines = [
            "# 场域诊断报告",
            f"会话ID: {self.session_id}",
            f"生成时间: {self.generated_at.isoformat()}",
            "",
            "## 四维轨迹",
            f"- U值（统一性）: {self._format_trajectory(self.u_trajectory)}",
            f"- D值（发展性）: {self._format_trajectory(self.d_trajectory)}",
            f"- A值（对抗性）: {self._format_trajectory(self.a_trajectory)}",
            f"- H值（和谐度）: {self._format_trajectory(self.h_trajectory)}",
            "",
            "## 谐振窗口状态",
            f"- 当前H值: {self.resonant_window_status.get('h_value', 'N/A')}",
            f"- 当前A值: {self.resonant_window_status.get('a_value', 'N/A')}",
            f"- 是否在谐振窗口内: {self.resonant_window_status.get('in_window', 'N/A')}",
            "",
            "## 矛盾点定位",
        ]
        if not self.contradiction_points:
            lines.append("（未检测到矛盾点）")
        else:
            for i, cp in enumerate(self.contradiction_points, 1):
                lines.extend([
                    f"### 矛盾点 {i}",
                    f"- 位置: {cp.get('position', 'N/A')}",
                    f"- A值: {cp.get('a_value', 'N/A')}",
                    f"- 陈述A: {cp.get('text_a', '')[:200]}...",
                    f"- 陈述B: {cp.get('text_b', '')[:200]}...",
                ])
        lines.append("")
        lines.append("## 翻转点检测")
        if not self.flip_points:
            lines.append("（未检测到翻转点）")
        else:
            for fp in self.flip_points:
                lines.append(
                    f"- 位置 {fp.get('position', 'N/A')}: "
                    f"ΔU={fp.get('u_delta', 'N/A')}, "
                    f"ΔD={fp.get('d_delta', 'N/A')}, "
                    f"ΔH={fp.get('h_delta', 'N/A')}"
                )
        lines.append("")
        if self.silent_dissonance_note:
            lines.extend(["## 沉默失谐注意", self.silent_dissonance_note, ""])
        lines.extend([
            "## 未解矛盾",
        ])
        if self.unresolved_contradictions:
            for uc in self.unresolved_contradictions:
                lines.append(f"- {uc.get('description', '')}")
        else:
            lines.append("（当前未检测到未解矛盾）")
        lines.extend([
            "",
            "---",
            "*本报告仅呈现诊断数据，不构成任何行动建议。判断权在您手中。*",
        ])
        return "\n".join(lines)

    def _format_trajectory(self, values: List[float]) -> str:
        if not values:
            return "[]"
        if len(values) <= 10:
            return "[" + ", ".join(f"{v:.3f}" for v in values) + "]"
        head = ", ".join(f"{v:.3f}" for v in values[:5])
        tail = ", ".join(f"{v:.3f}" for v in values[-5:])
        return f"[{head} ... {tail}] (共{len(values)}个采样点)"
