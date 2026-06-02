"""
ThinkCheck Harmony 指标计算模块
实现四维评估：U, D, A, H
"""

import re
import math
from typing import List, Dict, Tuple
from collections import Counter
import numpy as np


def calculate_unity(text: str) -> float:
    """
    计算统一性 (U)：文档内容的一致性和连贯性
    值范围：[0, 1]
    """
    if not text or len(text.strip()) < 10:
        return 0.0
    
    sentences = re.split(r'[.!?。！？]', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) < 2:
        return 0.5
    
    unity_score = 0.0
    
    # 1. 检查主题一致性（通过关键词密度）
    words = re.findall(r'[\w\u4e00-\u9fff]+', text.lower())
    word_counts = Counter(words)
    common_words = word_counts.most_common(min(10, len(word_counts)))
    
    if common_words:
        total_words = sum(word_counts.values())
        top_words_ratio = sum(count for _, count in common_words) / total_words
        unity_score += min(top_words_ratio * 2, 0.5)
    
    # 2. 检查句子长度一致性
    sentence_lengths = [len(s.split()) for s in sentences]
    if len(sentence_lengths) > 1:
        mean_len = np.mean(sentence_lengths)
        std_len = np.std(sentence_lengths) if mean_len > 0 else 0
        coeff_var = std_len / mean_len if mean_len > 0 else 1.0
        length_consistency = max(0.0, 1.0 - coeff_var)
        unity_score += length_consistency * 0.3
    
    # 3. 检查段落结构
    paragraphs = text.split('\n\n')
    if len(paragraphs) > 1:
        para_lengths = [len(p) for p in paragraphs if p.strip()]
        if para_lengths:
            mean_para = np.mean(para_lengths)
            unity_score += 0.2
    
    return min(1.0, unity_score)


def calculate_development(text: str) -> float:
    """
    计算发展性 (D)：文档内容的丰富度和深度
    值范围：[0, 1]
    """
    if not text or len(text.strip()) < 10:
        return 0.0
    
    development_score = 0.0
    
    # 1. 词汇丰富度
    words = re.findall(r'[\w\u4e00-\u9fff]+', text.lower())
    if words:
        unique_words = set(words)
        ttr = len(unique_words) / len(words)
        development_score += ttr * 0.4
    
    # 2. 文档长度（适中为好）
    text_length = len(text)
    if text_length < 100:
        length_score = text_length / 200
    elif text_length < 1000:
        length_score = 0.5 + (text_length - 100) / 1800
    elif text_length < 5000:
        length_score = 1.0
    else:
        length_score = max(0.5, 1.0 - (text_length - 5000) / 10000)
    development_score += length_score * 0.3
    
    # 3. 句子结构多样性
    sentences = re.split(r'[.!?。！？]', text)
    if len(sentences) > 3:
        sentence_patterns = []
        for s in sentences:
            if s.strip():
                has_numbers = bool(re.search(r'\d', s))
                has_special_chars = bool(re.search(r'[,:;：；]', s))
                pattern = (len(s.split()) > 10, has_numbers, has_special_chars)
                sentence_patterns.append(pattern)
        
        if sentence_patterns:
            unique_patterns = len(set(sentence_patterns))
            pattern_diversity = unique_patterns / len(sentence_patterns)
            development_score += pattern_diversity * 0.3
    
    return min(1.0, development_score)


def calculate_adversarial(text: str) -> float:
    """
    计算对抗性 (A)：文档中的矛盾、冲突和负面内容
    值范围：[0, 1]，值越高表示越有问题
    """
    if not text or len(text.strip()) < 10:
        return 0.0
    
    adversarial_score = 0.0
    
    # 1. 检测否定词和负面词汇
    negative_words = [
        '不是', '不能', '不会', '不要', '没有', '错误', '失败', '问题',
        '危险', '危害', '攻击', '反对', '拒绝', '否认', '质疑', '矛盾',
        '冲突', '争斗', '战争', '死亡', '灾难', '恐怖', '邪恶', '犯罪',
        'not', 'no', 'never', 'cannot', 'won\'t', 'don\'t', 'refuse', 'deny',
        'oppose', 'attack', 'danger', 'risk', 'hazard', 'threat', 'problem',
        'error', 'failure', 'wrong', 'bad', 'evil', 'crime', 'war', 'death'
    ]
    
    words = re.findall(r'[\w\u4e00-\u9fff]+', text.lower())
    negative_count = sum(1 for word in words if word in negative_words)
    if words:
        negative_ratio = negative_count / len(words)
        adversarial_score += min(negative_ratio * 10, 0.5)
    
    # 2. 检测逻辑矛盾模式
    contradiction_patterns = [
        r'(既是|是|等于).*?(又不是|不是|不等于)',
        r'(必须|应该|要).*?(不能|不要|不应该)',
        r'(所有|全部|一切).*?(有些|部分|例外)',
        r'(肯定|一定|绝对).*?(可能|也许|不确定)'
    ]
    
    for pattern in contradiction_patterns:
        if re.search(pattern, text):
            adversarial_score += 0.2
    
    # 3. 检测情感强度
    exclamation_count = text.count('!') + text.count('！')
    question_count = text.count('?') + text.count('？')
    total_sentences = max(1, len(re.split(r'[.!?。！？]', text)))
    emotion_ratio = (exclamation_count + question_count) / total_sentences
    adversarial_score += min(emotion_ratio * 0.5, 0.3)
    
    return min(1.0, adversarial_score)


def calculate_harmony(text: str) -> Dict[str, float]:
    """
    计算综合和谐度 (H) 及所有四个维度
    返回：{'U': u_score, 'D': d_score, 'A': a_score, 'H': h_score}
    """
    u = calculate_unity(text)
    d = calculate_development(text)
    a = calculate_adversarial(text)
    
    # 综合和谐度计算公式：H = 0.4*U + 0.4*D - 0.2*A
    # 但确保 H 在 [0, 1] 范围内
    h_raw = 0.4 * u + 0.4 * d - 0.2 * a
    h = max(0.0, min(1.0, h_raw))
    
    return {
        'U': u,
        'D': d,
        'A': a,
        'H': h
    }


# 为了兼容验证脚本，添加别名
compute_unity = calculate_unity
compute_development = calculate_development
compute_adversariality = calculate_adversarial


def compute_harmony(u: float, d: float, a: float, w_u: float, w_d: float, w_a: float) -> float:
    """
    兼容版本的和谐度计算函数
    """
    return w_u * u + w_d * d - w_a * a
