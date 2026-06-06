"""
ThinkCheck 评估器封装
对核心 ThinkCheck Harmony SDK 进行工程化封装，提供健壮的评估接口。
集成长文本处理、语义向量检测、可配置权重等功能。
"""
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from loguru import logger
import re
import numpy as np

try:
    from thinkcheck_harmony import HarmonyEvaluator
    from thinkcheck_harmony.metrics import (
        calculate_unity, calculate_development, 
        calculate_adversarial, calculate_harmony,
        get_current_weights
    )
except ImportError:
    logger.error("未找到 thinkcheck_harmony 模块。请确保它已安装或在 Python 路径中。")
    HarmonyEvaluator = None

from .long_text import TextChunker, InterBlockContradictionTracker


class DocumentEvaluator:
    """文档评估器，负责调用 ThinkCheck 引擎进行 U/D/A/H 四维评估。
    集成长文本处理、语义向量检测、可配置权重等功能。
    """

    def __init__(self, config: Dict[str, Any]):
        tc_config = config.get('thinkcheck', {})
        self.domain = tc_config.get('default_domain', 'general')
        self.harmony_threshold = tc_config.get('harmony_threshold', 0.7)
        self.adversarial_threshold = tc_config.get('adversarial_threshold', 0.3)
        
        # 配置权重（支持审计）
        self.lambda_u = float(config.get('LAMBDA_U', tc_config.get('lambda_u', 0.4)))
        self.lambda_d = float(config.get('LAMBDA_D', tc_config.get('lambda_d', 0.4)))
        self.lambda_a = float(config.get('LAMBDA_A', tc_config.get('lambda_a', 0.2)))
        
        # 长文本处理配置
        self.semantic_threshold = float(config.get('SEMANTIC_CONTRADICTION_THRESHOLD', -0.2))
        
        # 转折连词列表
        self.contrast_conjunctions = {'但', '然而', '却', '不过', '只是', '可惜', '反而', '相反', '尽管如此', '但是', '可'}
        
        # 长文本处理组件
        self.text_chunker = TextChunker(max_chars_per_chunk=4000)
        self.cross_tracker = None
        
        # 初始化语义模型（如果可用）
        self.semantic_model = None
        self.embedder = None
        if hasattr(self, 'embedder') and self.embedder is not None:
            self.semantic_model = self.embedder
        else:
            try:
                from sentence_transformers import SentenceTransformer
                self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("语义模型加载成功")
            except Exception as e:
                logger.warning(f"语义模型加载失败，将使用基础评估: {e}")
                self.semantic_model = None
        
        self.evaluator = None
        if HarmonyEvaluator is not None:
            try:
                self.evaluator = HarmonyEvaluator(domain=self.domain, enable_suggestions=tc_config.get('enable_suggestions', True))
                logger.info("ThinkCheck 评估器初始化成功。")
            except Exception as e:
                logger.error(f"初始化 ThinkCheck 评估器失败: {e}")
        else:
            logger.error("HarmonyEvaluator 不可用。所有评估请求将返回默认值。")

    def _split_long_sentence(self, sentence: str, max_chars: int = 200) -> List[str]:
        """
        将长句子拆分为较短的部分
        """
        if len(sentence) <= max_chars:
            return [sentence]
        parts = []
        current = ''
        for char in sentence:
            current += char
            if len(current) >= max_chars and char in '，。！？；：,.;!?':
                parts.append(current.strip())
                current = ''
        if current.strip():
            parts.append(current.strip())
        return parts if parts else [sentence]

    def _safe_encode(self, sentences: List[str]) -> tuple[Optional[Dict[str, np.ndarray]], List[str]]:
        """
        安全地编码句子，处理长句子
        返回：(句子到嵌入的映射, 处理后的句子列表)
        """
        if self.semantic_model is None:
            return None, sentences
        
        processed = []
        for sent in sentences:
            if len(sent) > 200:
                sub_parts = self._split_long_sentence(sent)
                processed.extend(sub_parts)
            else:
                processed.append(sent)
        
        try:
            embeddings = self.semantic_model.encode(processed, convert_to_numpy=True)
        except Exception as e:
            logger.warning(f"语义编码失败: {e}")
            return None, processed
        
        long_sent_map = {}
        emb_idx = 0
        for sent in sentences:
            if len(sent) > 200:
                sub_parts = self._split_long_sentence(sent)
                sub_embs = embeddings[emb_idx:emb_idx+len(sub_parts)]
                long_sent_map[sent] = np.mean(sub_embs, axis=0)
                emb_idx += len(sub_parts)
            else:
                long_sent_map[sent] = embeddings[emb_idx]
                emb_idx += 1
        
        return long_sent_map, processed

    def _get_sentence_embedding(self, sentence: str) -> Optional[np.ndarray]:
        """
        获取单个句子的嵌入向量
        """
        if self.semantic_model is None:
            return None
        try:
            return self.semantic_model.encode([sentence], convert_to_numpy=True)[0]
        except Exception as e:
            logger.warning(f"句子编码失败: {e}")
            return None

    def _detect_semantic_contradictions(self, text: str) -> float:
        """
        检测语义向量对立
        返回：语义矛盾分数 [0, 1]，越高表示矛盾越多
        """
        if self.semantic_model is None:
            return 0.0
        
        sentences = re.split(r'[.!?。！？]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 2:
            return 0.0
        
        contradiction_score = 0.0
        
        # 检测转折连词后的语义对立
        for conj in self.contrast_conjunctions:
            for sent in sentences:
                if conj in sent:
                    parts = sent.split(conj)
                    if len(parts) >= 2:
                        before_part = parts[0].strip()
                        after_part = parts[1].strip()
                        if before_part and after_part:
                            # 获取语义向量
                            before_emb = self._get_sentence_embedding(before_part)
                            after_emb = self._get_sentence_embedding(after_part)
                            
                            if before_emb is not None and after_emb is not None:
                                # 计算语义相似度
                                sim = np.dot(before_emb, after_emb) / (
                                    np.linalg.norm(before_emb) * np.linalg.norm(after_emb) + 1e-8)
                                # 如果相似度低于阈值，认为有语义对立
                                if sim < self.semantic_threshold:
                                    contradiction_score += 0.1
        
        # 检测跨块矛盾（如果是长文本）
        if len(text) > 4000:
            cross_contradictions = self._detect_long_text_contradictions(text)
            contradiction_score += cross_contradictions
        
        return min(1.0, contradiction_score)

    def _detect_long_text_contradictions(self, text: str) -> float:
        """
        检测长文本中的跨块矛盾
        """
        if self.semantic_model is None:
            return 0.0
        
        sentences = re.split(r'[.!?。！？]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 2:
            return 0.0
        
        # 分块
        chunks = self.text_chunker.chunk_sentences(sentences)
        
        if len(chunks) < 2:
            return 0.0
        
        contradiction_score = 0.0
        
        # 初始化跨块矛盾追踪器
        if self.cross_tracker is None:
            self.cross_tracker = InterBlockContradictionTracker(self.semantic_model, self.semantic_threshold)
        else:
            self.cross_tracker.clear()
        
        # 注册各个块的概念
        for block_idx, chunk_indices in enumerate(chunks):
            chunk_sentences = [sentences[i] for i in chunk_indices]
            # 获取嵌入
            emb_map, _ = self._safe_encode(chunk_sentences)
            if emb_map:
                embeddings = [emb_map[sent] for sent in chunk_sentences]
                self.cross_tracker.register_block_concepts(block_idx, chunk_sentences, chunk_indices, embeddings)
        
        # 检测跨块矛盾
        cross_edges = self.cross_tracker.detect_cross_block_contradictions()
        
        if cross_edges:
            contradiction_score += min(0.3, len(cross_edges) * 0.05)
        
        return contradiction_score

    def evaluate(self, content: str) -> Dict[str, Any]:
        """
        评估文档，使用增强的方法
        返回完整的评估结果，包含所有四个维度的分数
        """
        if not content or not content.strip():
            logger.warning("空文档")
            return {
                'needs_tuning': False,
                'harmony_report': {
                    'U': 0.0, 'D': 0.0, 'A': 0.0, 'H': 0.0,
                    'lambda_u': self.lambda_u,
                    'lambda_d': self.lambda_d,
                    'lambda_a': self.lambda_a
                },
                'suggestions': [],
                'warnings': ['文档为空'],
                'pathology': '空文档'
            }
        
        try:
            # 基础评估
            scores = calculate_harmony(content, self.lambda_u, self.lambda_d, self.lambda_a)
            
            # 增强的对抗性检测
            enhanced_adversarial = scores['A'] + self._detect_semantic_contradictions(content)
            scores['A'] = min(1.0, enhanced_adversarial)
            
            # 重新计算和谐度
            scores['H'] = max(0.0, min(1.0, 
                self.lambda_u * scores['U'] + 
                self.lambda_d * scores['D'] - 
                self.lambda_a * scores['A']))
            
            # 使用原始评估器获取建议和警告
            try:
                report = self.evaluator.evaluate(content) if self.evaluator else None
                report_dict = report.to_dict() if report else {}
                suggestions = report_dict.get('suggestions', [])
                warnings = report_dict.get('warnings', [])
            except Exception as e:
                logger.warning(f"原始评估器失败，使用默认值: {e}")
                suggestions = []
                warnings = []
            
            # 诊断分类
            pathology = self._classify_pathology(scores)
            
            needs_tuning = scores['H'] < self.harmony_threshold or scores['A'] > self.adversarial_threshold
            
            result = {
                'needs_tuning': needs_tuning,
                'harmony_report': scores,
                'suggestions': suggestions,
                'warnings': warnings,
                'pathology': pathology
            }
            
            logger.info(f"评估完成。H={scores['H']:.3f}, A={scores['A']:.3f}, 判定: {pathology}")
            return result
            
        except Exception as e:
            logger.exception(f"评估过程中发生意外错误: {e}")
            return {
                'needs_tuning': False,
                'error': f"Evaluation failed: {str(e)}",
                'harmony_report': {
                    'U': 0.0, 'D': 0.0, 'A': 0.0, 'H': 0.0,
                    'lambda_u': self.lambda_u,
                    'lambda_d': self.lambda_d,
                    'lambda_a': self.lambda_a
                },
                'suggestions': [],
                'warnings': [str(e)],
                'pathology': '评估错误'
            }

    def _classify_pathology(self, scores: Dict) -> str:
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
    
    def get_audit_info(self) -> Dict[str, Any]:
        """
        获取审计信息，包括当前的权重配置
        """
        return {
            'lambda_u': self.lambda_u,
            'lambda_d': self.lambda_d,
            'lambda_a': self.lambda_a,
            'default_weights': get_current_weights(),
            'harmony_threshold': self.harmony_threshold,
            'adversarial_threshold': self.adversarial_threshold,
            'semantic_model_available': self.semantic_model is not None
        }
