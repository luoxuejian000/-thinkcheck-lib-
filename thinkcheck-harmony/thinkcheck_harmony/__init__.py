'''ThinkCheck Harmony 3.0 - 通用谐振评估与调谐SDK'''
from .evaluator import HarmonyEvaluator
from .report import HarmonyReport
from .relationship_graph import RelationshipGraph, Node, Edge, EdgeType
from .contradiction_lifecycle import ContradictionLifecycleManager, Contradiction, ContradictionStage
from .contradiction_detector import ContradictionDetector
from .report_generator import DiagnosticReport
from .intervention.base import BaseHarvester
from .intervention.suggestion_engine import ObservationEngine
from .presets import get_preset

__version__ = "3.0.0"
__all__ = [
    "HarmonyEvaluator",
    "HarmonyReport",
    "RelationshipGraph",
    "Node",
    "Edge",
    "EdgeType",
    "ContradictionLifecycleManager",
    "Contradiction",
    "ContradictionStage",
    "ContradictionDetector",
    "DiagnosticReport",
    "BaseHarvester",
    "ObservationEngine",
    "get_preset"
]