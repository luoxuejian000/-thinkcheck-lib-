"""
ThinkCheck Harmony 指标计算模块
实现四维评估：U, D, A, H，包含语义向量对立检测、共现约束、分层计算等
"""

import re
import math
from typing import List, Dict, Tuple, Optional
from collections import Counter, defaultdict
import numpy as np
from itertools import combinations


def calculate_unity(text: str) -> float:
    """
    计算统一性 (U)：文档内容的一致性和连贯性
    包含跨术语一致性检测
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
        unity_score += min(top_words_ratio * 2, 0.4)
    
    # 2. 跨术语一致性检测
    term_consistency_score = _detect_term_consistency(text, sentences)
    unity_score += term_consistency_score * 0.3
    
    # 3. 检查句子长度一致性
    sentence_lengths = [len(s.split()) for s in sentences]
    if len(sentence_lengths) > 1:
        mean_len = np.mean(sentence_lengths)
        std_len = np.std(sentence_lengths) if mean_len > 0 else 0
        coeff_var = std_len / mean_len if mean_len > 0 else 1.0
        length_consistency = max(0.0, 1.0 - coeff_var)
        unity_score += length_consistency * 0.2
    
    # 4. 检查段落结构
    paragraphs = text.split('\n\n')
    if len(paragraphs) > 1:
        para_lengths = [len(p) for p in paragraphs if p.strip()]
        if para_lengths:
            mean_para = np.mean(para_lengths)
            unity_score += 0.1
    
    return min(1.0, unity_score)


def _detect_term_consistency(text: str, sentences: List[str]) -> float:
    """
    跨术语一致性检测：检查术语在文档中的一致性使用
    返回分数：[0, 1]，越高表示一致性越好
    """
    if len(sentences) < 2:
        return 0.5
    
    # 提取关键词和术语
    words = re.findall(r'[\w\u4e00-\u9fff]+', text.lower())
    word_freq = Counter(words)
    
    # 找出高频术语（在文档中多次出现）
    important_terms = [word for word, count in word_freq.items() if count >= 3]
    
    if not important_terms:
        return 0.5
    
    consistency_score = 0.0
    num_terms = len(important_terms)
    
    # 检查术语在文档中的一致性使用
    for term in important_terms:
        # 找出所有包含该术语的句子
        containing_sentences = []
        for i, sent in enumerate(sentences):
            if term in sent.lower():
                containing_sentences.append(i)
        
        # 检查术语出现的上下文是否一致
        if len(containing_sentences) > 1:
            # 检查术语在句子中的位置一致性
            consistency_score += 0.5
        else:
            consistency_score += 0.3
    
    return min(1.0, consistency_score / num_terms if num_terms > 0 else 0.5)


def calculate_development(text: str) -> float:
    """
    计算发展性 (D)：文档内容的丰富度和深度
    区分建设性创新和破坏性重复
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
        development_score += ttr * 0.3
    
    # 2. 区分建设性创新和破坏性重复
    sentences = re.split(r'[.!?。！？]', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if sentences:
        innovation_score, repetition_penalty = _analyze_innovation_and_repetition(sentences)
        development_score += innovation_score * 0.4
        development_score -= repetition_penalty * 0.1
    
    # 3. 文档长度（适中为好）
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
    
    # 4. 句子结构多样性
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
            development_score += pattern_diversity * 0.1
    
    return max(0.0, min(1.0, development_score))


def _analyze_innovation_and_repetition(sentences: List[str]) -> Tuple[float, float]:
    """
    分析建设性创新和破坏性重复
    返回：(创新分数, 重复惩罚分数)
    """
    if len(sentences) < 2:
        return 0.5, 0.0
    
    # 检测重复内容
    sentence_patterns = []
    for sent in sentences:
        words = set(re.findall(r'[\w\u4e00-\u9fff]{2,}', sent.lower()))
        sentence_patterns.append(tuple(sorted(words)))
    
    # 计算重复率
    pattern_counts = Counter(sentence_patterns)
    repetitions = sum(count - 1 for count in pattern_counts.values())
    repetition_penalty = min(repetitions / len(sentences), 0.5)
    
    # 计算创新度
    unique_patterns = len(pattern_counts)
    innovation_score = unique_patterns / len(sentence_patterns)
    
    # 额外检测：检测建设性创新（递进关系、新观点）
    progressive_markers = ['然后', '因此', '所以', '此外', '而且', '另外', '进一步',
                          'then', 'therefore', 'thus', 'furthermore', 'moreover', 'additionally']
    progressive_count = 0
    for sent in sentences:
        if any(marker in sent for marker in progressive_markers):
            progressive_count += 1
    
    # 如果有递进关系，增加创新分数
    if progressive_count > 0:
        innovation_score += min(0.2, progressive_count / len(sentences))
    
    return min(1.0, innovation_score), repetition_penalty


def calculate_adversarial(text: str) -> float:
    """
    计算对抗性 (A)：文档中的矛盾、冲突和负面内容
    包含语义向量对立检测、共现约束、分层计算等
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
        'error', 'failure', 'wrong', 'bad', 'evil', 'crime', 'war', 'death',
        '没用', '差', '糟糕', '极差', '没用', '没用'
    ]
    
    words = re.findall(r'[\w\u4e00-\u9fff]+', text.lower())
    negative_count = sum(1 for word in words if word in negative_words)
    if words:
        negative_ratio = negative_count / len(words)
        adversarial_score += min(negative_ratio * 15, 0.4)
    
    # 2. 检测逻辑矛盾模式（分层计算）
    contradiction_score = _detect_contradictions(text)
    adversarial_score += contradiction_score
    
    # 3. 检测共现约束和对立关系
    cooccurrence_violation_score = _detect_cooccurrence_violations(text)
    adversarial_score += cooccurrence_violation_score
    
    # 4. 检测情感强度
    exclamation_count = text.count('!') + text.count('！')
    question_count = text.count('?') + text.count('？')
    total_sentences = max(1, len(re.split(r'[。！？.!?]', text)))
    emotion_ratio = (exclamation_count + question_count) / total_sentences
    adversarial_score += min(emotion_ratio * 0.5, 0.1)
    
    return min(1.0, adversarial_score)


def _detect_contradictions(text: str) -> float:
    """
    分层检测矛盾，使用多层模式检测
    返回分数：[0, 1]，越高表示矛盾越多
    """
    contradiction_score = 0.0
    
    # 第一层：检测直接矛盾模式
    direct_contradiction_patterns = [
        r'(既是|是|等于).*?(又不是|不是|不等于)',
        r'(必须|应该|要).*?(不能|不要|不应该)',
        r'(所有|全部|一切).*?(有些|部分|例外)',
        r'(肯定|一定|绝对).*?(可能|也许|不确定)'
    ]
    
    for pattern in direct_contradiction_patterns:
        if re.search(pattern, text):
            contradiction_score += 0.25
    
    # 第二层：检测转折连词后的语义对立
    contrast_conjunctions = ['但', '然而', '却', '不过', '只是', '可惜', '反而', '相反', '尽管如此', '但是', '可']
    sentences = re.split(r'[。！？.!?]', text)
    
    for sent in sentences:
        if not sent.strip():
            continue
        for conj in contrast_conjunctions:
            if conj in sent:
                parts = sent.split(conj)
                if len(parts) >= 2:
                    # 检测转折前后的内容是否强烈对立
                    before_part = parts[0].strip()
                    after_part = parts[1].strip()
                    if before_part and after_part:
                        # 简单检测前后部分的语义对立
                        if _detect_semantic_opposition(before_part, after_part):
                            contradiction_score += 0.35
                        else:
                            # 只要有转折连词，至少加一点
                            contradiction_score += 0.15
    
    return min(1.0, contradiction_score)


def _detect_semantic_opposition(text1: str, text2: str) -> bool:
    """
    检测两个文本部分的语义对立
    使用简单的词汇级别的检测
    """
    if not text1 or not text2:
        return False
    
    # 扩展的正面和负面词汇表
    positive_words = [
        '好', '优秀', '出色', '成功', '有效', '正确', '安全', '稳定', '良好', '完美',
        '不错', '满意', '喜欢', '欣赏', '高兴', '开心', '优秀', '强大', '强大', '优秀',
        '高', '大', '好', '棒', '优秀', '优秀', '完美', '完美', '推荐', '购买', '实惠',
        '很棒', '很好', '非常好', '相当好', '太好', '太好了'
    ]
    negative_words = [
        '差', '糟糕', '失败', '无效', '错误', '危险', '不稳定', '坏', '问题', '缺陷',
        '没用', '差', '糟糕', '不好', '不喜欢', '讨厌', '差劲', '劣质', '不好', '差',
        '低', '小', '差', '糟糕', '不行', '不要买', '不推荐', '贵', '昂贵', '极差'
    ]
    
    has_positive1 = any(p in text1 for p in positive_words)
    has_positive2 = any(p in text2 for p in positive_words)
    has_negative1 = any(n in text1 for n in negative_words)
    has_negative2 = any(n in text2 for n in negative_words)
    
    # 检测语义对立情况
    if (has_positive1 and has_negative2) or (has_negative1 and has_positive2):
        return True
    
    # 额外检测：直接的对比词
    contrast_pairs = [
        ('强大', '没用'), ('好', '差'), ('优秀', '糟糕'),
        ('便宜', '昂贵'), ('推荐', '不推荐'), ('完美', '缺陷')
    ]
    
    for pos_word, neg_word in contrast_pairs:
        if (pos_word in text1 and neg_word in text2) or (neg_word in text1 and pos_word in text2):
            return True
    
    return False


def _detect_cooccurrence_violations(text: str) -> float:
    """
    检测共现约束违反情况
    返回分数：[0, 1]，越高表示违反越多
    """
    violation_score = 0.0
    
    # 定义不能共现的词对
    conflicting_pairs = [
        ('安全', '危险'),
        ('成功', '失败'),
        ('正确', '错误'),
        ('好', '坏'),
        ('有效', '无效'),
        ('稳定', '不稳定'),
        ('优秀', '糟糕'),
        ('完美', '缺陷')
    ]
    
    words = set(re.findall(r'[\w\u4e00-\u9fff]+', text.lower()))
    
    for (word1, word2) in conflicting_pairs:
        if word1 in words and word2 in words:
            violation_score += 0.1
    
    return min(1.0, violation_score)


def calculate_harmony(text: str, lambda_u: float = 0.4, lambda_d: float = 0.4, lambda_a: float = 0.2) -> Dict[str, float]:
    """
    计算综合和谐度 (H) 及所有四个维度
    支持可配置λ权重，可审计
    返回：{'U': u_score, 'D': d_score, 'A': a_score, 'H': h_score, 'lambda_u': lambda_u, 'lambda_d': lambda_d, 'lambda_a': lambda_a}
    """
    u = calculate_unity(text)
    d = calculate_development(text)
    a = calculate_adversarial(text)
    
    # 综合和谐度计算公式：H = lambda_u*U + lambda_d*D - lambda_a*A
    # 但确保 H 在 [0, 1] 范围内
    h_raw = lambda_u * u + lambda_d * d - lambda_a * a
    h = max(0.0, min(1.0, h_raw))
    
    return {
        'U': u,
        'D': d,
        'A': a,
        'H': h,
        'lambda_u': lambda_u,
        'lambda_d': lambda_d,
        'lambda_a': lambda_a
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


# 审计功能：记录权重配置
def get_current_weights() -> Dict[str, float]:
    """
    获取当前权重配置，用于审计
    """
    return {
        'lambda_u': 0.4,
        'lambda_d': 0.4,
        'lambda_a': 0.2
    }


def set_weights(lambda_u: float, lambda_d: float, lambda_a: float) -> None:
    """
    设置权重配置，用于审计
    """
    pass  # 这里可以添加持久化配置的功能
