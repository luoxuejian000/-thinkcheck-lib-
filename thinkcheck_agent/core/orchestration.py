"""
OCHR 协调器 - 谐振调谐的指挥中心
"""

import uuid
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from loguru import logger

from .evaluator import DocumentEvaluator
from .actuator import HarmonyActuator
from .challenger import ChallengeAgent
from ochr import RelationshipMapper, ReflectionCavity, BoundaryController


class EvaluationError(Exception):
    """评估错误"""
    pass


class RepairError(Exception):
    """修复错误"""
    pass


class OCHRError(Exception):
    """OCHR 错误"""
    pass


@dataclass
class TaskContext:
    file_path: str
    original_content: str
    workflow_type: str = "default"
    intermediate_results: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))


class Orchestrator:
    """
    协调器 - 管理完整的评估-决策-执行-验证闭环
    """

    def __init__(
        self,
        evaluator: DocumentEvaluator,
        actuator: HarmonyActuator,
        config: Dict,
        enable_ochr: bool = True
    ):
        self.evaluator = evaluator
        self.actuator = actuator
        self.config = config
        self.enable_ochr = enable_ochr

        # 权重配置
        self.lambdas = {"U": 0.4, "D": 0.4, "A": 0.2}

        # OCHR 组件
        if enable_ochr:
            self.relationship_mapper = RelationshipMapper()
            self.reflection_cavity = ReflectionCavity()
            self.boundary_controller = BoundaryController()
            logger.info("OCHR 组件已启用")
        else:
            self.relationship_mapper = None
            self.reflection_cavity = None
            self.boundary_controller = None

        # 双脑博弈质疑组件
        self.challenger = ChallengeAgent(config, actuator)

    def negotiate_weights(self, stakeholder_prefs: Dict[str, Dict[str, float]]):
        """
        协商权重
        """
        avg = {"U": 0.0, "D": 0.0, "A": 0.0}
        n = len(stakeholder_prefs)

        if n > 0:
            for prefs in stakeholder_prefs.values():
                for k in avg:
                    avg[k] += prefs.get(k, 0.0)

            for k in avg:
                avg[k] /= n

        self.lambdas = avg
        logger.info(f"权重协商完成: {self.lambdas}")

    async def orchestrate(
        self,
        context: TaskContext,
        auto_fix: bool = False
    ) -> Dict[str, Any]:
        """
        执行完整的协调流程

        Args:
            context: 任务上下文
            auto_fix: 是否自动修复

        Returns:
            协调结果
        """
        request_id = context.request_id
        logger.info(f"[{request_id}] 开始协调流程")

        result = {
            'status': 'success',
            'request_id': request_id,
            'needs_tuning': False,
            'initial_scores': None,
            'final_scores': None,
            'improvement': 0.0,
            'fixed_content': None,
            'fix_strategy': None,
            'suggestions': [],
            'warnings': [],
            'error': None,
            'ochr_info': {},
            'challenge_report': None
        }

        try:
            # 阶段 1: 边界检查
            if self.enable_ochr and self.boundary_controller:
                allowed, violations = self.boundary_controller.check_permissions(context.original_content)
                result['ochr_info']['boundary_check'] = {
                    'allowed': allowed,
                    'violations': violations
                }

                if self.reflection_cavity:
                    self.reflection_cavity.log_boundary_check(
                        context.file_path,
                        allowed,
                        f"found {len(violations)} violations"
                    )

                if not allowed:
                    result['status'] = 'blocked'
                    result['error'] = "文档包含禁止修改的内容"
                    logger.warning(f"[{request_id}] 文档被边界控制器阻止")
                    return result

            # 阶段 2: 关系分析
            if self.enable_ochr and self.relationship_mapper:
                relationship_info = self.relationship_mapper.analyze(context.original_content)
                result['ochr_info']['relationship_analysis'] = relationship_info

            # 阶段 3: 评估
            logger.info(f"[{request_id}] 开始评估")
            evaluation_report = self.evaluator.evaluate(context.original_content)
            evaluation_dict = evaluation_report.to_dict()

            initial_scores = {
                'U': evaluation_dict['U'],
                'D': evaluation_dict['D'],
                'A': evaluation_dict['A'],
                'H': evaluation_dict['H']
            }
            result['initial_scores'] = initial_scores
            result['suggestions'] = evaluation_dict.get('suggestions', [])
            result['warnings'] = evaluation_dict.get('warnings', [])
            result['needs_tuning'] = evaluation_dict.get('H', 1.0) < 0.7 or evaluation_dict.get('A', 0) > 0.3

            # 构建诊断字典用于质疑
            diagnosis = {
                'needs_tuning': result['needs_tuning'],
                'pathology': self._classify_pathology(initial_scores),
                'harmony_report': initial_scores,
                'suggestions': result['suggestions'],
                'drift_warnings': result['warnings']
            }
            context.intermediate_results['initial_diagnosis'] = diagnosis

            # 阶段 3.5: 双脑博弈质疑
            logger.info(f"[{request_id}] 执行质疑审查")
            challenge_report = self.challenger.challenge(context.original_content, diagnosis)
            context.intermediate_results['challenge_report'] = challenge_report
            result['challenge_report'] = challenge_report

            # 快速检查：如果已经很好了
            if initial_scores['H'] >= 0.9:
                logger.info(f"[{request_id}] 文档和谐度已足够高 (H={initial_scores['H']:.3f})，跳过修复")
                result['status'] = 'no_tuning_needed'
                return result

            # 如果不需要修复或不自动修复
            if not result['needs_tuning'] or not auto_fix:
                logger.info(f"[{request_id}] 文档不需要调谐或自动修复已禁用")
                result['status'] = 'evaluation_only' if not auto_fix else 'no_tuning_needed'
                return result

            # 阶段 4: 执行修复
            logger.info(f"[{request_id}] 开始修复")

            repair_result = self.actuator.tune(context.original_content, diagnosis)

            if not repair_result['success']:
                result['status'] = 'error'
                result['error'] = repair_result.get('error', '修复失败')
                logger.error(f"[{request_id}] 修复失败: {result['error']}")
                return result

            result['fixed_content'] = repair_result['tuned_text']
            result['fix_strategy'] = repair_result['strategy']

            # 阶段 5: 验证修复结果
            logger.info(f"[{request_id}] 验证修复结果")
            final_report = self.evaluator.evaluate(result['fixed_content'])
            final_dict = final_report.to_dict()

            final_scores = {
                'U': final_dict['U'],
                'D': final_dict['D'],
                'A': final_dict['A'],
                'H': final_dict['H']
            }
            result['final_scores'] = final_scores

            # 计算改进
            result['improvement'] = final_scores['H'] - initial_scores['H']

            # 记录审计
            if self.reflection_cavity:
                self.reflection_cavity.log_repair(
                    context.file_path,
                    initial_scores,
                    final_scores,
                    [f"Strategy: {result['fix_strategy']}"]
                )

            logger.info(f"[{request_id}] 协调完成: H={initial_scores['H']:.3f} -> {final_scores['H']:.3f}, improvement={result['improvement']:+.3f}")

        except EvaluationError as e:
            result['status'] = 'error'
            result['error'] = f"评估失败: {e}"
            logger.exception(f"[{request_id}] 评估错误")
        except RepairError as e:
            result['status'] = 'error'
            result['error'] = f"修复失败: {e}"
            logger.exception(f"[{request_id}] 修复错误")
        except OCHRError as e:
            result['status'] = 'error'
            result['error'] = f"OCHR 失败: {e}"
            logger.exception(f"[{request_id}] OCHR 错误")
        except Exception as e:
            result['status'] = 'error'
            result['error'] = f"未知错误: {e}"
            logger.exception(f"[{request_id}] 未知错误")

        return result

    def _classify_pathology(self, scores: Dict[str, float]) -> str:
        """
        分类病理
        """
        h = scores.get('H', 0)
        a = scores.get('A', 0)
        u = scores.get('U', 0)
        d = scores.get('D', 0)

        if h >= 0.6:
            return "谐振态"
        if u < 0.3 and a > 0.7 and h < 0:
            return "逻辑自杀"
        if d < 0.2 and a < 0.3 and h < 0.4:
            return "逻辑空洞"
        if h >= 0.4 and a < 0.2:
            return "度假合格"
        return "需调谐"

    def get_session_summary(self) -> Optional[Dict[str, Any]]:
        """
        获取会话摘要
        """
        if self.reflection_cavity:
            return self.reflection_cavity.get_session_summary()
        return None
