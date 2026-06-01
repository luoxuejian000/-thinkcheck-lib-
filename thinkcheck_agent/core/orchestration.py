"""
OCHR 协调器：谐振调谐的指挥中心
"""
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from .evaluator import DocumentEvaluator
from .actuator import HarmonyActuator
from loguru import logger


@dataclass
class TaskContext:
    file_path: str
    original_content: str
    workflow_type: str = "default"
    intermediate_results: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)


class Orchestrator:
    def __init__(self, evaluator: DocumentEvaluator, actuator: HarmonyActuator, config: Dict):
        self.evaluator = evaluator
        self.actuator = actuator
        self.config = config
        self.lambdas = {"U": 0.4, "D": 0.4, "A": 0.2}

    def negotiate_weights(self, stakeholder_prefs: Dict[str, Dict[str, float]]):
        avg = {"U": 0.0, "D": 0.0, "A": 0.0}
        for prefs in stakeholder_prefs.values():
            for k in avg:
                avg[k] += prefs.get(k, 0.0)
        n = len(stakeholder_prefs)
        if n > 0:
            for k in avg:
                avg[k] /= n
        self.lambdas = avg
        logger.info(f"权重协商完成：{self.lambdas}")

    async def orchestrate(self, context: TaskContext) -> Dict[str, Any]:
        diagnosis = self.evaluator.evaluate(context.original_content)
        initial_h = diagnosis.get('harmony_report', {}).get('H', 0)
        context.intermediate_results['initial_diagnosis'] = diagnosis

        if not diagnosis.get('needs_tuning'):
            return {"status": "no_tuning_needed", "initial_harmony": initial_h}

        tuning_result = self.actuator.tune(context.original_content, diagnosis)
        if tuning_result['strategy'] == 'failed':
            return {"status": "error", "error": "Tuning failed"}

        final_diagnosis = self.evaluator.evaluate(tuning_result['tuned_text'])
        final_h = final_diagnosis.get('harmony_report', {}).get('H', 0)
        improvement = final_h - initial_h

        logger.info(f"调谐成功。H: {initial_h:.3f} → {final_h:.3f}, 提升: {improvement:+.3f}")
        return {
            "status": "success",
            "initial_harmony": initial_h,
            "final_harmony": final_h,
            "improvement": improvement,
            "fix_strategy": tuning_result['strategy'],
            "suggestions_applied": diagnosis.get('suggestions', []),
            "fixed_content": tuning_result['tuned_text'],
            "drift_warnings": diagnosis.get('drift_warnings', [])
        }