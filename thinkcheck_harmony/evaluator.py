"""
ThinkCheck Harmony 评估器
支持可配置权重、长文本处理、审计信息记录等功能
"""

import re
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from loguru import logger
from .metrics import calculate_harmony, get_current_weights, ContradictionDetector, _get_global_detector


class HarmonyEvaluator:
    """
    文档和谐度评估器
    执行四维评估：U, D, A, H
    支持可配置权重和语义模型
    """
    
    def __init__(self, domain: str = "general", enable_suggestions: bool = True,
                 lambda_u: float = 0.4, lambda_d: float = 0.4, lambda_a: float = 0.2,
                 semantic_model=None):
        """
        初始化评估器
        
        Args:
            domain: 领域类型
            enable_suggestions: 是否启用建议生成
            lambda_u: U维度权重
            lambda_d: D维度权重
            lambda_a: A维度权重
            semantic_model: 可选的语义模型，用于句子嵌入
        """
        self.domain = domain
        self.enable_suggestions = enable_suggestions
        self.max_chunk_size = 100000  # 超过此大小的文档进行分块处理
        self.window_size = 512
        self.step_size = 256
        
        # 权重配置
        self.lambda_u = lambda_u
        self.lambda_d = lambda_d
        self.lambda_a = lambda_a
        
        # 审计信息配置
        self.weight_source = "default"
        self.weight_history = []
        
        # 记录初始权重配置
        self.weight_history.append({
            "timestamp": datetime.now().isoformat(),
            "lambda_u": self.lambda_u,
            "lambda_d": self.lambda_d,
            "lambda_a": self.lambda_a,
            "source": "default"
        })
        
        # 初始化矛盾检测器
        if semantic_model:
            # 如果提供了语义模型，创建新的检测器实例
            self.detector = ContradictionDetector(semantic_model=semantic_model)
        else:
            # 否则使用全局检测器（向后兼容）
            self.detector = _get_global_detector()
        
    def evaluate(self, text: str) -> 'HarmonyReport':
        """
        评估文档的四维和谐度
        支持可配置权重
        
        Args:
            text: 待评估的文档文本
            
        Returns:
            HarmonyReport 对象
        """
        if not text or not text.strip():
            logger.warning("空文档")
            return HarmonyReport(
                scores={
                    'U': 0.0, 'D': 0.0, 'A': 0.0, 'H': 0.0,
                    'lambda_u': self.lambda_u,
                    'lambda_d': self.lambda_d,
                    'lambda_a': self.lambda_a
                },
                suggestions=[],
                warnings=['文档为空']
            )
        
        text_length = len(text)
        logger.info(f"开始评估文档，长度: {text_length} 字符")
        
        # 对于长文档，使用分块并行计算
        if text_length > self.max_chunk_size:
            scores = self._evaluate_large_document(text)
        else:
            scores = calculate_harmony(text, self.lambda_u, self.lambda_d, self.lambda_a)
        
        # 生成建议和警告
        suggestions = self._generate_suggestions(scores, text) if self.enable_suggestions else []
        warnings = self._generate_warnings(scores, text)
        
        report = HarmonyReport(
            scores=scores,
            suggestions=suggestions,
            warnings=warnings,
            text_length=text_length
        )
        
        logger.info(f"评估完成。H={scores['H']:.3f}, U={scores['U']:.3f}, D={scores['D']:.3f}, A={scores['A']:.3f}")
        return report
    
    def _evaluate_large_document(self, text: str) -> Dict[str, float]:
        """
        处理长文档：分块并行计算，然后聚合结果
        """
        logger.info("检测到长文档，启用分块处理")
        
        # 按段落分块
        chunks = self._split_into_chunks(text)
        
        if len(chunks) == 1:
            return calculate_harmony(chunks[0], self.lambda_u, self.lambda_d, self.lambda_a)
        
        # 并行计算每个块的分数
        chunk_scores = []
        with ThreadPoolExecutor(max_workers=min(4, len(chunks))) as executor:
            futures = {executor.submit(calculate_harmony, chunk, 
                                       self.lambda_u, self.lambda_d, self.lambda_a): chunk 
                       for chunk in chunks}
            for future in as_completed(futures):
                try:
                    score = future.result()
                    chunk_scores.append(score)
                except Exception as e:
                    logger.error(f"块评估失败: {e}")
        
        if not chunk_scores:
            return {
                'U': 0.0, 'D': 0.0, 'A': 0.0, 'H': 0.0,
                'lambda_u': self.lambda_u,
                'lambda_d': self.lambda_d,
                'lambda_a': self.lambda_a
            }
        
        # 聚合分数（加权平均）
        total_weight = sum(len(chunk) for chunk in chunks)
        aggregated = {
            'U': 0.0, 'D': 0.0, 'A': 0.0,
            'lambda_u': self.lambda_u,
            'lambda_d': self.lambda_d,
            'lambda_a': self.lambda_a
        }
        
        for i, score in enumerate(chunk_scores):
            weight = len(chunks[i]) / total_weight if total_weight > 0 else 1.0 / len(chunk_scores)
            aggregated['U'] += score['U'] * weight
            aggregated['D'] += score['D'] * weight
            aggregated['A'] += score['A'] * weight
        
        aggregated['H'] = max(0.0, min(1.0, 
            self.lambda_u * aggregated['U'] + 
            self.lambda_d * aggregated['D'] - 
            self.lambda_a * aggregated['A']))
        
        # 额外计算整体和谐度（使用滑动窗口）
        if len(text) > 2000:
            h_scores = []
            for i in range(0, len(text) - self.window_size, self.step_size):
                window = text[i:i + self.window_size]
                window_score = calculate_harmony(window, self.lambda_u, self.lambda_d, self.lambda_a)
                h_scores.append(window_score['H'])
            
            if h_scores:
                aggregated['H'] = (aggregated['H'] + sum(h_scores) / len(h_scores)) / 2
        
        return aggregated
    
    def _split_into_chunks(self, text: str) -> List[str]:
        """
        将文档分割成合适的块
        """
        chunks = []
        paragraphs = text.split('\n\n')
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) < self.max_chunk_size:
                current_chunk += para + '\n\n'
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + '\n\n'
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else [text]
    
    def _generate_suggestions(self, scores: Dict[str, float], text: str) -> List[str]:
        """
        基于评估分数生成改进建议
        """
        suggestions = []
        
        if scores['U'] < 0.5:
            suggestions.append("建议增强文档的统一性：保持主题一致，避免频繁切换话题")
        
        if scores['D'] < 0.5:
            suggestions.append("建议增强文档的发展性：增加更多细节和支持性内容")
        
        if scores['A'] > 0.5:
            suggestions.append("建议降低文档的对抗性：减少负面词汇和可能的逻辑矛盾")
        
        if scores['H'] < 0.6:
            suggestions.append("整体和谐度有待提高，建议综合改进")
        
        return suggestions
    
    def _generate_warnings(self, scores: Dict[str, float], text: str) -> List[str]:
        """
        生成警告信息
        """
        warnings = []
        
        if scores['A'] > 0.7:
            warnings.append("检测到高对抗性内容，请仔细检查文档中的矛盾和负面表达")
        
        if scores['H'] < 0.3:
            warnings.append("文档和谐度过低，建议进行全面审查")
        
        return warnings
    
    def update_weights(self, lambda_u: float = None, lambda_d: float = None, lambda_a: float = None, source: str = "manual"):
        """
        更新权重配置
        
        Args:
            lambda_u: U维度权重
            lambda_d: D维度权重
            lambda_a: A维度权重
            source: 权重来源标识
        """
        if lambda_u is not None:
            self.lambda_u = lambda_u
        if lambda_d is not None:
            self.lambda_d = lambda_d
        if lambda_a is not None:
            self.lambda_a = lambda_a
        
        # 更新权重来源
        self.weight_source = source
        
        # 记录权重修改历史
        self.weight_history.append({
            "timestamp": datetime.now().isoformat(),
            "lambda_u": self.lambda_u,
            "lambda_d": self.lambda_d,
            "lambda_a": self.lambda_a,
            "source": source
        })
        
        logger.info(f"权重已更新: U={self.lambda_u}, D={self.lambda_d}, A={self.lambda_a}, source={source}")
    
    def get_audit_info(self) -> Dict[str, Any]:
        """
        获取审计信息
        
        Returns:
            包含权重配置、来源和历史的完整审计信息
        """
        return {
            'lambda_u': self.lambda_u,
            'lambda_d': self.lambda_d,
            'lambda_a': self.lambda_a,
            'weight_source': self.weight_source,
            'weight_history': self.weight_history[-5:],  # 最近5次修改
            'default_weights': get_current_weights(),
            'domain': self.domain,
            'max_chunk_size': self.max_chunk_size
        }


