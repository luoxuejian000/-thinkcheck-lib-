"""
ThinkCheck Harmony SDK - 四维文档评估引擎
U: 统一性 (Unity)
D: 发展性 (Development) 
A: 对抗性 (Adversarial)
H: 和谐度 (Harmony)
"""

from .evaluator import HarmonyEvaluator
from .metrics import calculate_unity, calculate_development, calculate_adversarial, calculate_harmony

__version__ = "3.0.0"
__all__ = [
    "HarmonyEvaluator",
    "calculate_unity",
    "calculate_development",
    "calculate_adversarial",
    "calculate_harmony",
]
