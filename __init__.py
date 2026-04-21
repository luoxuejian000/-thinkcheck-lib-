"""
ThinkCheck法律专业版 - 基于晶脉哲学与谐振理论
提供法律推理过程的质量评估，检测概念漂移、逻辑矛盾
"""

from .legal_monitor import LegalReasoningMonitor, StandaloneLegalMonitor
from .legal_utils import compute_harmony, compute_U_semantic, get_drift_warnings
from .legal_config import (
    DEFAULT_LAMBDA_U, DEFAULT_LAMBDA_D, DEFAULT_LAMBDA_A,
    LEGAL_TERMS, U_DRIFT_THRESHOLD
)

__version__ = "2.0.0"
__all__ = [
    "LegalReasoningMonitor",
    "StandaloneLegalMonitor",
    "compute_harmony",
    "compute_U_semantic",
    "get_drift_warnings",
    "DEFAULT_LAMBDA_U",
    "DEFAULT_LAMBDA_D",
    "DEFAULT_LAMBDA_A",
    "LEGAL_TERMS",
    "U_DRIFT_THRESHOLD"
]