class HarmonyReport:
    """
    评估结果报告
    """
    
    def __init__(
        self,
        scores: Dict[str, any],
        suggestions: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None,
        text_length: Optional[int] = None
    ):
        self.scores = scores
        self.suggestions = suggestions or []
        self.warnings = warnings or []
        self.text_length = text_length or 0
        # 获取A值的详细构成（如果有）
        self.audit = {
            'A_detail': scores.get('A_detail', None)
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        """
        result = {
            'U': self.scores.get('U', 0.0),
            'D': self.scores.get('D', 0.0),
            'A': self.scores.get('A', 0.0),
            'H': self.scores.get('H', 0.0),
            'lambda_u': self.scores.get('lambda_u', 0.4),
            'lambda_d': self.scores.get('lambda_d', 0.4),
            'lambda_a': self.scores.get('lambda_a', 0.2),
            'suggestions': self.suggestions,
            'warnings': self.warnings,
            'text_length': self.text_length
        }
        # 添加审计信息
        if self.audit.get('A_detail'):
            result['A_detail'] = self.audit['A_detail']
        return result
    
    def get(self, key: str, default: any = None) -> any:
        """
        兼容字典访问方式的get方法
        """
        if key == 'harmony_report':
            return self
        if key in self.scores:
            return self.scores[key]
        if key == 'A_detail' and self.audit.get('A_detail'):
            return self.audit['A_detail']
        return default
    
    def __getitem__(self, key: str) -> any:
        """
        兼容字典访问方式
        """
        return self.get(key)
