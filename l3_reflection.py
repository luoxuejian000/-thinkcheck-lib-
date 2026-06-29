"""
L3 元反思引擎
公理五：元反思律 — 任何理论原则都必须对实践检验保持开放
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional


@dataclass
class RulePerformance:
    """单条规则的性能数据"""
    rule_id: str
    rule_name: str
    total_triggers: int = 0
    confirmed_count: int = 0
    dismissed_count: int = 0
    pending_count: int = 0
    trigger_trend: List[int] = field(default_factory=list)

    @property
    def confirmation_rate(self) -> float:
        return self.confirmed_count / self.total_triggers if self.total_triggers > 0 else 0.0

    @property
    def false_positive_rate(self) -> float:
        return self.dismissed_count / self.total_triggers if self.total_triggers > 0 else 0.0

    def is_high_false_positive(self, threshold: float = 0.3) -> bool:
        return self.false_positive_rate > threshold

    def is_low_frequency(self, min_triggers: int = 5) -> bool:
        return self.total_triggers < min_triggers

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "total_triggers": self.total_triggers,
            "confirmed_count": self.confirmed_count,
            "dismissed_count": self.dismissed_count,
            "pending_count": self.pending_count,
            "confirmation_rate": self.confirmation_rate,
            "false_positive_rate": self.false_positive_rate,
            "trigger_trend": self.trigger_trend,
            "status": "误报率过高" if self.is_high_false_positive() else (
                "触发频率过低" if self.is_low_frequency() else "正常"
            ),
        }


@dataclass
class GovernanceHealthReport:
    """治理健康度报告"""
    generated_at: datetime = field(default_factory=datetime.now)
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    rule_performances: List[RulePerformance] = field(default_factory=list)
    recommendations: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": self.generated_at.isoformat(),
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "rule_performances": [rp.to_dict() for rp in self.rule_performances],
            "recommendations": self.recommendations,
        }

    def to_markdown(self) -> str:
        lines = [
            "# 治理健康度报告",
            f"生成时间: {self.generated_at.isoformat()}",
        ]
        if self.period_start and self.period_end:
            lines.append(f"统计周期: {self.period_start.isoformat()} ~ {self.period_end.isoformat()}")
        lines.extend([
            "",
            "## 规则性能摘要",
            "| 规则ID | 名称 | 触发次数 | 确认率 | 误报率 | 状态 |",
            "|--------|------|----------|--------|--------|------|",
        ])
        for rp in self.rule_performances:
            status = "正常"
            if rp.is_high_false_positive():
                status = "⚠️ 误报率过高"
            elif rp.is_low_frequency():
                status = "⚠️ 触发频率过低"
            lines.append(
                f"| {rp.rule_id} | {rp.rule_name} | {rp.total_triggers} | "
                f"{rp.confirmation_rate:.1%} | {rp.false_positive_rate:.1%} | {status} |"
            )
        lines.append("")
        if self.recommendations:
            lines.extend([
                "## 调整建议",
                "",
                "> 以下建议基于数据分析生成，是否采纳由您决定。",
                "",
            ])
            for rec in self.recommendations:
                lines.append(f"### {rec.get('rule_id', '')}: {rec.get('issue', '')}")
                lines.append(f"- {rec.get('suggestion', '')}")
                lines.append("")
        else:
            lines.extend([
                "## 调整建议",
                "",
                "（当前未检测到需要调整的规则。所有规则运行正常。）",
            ])
        lines.extend([
            "",
            "---",
            "*本报告仅呈现数据和建议方向，不强制执行任何修改。决策权在您手中。*",
        ])
        return "\n".join(lines)


class L3ReflectionEngine:
    """
    L3层元反思引擎
    核心原则：
    1. 定期审视L1规则和L2复审的有效性
    2. 生成报告但不自动修改任何规则
    3. 所有调整由用户在阅读报告后决定
    """

    def __init__(self):
        self.report_history: List[GovernanceHealthReport] = []
        self.last_review_at: Optional[datetime] = None
        self.review_interval_hours: int = 24

    def should_review(self) -> bool:
        """判断是否需要进行新一轮审视"""
        if self.last_review_at is None:
            return True
        elapsed = datetime.now() - self.last_review_at
        return elapsed.total_seconds() > self.review_interval_hours * 3600

    def generate_report(
        self,
        rule_stats: Dict[str, Dict[str, Any]],
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
    ) -> GovernanceHealthReport:
        """生成治理健康度报告"""
        performances = []
        recommendations = []

        for rule_id, stats in rule_stats.items():
            rp = RulePerformance(
                rule_id=rule_id,
                rule_name=stats.get("name", rule_id),
                total_triggers=stats.get("total_triggers", 0),
                confirmed_count=stats.get("confirmed", 0),
                dismissed_count=stats.get("dismissed", 0),
                pending_count=stats.get("pending", 0),
                trigger_trend=stats.get("trend", []),
            )
            performances.append(rp)

            if rp.is_high_false_positive():
                recommendations.append({
                    "rule_id": rule_id,
                    "issue": f"误报率 {rp.false_positive_rate:.1%} 超过阈值30%",
                    "suggestion": f"考虑提高 {rule_id} 的触发阈值或调整匹配模式",
                })
            elif rp.is_low_frequency():
                recommendations.append({
                    "rule_id": rule_id,
                    "issue": f"触发频率过低（{rp.total_triggers}次）",
                    "suggestion": f"考虑降低 {rule_id} 的触发阈值或检查规则是否过于严格",
                })

        report = GovernanceHealthReport(
            generated_at=datetime.now(),
            period_start=period_start,
            period_end=period_end,
            rule_performances=performances,
            recommendations=recommendations,
        )

        self.report_history.append(report)
        self.last_review_at = datetime.now()

        return report

    def get_latest_report(self) -> Optional[GovernanceHealthReport]:
        """获取最新的健康度报告"""
        return self.report_history[-1] if self.report_history else None

    def get_report_history(self) -> List[GovernanceHealthReport]:
        """获取历史报告"""
        return self.report_history

    def export_report(self, report: GovernanceHealthReport, filepath: str) -> None:
        """导出报告为Markdown文件"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report.to_markdown())
