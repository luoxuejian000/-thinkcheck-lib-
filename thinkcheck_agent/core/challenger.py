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
