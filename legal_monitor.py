"""
法律专业版推理监控器
提供独立监控器和继承版本
"""
import sys
import os

# 尝试导入1.0的基类（可选）
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'thinkcheck'))
    from thinkcheck.monitor import ReasoningMonitor
    BASE_CLASS = ReasoningMonitor
except ImportError:
    BASE_CLASS = object

from .legal_utils import compute_harmony
from .legal_config import DEFAULT_LAMBDA_U, DEFAULT_LAMBDA_D, DEFAULT_LAMBDA_A


class LegalReasoningMonitor(BASE_CLASS):
    """继承版本（需要1.0支持）"""
    def __init__(self, lambda_u=None, lambda_d=None, lambda_a=None, **kwargs):
        super().__init__(**kwargs)
        self.lambda_u = lambda_u if lambda_u is not None else DEFAULT_LAMBDA_U
        self.lambda_d = lambda_d if lambda_d is not None else DEFAULT_LAMBDA_D
        self.lambda_a = lambda_a if lambda_a is not None else DEFAULT_LAMBDA_A
        self.last_full_report = None

    def _compute_resonance_score(self, tokens):
        if isinstance(tokens, list):
            text = "".join(tokens) if tokens else ""
        else:
            text = str(tokens)
        result = compute_harmony(text, self.lambda_u, self.lambda_d, self.lambda_a)
        self.last_full_report = result
        return result["H"]

    def get_full_report(self):
        return self.last_full_report

    def evaluate_text(self, text: str) -> float:
        result = compute_harmony(text, self.lambda_u, self.lambda_d, self.lambda_a)
        self.last_full_report = result
        return result["H"]


class StandaloneLegalMonitor:
    """独立监控器，不依赖1.0基础类"""
    def __init__(self, lambda_u=None, lambda_d=None, lambda_a=None):
        self.lambda_u = lambda_u if lambda_u is not None else DEFAULT_LAMBDA_U
        self.lambda_d = lambda_d if lambda_d is not None else DEFAULT_LAMBDA_D
        self.lambda_a = lambda_a if lambda_a is not None else DEFAULT_LAMBDA_A
        self.last_report = None

    def evaluate(self, text: str) -> float:
        self.last_report = compute_harmony(
            text, self.lambda_u, self.lambda_d, self.lambda_a
        )
        return self.last_report["H"]

    def get_report(self):
        return self.last_report