'''主评估器：实践介入论的接口层'''
from typing import List, Optional
from .core import compute_U, compute_D, compute_A, compute_harmony
from .concept_graph import ConceptGraph
from .contradiction_detector import ContradictionDetector
from .report import HarmonyReport
from .intervention.suggestion_engine import ObservationEngine
from .config import DEFAULT_LAMBDA_U, DEFAULT_LAMBDA_D, DEFAULT_LAMBDA_A

class HarmonyEvaluator:
    def __init__(self,
                 domain: str = "general",
                 lambda_u: float = DEFAULT_LAMBDA_U,
                 lambda_d: float = DEFAULT_LAMBDA_D,
                 lambda_a: float = DEFAULT_LAMBDA_A,
                 custom_terms: Optional[List[str]] = None,
                 enable_observations: bool = False):
        self.domain = domain
        self.lambda_u = lambda_u
        self.lambda_d = lambda_d
        self.lambda_a = lambda_a
        self.enable_observations = enable_observations

        from .presets import get_preset
        preset = get_preset(domain)
        self.key_terms = custom_terms if custom_terms else preset.get("terms", [])
        self.contradiction_rules = preset.get("contradiction_rules", [])
        self.detector = ContradictionDetector(self.contradiction_rules)

        self.observation_engine = ObservationEngine() if enable_observations else None
        self.last_report: Optional[HarmonyReport] = None

    def evaluate(self, text: str) -> HarmonyReport:
        concept_graph = ConceptGraph(text, self.key_terms)
        U = compute_U(concept_graph)
        D = compute_D(text, concept_graph)
        A = compute_A(text, self.detector)
        H = compute_harmony(U, D, A, self.lambda_u, self.lambda_d, self.lambda_a)
        drift_warnings = concept_graph.get_drift_warnings()

        report = HarmonyReport(
            H=H, U=U, D=D, A=A,
            lambda_weights={"U": self.lambda_u, "D": self.lambda_d, "A": self.lambda_a},
            drift_warnings=drift_warnings,
            micro_details={"term_consistencies": concept_graph.consistency_scores},
            meso_details={"sentence_count": len(concept_graph.sentences)},
            macro_details={"domain": self.domain},
            audit={"evaluator_version": "3.0.0", "domain": self.domain}
        )

        self.last_report = report
        return report

    def generate_observations(self) -> dict:
        """生成诊断观察（需先调用evaluate）"""
        if not self.last_report:
            return {"observations": [], "invitations": ["请先调用 evaluate()"]}
        if self.observation_engine:
            return self.observation_engine.generate_observations_and_invitations(self.last_report)
        return {"observations": ["观察引擎未启用"], "invitations": []}
