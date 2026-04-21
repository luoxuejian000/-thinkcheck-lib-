"""
法律推理谐振评估工具函数
每个函数均对应论文中的可操作化定义，体现关系本体论、矛盾动力论
"""
import re
import numpy as np
from typing import List, Tuple, Dict, Set
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import legal_config as config

# 全局嵌入模型（懒加载）
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(config.EMBEDDING_MODEL)
    return _model

# ---------- 关系本体论实践：术语语义一致性（U指标核心） ----------
def extract_sentences(text: str) -> List[str]:
    """按句号、问号、感叹号分句"""
    text = text.replace('；', '。').replace('！', '。').replace('？', '。')
    sentences = [s.strip() for s in text.split('。') if s.strip()]
    return sentences

def compute_term_consistency_semantic(text: str, term: str) -> Tuple[float, List[str]]:
    sentences = extract_sentences(text)
    term_sentences = [s for s in sentences if term in s]
    if len(term_sentences) < 2:
        return 1.0, term_sentences
    embeddings = get_model().encode(term_sentences)
    sim_matrix = cosine_similarity(embeddings)
    triu_indices = np.triu_indices_from(sim_matrix, k=1)
    if len(triu_indices[0]) == 0:
        return 1.0, term_sentences
    avg_sim = float(np.mean(sim_matrix[triu_indices]))
    return avg_sim, term_sentences

def compute_U_semantic(text: str, terms: List[str] = None) -> float:
    if terms is None:
        terms = config.LEGAL_TERMS
    scores = []
    for term in terms:
        if term in text:
            score, _ = compute_term_consistency_semantic(text, term)
            scores.append(score)
    if not scores:
        return 1.0
    return float(np.mean(scores))

def get_drift_warnings(text: str, threshold: float = None) -> List[Dict]:
    if threshold is None:
        threshold = config.U_DRIFT_THRESHOLD
    warnings = []
    for term in config.LEGAL_TERMS:
        if term in text:
            score, sentences = compute_term_consistency_semantic(text, term)
            if score < threshold:
                warnings.append({
                    "term": term,
                    "consistency": round(score, 3),
                    "threshold": threshold,
                    "occurrences": len(sentences),
                    "sentences": sentences
                })
    return warnings

def compute_D(text: str, terms: List[str] = None) -> float:
    if terms is None:
        terms = config.LEGAL_TERMS
    sentences = extract_sentences(text)
    if len(sentences) <= 1:
        return 0.0
    seen_terms: Set[str] = set()
    first_positions = []
    for i, sent in enumerate(sentences):
        for term in terms:
            if term in sent and term not in seen_terms:
                seen_terms.add(term)
                first_positions.append(i)
    if len(first_positions) <= 1:
        return 0.0
    positions_normalized = [p / len(sentences) for p in first_positions]
    std = np.std(positions_normalized)
    return min(1.0, std * 2.5)

def compute_A(text: str) -> float:
    sentences = extract_sentences(text)
    if not sentences:
        return 0.0
    marker_count = 0
    for sent in sentences:
        for marker in config.ADVERSARIAL_MARKERS:
            if marker in sent:
                marker_count += 1
                break
    marker_density = marker_count / len(sentences)
    contradiction_count = 0
    for term1, term2 in config.CONTRADICTION_RULES:
        if term1 in text and term2 in text:
            contradiction_count += 1
    contradiction_score = min(1.0, contradiction_count * 0.3)
    A = 0.6 * marker_density + 0.4 * contradiction_score
    return min(1.0, A)

def compute_harmony(text: str, lambda_u: float = None, lambda_d: float = None, lambda_a: float = None) -> Dict:
    if lambda_u is None: lambda_u = config.DEFAULT_LAMBDA_U
    if lambda_d is None: lambda_d = config.DEFAULT_LAMBDA_D
    if lambda_a is None: lambda_a = config.DEFAULT_LAMBDA_A
    u = compute_U_semantic(text)
    d = compute_D(text)
    a = compute_A(text)
    h = lambda_u * u + lambda_d * d - lambda_a * a
    drift_warnings = get_drift_warnings(text)
    return {
        "H": round(h, 4),
        "U": round(u, 4),
        "D": round(d, 4),
        "A": round(a, 4),
        "lambda": {"U": lambda_u, "D": lambda_d, "A": lambda_a},
        "drift_warnings": drift_warnings,
        "text_length": len(text),
        "sentence_count": len(extract_sentences(text))
    }