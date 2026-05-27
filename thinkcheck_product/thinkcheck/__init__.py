"""
ThinkCheck - 谐振理论推理监控库
版本: 0.1.0
描述: 自动监控LLM推理质量，在推理质量下降时触发回溯
"""

from .decorator import thinkcheck, thinkcheck_retry
from .core import calculate_h_score, HarmonicMonitor

__version__ = "0.1.0"
__all__ = ["thinkcheck", "thinkcheck_retry", "calculate_h_score", "HarmonicMonitor"]