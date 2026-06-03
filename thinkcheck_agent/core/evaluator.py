"""
ThinkCheck 评估器封装
对核心 ThinkCheck Harmony SDK 进行工程化封装，提供健壮的评估接口。
"""
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from loguru import logger

try:
    from thinkcheck_harmony import HarmonyEvaluator
except ImportError:
    logger.error("未找到 thinkcheck_harmony 模块。请确保它已安装或在 Python 路径中。")
    HarmonyEvaluator = None

class DocumentEvaluator:
    """文档评估器，负责调用 ThinkCheck 引擎进行 U/D/A/H 四维评估。"""

    def __init__(self, config: Dict[str, Any]):
        tc_config = config.get('thinkcheck', {})
        self.domain = tc_config.get('default_domain', 'general')
        self.harmony_threshold = tc_config.get('harmony_threshold', 0.7)
        self.adversarial_threshold = tc_config.get('adversarial_threshold', 0.3)
        self.evaluator = None
        if HarmonyEvaluator is not None:
            try:
                self.evaluator = HarmonyEvaluator(domain=self.domain, enable_suggestions=tc_config.get('enable_suggestions', True))
                logger.info("ThinkCheck 评估器初始化成功。")
            except Exception as e:
                logger.error(f"初始化 ThinkCheck 评估器失败: {e}")
        else:
            logger.error("HarmonyEvaluator 不可用。所有评估请求将返回默认值。")

    def evaluate(self, content: str) -> Dict[str, Union[bool, Dict, List, str]]:
        if not self.evaluator:
            logger.warning("评估器不可用，返回默认诊断。")
            return {"needs_tuning": False, "error": "Evaluator not available"}
        try:
            report = self.evaluator.evaluate(content)
            report_dict = report.to_dict()
            signal = {
                "needs_tuning": report_dict.get('H', 1.0) < self.harmony_threshold or report_dict.get('A', 0) > self.adversarial_threshold,
                "harmony_report": report_dict,
                "suggestions": report_dict.get('suggestions', []),
                "drift_warnings": report_dict.get('warnings', []),
                "pathology": self._classify_pathology(report_dict)
            }
            logger.info(f"评估完成。H={report_dict.get('H'):.3f}, A={report_dict.get('A'):.3f}, 判定: {signal['pathology']}")
            return signal
        except Exception as e:
            logger.exception(f"评估过程中发生意外错误: {e}")
            return {"needs_tuning": False, "error": f"Evaluation failed: {str(e)}"}

    def _classify_pathology(self, report: Dict) -> str:
        h, a, u, d = report.get('H', 0), report.get('A', 0), report.get('U', 0), report.get('D', 0)
        if h >= 0.6: return "谐振态"
        if u < 0.3 and a > 0.7 and h < 0: return "逻辑自杀"
        if d < 0.2 and a < 0.3 and h < 0.4: return "逻辑空洞"
        if h >= 0.4 and a < 0.2: return "度假合格"
        return "需调谐"