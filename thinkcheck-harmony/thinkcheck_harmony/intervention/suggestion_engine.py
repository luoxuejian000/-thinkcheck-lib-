'''诊断观察与邀请引擎 - 公理三：只看病，不开方'''
from typing import List, Dict, Any
from .base import BaseHarvester
from .term_alignment import TermAlignmentHarvester
from .weight_negotiation import WeightNegotiationHarvester
from ..report import HarmonyReport


class ObservationEngine:
    '''诊断观察与邀请引擎 - 输出纯观察数据，不包含行动建议'''

    def __init__(self, harvesters: List[BaseHarvester] = None):
        self.harvesters = harvesters or [
            TermAlignmentHarvester(),
            WeightNegotiationHarvester(),
        ]

    def register_harvester(self, harvester: BaseHarvester):
        self.harvesters.append(harvester)

    def generate_observations_and_invitations(self, report: HarmonyReport) -> Dict[str, Any]:
        """
        生成诊断观察与用户邀请

        输出格式：
        {
            "observations": ["检测到术语使用不一致"],
            "invitations": ["您可以考虑核对术语定义是否一致", "如需协助，请回复 /help"]
        }
        """
        observations = []
        invitations = []

        # 从报告中提取观测数据
        if hasattr(report, 'a_trajectory') and report.a_trajectory:
            if max(report.a_trajectory) > 0.6:
                observations.append("检测到高对抗性信号（A值峰值超过0.6）")
                invitations.append("您可以查看矛盾点定位部分的详细数据")

        if hasattr(report, 'u_trajectory') and report.u_trajectory:
            if min(report.u_trajectory) < 0.15:
                observations.append("检测到低确定性信号（U值谷值低于0.15）")
                invitations.append("您可以审视核心概念的定义是否清晰")

        # 从harvester中提取观察
        for harvester in self.harvesters:
            if harvester.analyze(report):
                harvester_observations = harvester.generate_observations(report)
                if harvester_observations:
                    observations.extend(harvester_observations)

        return {
            "observations": observations if observations else ["未检测到显著模式"],
            "invitations": invitations if invitations else ["如需进一步分析，请使用 /analyze 命令"]
        }

    # 保留旧方法以维持向后兼容（标记为废弃）
    def generate_suggestions(self, report: HarmonyReport) -> List[str]:
        """
        [已废弃] 请使用 generate_observations_and_invitations()
        本方法仅为了向后兼容保留
        """
        result = self.generate_observations_and_invitations(report)
        # 将观察转化为"邀请式"建议
        suggestions = []
        for obs in result["observations"]:
            suggestions.append(f"观察到：{obs}")
        for inv in result["invitations"]:
            suggestions.append(inv)
        return suggestions
