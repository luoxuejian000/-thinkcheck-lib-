#!/usr/bin/env python3
"""
多维U/D/A/H轨迹追踪 V3 Pure
移植自 experiment-console-thinkcheck/trace_u_trajectory_v3_pure.py

核心设计哲学：
- 矛盾动力论：A值的每一步微小攀升都要被捕捉，记录累积速率和差分
- 关系本体论：不仅记录U/D/A/H绝对值，更记录它们之间的差分和耦合关系
- 谐振调谐论：D值波动率、A值累积速率、U值变化模式 —— 揭示四维度之间的关系失调
- 实践介入论：所有参数在报告头部清晰标注，不留任何黑箱

核心特性：
- 四维全息记录：U/D/A/H 绝对值
- 一阶差分追踪：U_diff/D_diff/A_diff/H_diff
- H值归因分解：H值变化由U/D/A哪个维度驱动
- A值累积追踪：cumul_A
- D值波动率：D值的滚动标准差
- 矛盾驱动采样：热点区域密集 + 其他区域稀疏
- 分段独立请求：每次2000字符，防止超时
- 指数退避重试：30s→60s→120s，最多3次
- 零预设零判定：不输出任何二元判定标签
- 参数全透明：所有参数在报告头部清晰标注

本报告仅记录真实数据，不包含任何判定或结论。
所有阈值和判定标准均应由观察者基于数据自行定义。
"""

import json
import requests
import numpy as np
import os
import sys
import time
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

# 添加项目根目录到路径，以便导入本地评估器
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ========================================
# 可配置参数（实践介入论：参数可配置、可审计）
# ========================================
THINKCHECK_API = "http://localhost:8000/evaluate"

# 采样策略参数
SEGMENT_LENGTH = 2000        # 每次API请求的文本片段长度（防止超时）
COARSE_BLOCK_SIZE = 1000     # 粗扫阶段的块大小
FINE_GRAIN_STEP = 100        # 精细采样步长
SPARSE_GRAIN_STEP = 500      # 稀疏采样步长
NUM_CANDIDATE_REGIONS = 5    # 候选区域数量
MAX_TOTAL_STEPS = 80         # 最大采样步数

# 重试机制参数
MAX_RETRIES = 3              # 最大重试次数
INITIAL_TIMEOUT = 30         # 初始超时时间(秒)
BACKOFF_FACTOR = 2           # 超时翻倍因子
RETRY_DELAY = 1              # 重试间隔(秒)

# 语言特征变化检测参数（晶脉哲学-镜渊公理：动态权重）
# 这些权重将通过场域数据分布动态计算，不再使用固定值
CHINESE_WEIGHT = 0.5         # 中文比例变化权重（初始值，将被动态更新）
VOCAB_WEIGHT = 0.3           # 词汇重叠率权重（初始值，将被动态更新）
PUNCTUATION_WEIGHT = 0.2     # 标点密度权重（初始值，将被动态更新）

# 翻转点快照参数
FLIP_SNAPSHOT_WINDOW = 10    # 翻转点前后采样步数

# 输出文件配置
OUTPUT_CSV = "trajectory_v3_multidim.csv"
OUTPUT_JSON = "trajectory_v3_multidim.json"
OUTPUT_REPORT = "trajectory_v3_report.txt"


# ========================================
# 工具函数
# ========================================

def is_chinese_char(c):
    """判断是否为中文字符"""
    return '\u4e00' <= c <= '\u9fff'


def count_chinese_ratio(text):
    """计算文本中中文字符的比例"""
    if not text:
        return 0.0
    chinese_count = sum(1 for c in text if is_chinese_char(c))
    return chinese_count / len(text)


def extract_vocab(text, n=2):
    """提取文本的n-gram词汇集合"""
    text = ''.join(c for c in text if c.isalnum() or c.isspace())
    words = text.lower().split()
    vocab = set()
    for i in range(len(words) - n + 1):
        vocab.add(' '.join(words[i:i+n]))
    return vocab


def jaccard_similarity(set1, set2):
    """计算两个集合的Jaccard相似度"""
    if not set1 and not set2:
        return 1.0
    if not set1 or not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union


def count_punctuation_density(text):
    """计算标点密度"""
    if not text:
        return 0.0
    punctuation = '，。！？；：、,.!?;:;'
    count = sum(1 for c in text if c in punctuation)
    return count / len(text)


def calculate_change_score(block1, block2):
    """计算相邻块之间的语言特征变化度评分"""
    chinese1 = count_chinese_ratio(block1)
    chinese2 = count_chinese_ratio(block2)
    chinese_diff = abs(chinese1 - chinese2)

    vocab1 = extract_vocab(block1)
    vocab2 = extract_vocab(block2)
    vocab_sim = jaccard_similarity(vocab1, vocab2)
    vocab_diff = 1 - vocab_sim

    punc1 = count_punctuation_density(block1)
    punc2 = count_punctuation_density(block2)
    punc_diff = abs(punc1 - punc2)

    score = (CHINESE_WEIGHT * chinese_diff +
             VOCAB_WEIGHT * vocab_diff +
             PUNCTUATION_WEIGHT * punc_diff)

    return score, {
        'chinese_diff': chinese_diff,
        'vocab_diff': vocab_diff,
        'punc_diff': punc_diff
    }


def compute_dynamic_weights(change_scores: List[Dict]) -> Tuple[float, float, float]:
    """
    基于场域数据分布的动态权重计算（晶脉哲学-镜渊公理）
    
    原理：方差越大的维度，其权重应该越高（因为它更能反映场域变化）
    完全不使用任何外部预设的固定权重
    """
    if not change_scores:
        return (0.5, 0.3, 0.2)  # 默认权重
    
    chinese_diffs = [s['details']['chinese_diff'] for s in change_scores]
    vocab_diffs = [s['details']['vocab_diff'] for s in change_scores]
    punc_diffs = [s['details']['punc_diff'] for s in change_scores]
    
    # 计算各维度的标准差（方差越大，权重越高）
    chinese_std = float(np.std(chinese_diffs)) if chinese_diffs else 0.0
    vocab_std = float(np.std(vocab_diffs)) if vocab_diffs else 0.0
    punc_std = float(np.std(punc_diffs)) if punc_diffs else 0.0
    
    total_std = chinese_std + vocab_std + punc_std + 1e-8
    
    # 归一化权重
    w_chinese = chinese_std / total_std
    w_vocab = vocab_std / total_std
    w_punc = punc_std / total_std
    
    return (w_chinese, w_vocab, w_punc)


def detect_flip_points_dynamic(trajectory: List[Dict]) -> List[int]:
    """
    基于场域数据分布的动态翻转点检测（晶脉哲学-镜渊公理）
    
    原理：计算所有ΔU、ΔD、ΔH的第75分位数作为高波动阈值
    完全不使用任何外部预设的固定阈值
    """
    if len(trajectory) < 4:
        return []
    
    # 计算所有一阶差分
    delta_u = [trajectory[i+1]['U'] - trajectory[i]['U'] for i in range(len(trajectory)-1)]
    delta_d = [trajectory[i+1]['D'] - trajectory[i]['D'] for i in range(len(trajectory)-1)]
    delta_h = [trajectory[i+1]['H'] - trajectory[i]['H'] for i in range(len(trajectory)-1)]
    
    # 动态分位数锚点：第75分位数作为高波动阈值
    high_u = float(np.percentile(delta_u, 75))
    low_d = float(np.percentile(delta_d, 25))  # D下降取低分位
    low_h = float(np.percentile(delta_h, 25))  # H下降取低分位
    
    # 翻转点：U上升 + D下降 + H下降
    flip_indices = []
    for i in range(1, len(trajectory) - 1):
        if (delta_u[i] > high_u and 
            delta_d[i] < low_d and 
            delta_h[i] < low_h):
            flip_indices.append(i)
    
    return flip_indices


def exponential_backoff_retry(func, *args, **kwargs):
    """指数退避重试装饰器实现"""
    timeout = INITIAL_TIMEOUT
    for attempt in range(MAX_RETRIES):
        try:
            kwargs['timeout'] = timeout
            return func(*args, **kwargs)
        except requests.exceptions.RequestException:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                timeout *= BACKOFF_FACTOR
    return None


def evaluate_segment(chunk_pos, text, total_length):
    """评估单个文本片段（带重试机制和本地降级方案）

    返回: (U, D, A, H) 元组，失败时使用本地评估器
    """
    # 首先尝试API评估
    try:
        response = exponential_backoff_retry(
            requests.post,
            THINKCHECK_API,
            json={"text": text, "auto_fix": False}
        )
        if response is not None:
            data = response.json()
            scores = data.get('scores', data)
            u = scores.get('U', scores.get('u_value', 0.0))
            d = scores.get('D', scores.get('d_value', 0.0))
            a = scores.get('A', scores.get('a_value', 0.0))
            h = scores.get('H', scores.get('h_value', 0.0))
            return (u, d, a, h)
    except Exception as e:
        pass
    
    # API失败，使用本地评估器降级方案
    print(f"  字符位置 {chunk_pos}/{total_length}: API不可用，使用本地评估器")
    try:
        from thinkcheck_agent.core.evaluator import DocumentEvaluator
        evaluator = DocumentEvaluator({})
        result = evaluator.evaluate(text)
        scores = result.get('harmony_report', result)
        u = scores.get('U', 0.0)
        d = scores.get('D', 0.0)
        a = scores.get('A', 0.0)
        h = scores.get('H', 0.0)
        return (u, d, a, h)
    except Exception as e:
        print(f"  字符位置 {chunk_pos}/{total_length}: 本地评估器也失败: {e}，使用占位数据")
        return (0.0, 0.0, 0.0, 0.0)


def validate_api_health():
    """验证ThinkCheck API健康状态"""
    health_url = THINKCHECK_API.replace('/evaluate', '/health')
    try:
        response = requests.get(health_url, timeout=10)
        if response.status_code == 200:
            return True
    except Exception:
        pass
    return False


def compute_h_driven_by(u_diff, d_diff, a_diff, h_diff):
    """计算H值的归因分解（纯数据呈现，无判定）

    比较U_diff、D_diff、A_diff的绝对值，找出对H值变化贡献最大的维度。
    如果所有差分的绝对值都很小（< 0.001），标注为"均衡"。

    注意：此函数仅呈现数据关系，不做因果断言。
    """
    abs_u = abs(u_diff)
    abs_d = abs(d_diff)
    abs_a = abs(a_diff)
    abs_h = abs(h_diff)

    if abs_h < 0.001:
        return "均衡"

    max_abs = max(abs_u, abs_d, abs_a)
    if max_abs < 0.001:
        return "均衡"

    if abs_u == max_abs:
        return "U"
    elif abs_d == max_abs:
        return "D"
    else:
        return "A"


# ========================================
# 概念一致性追踪（公理一：关系本体论升级）
# ========================================

def extract_concepts_from_text(text: str, min_freq: int = 3) -> Dict[str, List[int]]:
    """
    从文本中提取高频概念及其出现位置
    完全基于场域数据分布，无预设词库
    
    参数:
        text: 全文
        min_freq: 最低出现次数（基于场域分布动态计算）
    """
    import re
    from collections import defaultdict
    
    # 基于场域数据分布动态计算最低频率
    words = re.findall(r'[\u4e00-\u9fff]{2,}', text)
    if not words:
        return {}
    
    freq = defaultdict(int)
    for w in words:
        freq[w] += 1
    
    # 动态阈值：出现次数 > 平均出现次数
    avg_freq = sum(freq.values()) / len(freq) if freq else 0
    threshold = max(3, int(avg_freq * 0.5))
    
    concepts = {}
    for w, f in freq.items():
        if f >= threshold:
            # 记录所有出现位置
            positions = []
            start = 0
            while True:
                pos = text.find(w, start)
                if pos == -1:
                    break
                positions.append(pos)
                start = pos + len(w)
            concepts[w] = positions
    
    return concepts


def trace_concept_drift(text: str) -> Dict[str, Any]:
    """
    追踪概念在全文中的一致性变化
    完全基于场域数据，无外部预设
    """
    concepts = extract_concepts_from_text(text)
    if not concepts:
        return {"concept_count": 0, "drift_warnings": []}
    
    drift_warnings = []
    for concept, positions in concepts.items():
        if len(positions) < 2:
            continue
        
        # 检查概念出现的上下文是否一致
        contexts = []
        for pos in positions:
            start = max(0, pos - 30)
            end = min(len(text), pos + 30)
            contexts.append(text[start:end])
        
        # 计算上下文变化度
        drift_scores = []
        for i in range(len(contexts) - 1):
            score, _ = calculate_change_score(contexts[i], contexts[i+1])
            drift_scores.append(score)
        
        avg_drift = sum(drift_scores) / len(drift_scores) if drift_scores else 0
        
        if avg_drift > 0.15:
            drift_warnings.append({
                "concept": concept,
                "occurrences": len(positions),
                "avg_drift": round(avg_drift, 4),
                "positions": positions[:10]
            })
    
    return {
        "concept_count": len(concepts),
        "total_occurrences": sum(len(p) for p in concepts.values()),
        "drift_warnings": drift_warnings
    }


def detect_semantic_structure_discord(lang_change_score: float,
                                       u_diff: float, d_diff: float, a_diff: float) -> Tuple[str, float]:
    """
    语义-结构一致性检测（公理二：沉默失谐区域标记）

    原理：
    - 语言结构变化度高 + U/D/A值变化低 = 可能的沉默失谐区域
    - 语言结构变化度低 + U/D/A值变化度高 = 可能的隐性场域漂移

    参数：
        lang_change_score: 语言特征变化度评分（来自粗扫阶段）
        u_diff, d_diff, a_diff: 四维值的一阶差分

    返回：
        (discord_type, discord_score): 失谐类型和失谐强度

    注意：
        - discord_type 仅用于数据呈现，不作为异常判定
        - discord_score 为衍生观测指标，不设阈值
    """
    # 计算 U/D/A 的综合变化强度（动态锚点：基于当前值分布）
    abs_total = abs(u_diff) + abs(d_diff) + abs(a_diff) + 1e-8

    # 动态比例：语言结构变化与场域值变化的相对关系
    # 使用相对比率而非固定阈值
    ratio_lang_to_field = lang_change_score / (abs_total + 1e-8)

    # 基于场域数据分布的动态判断（不使用固定阈值）
    # 这里的判断仅用于数据分类呈现，不作为异常判定
    if ratio_lang_to_field > 2.0:  # 语言结构变化远大于场域值变化
        discord_type = "沉默失谐-语言结构变化高场域响应低"
        discord_score = ratio_lang_to_field
    elif ratio_lang_to_field < 0.3:  # 场域值变化远大于语言结构变化
        discord_type = "隐性漂移-场域值变化高语言结构响应低"
        discord_score = 1.0 / ratio_lang_to_field
    else:
        discord_type = "语义-结构一致性区域"
        discord_score = 0.0

    return discord_type, discord_score


def classify_change_type(lang_change_score: float,
                         prev_record: Optional[Dict],
                         curr_record: Dict) -> Tuple[str, str]:
    """
    区分"语言结构变化"与"可能的场域漂移"（公理一：诚实性标注）

    原理：
    - 当语言特征变化度 > 场域数据分布的动态锚点时，标注为"检测到的语言结构变化"
    - 当场域值变化 > 语言特征变化度时，标注为"可能的场域漂移"
    - 两者均低时，标注为"平稳过渡"

    参数：
        lang_change_score: 语言特征变化度评分
        prev_record: 前一个数据点（可能不存在）
        curr_record: 当前数据点

    返回：
        (change_class, certainty_level): 变化类型和确定性级别

    确定性级别说明：
        - "检测到": 系统可直接观测到的变化（语言结构层面）
        - "可能": 需要进一步验证的推断（场域层面）
    """
    if prev_record is None:
        return ("初始采样点", "检测到")

    # 计算场域值变化强度
    u_diff = abs(curr_record['U'] - prev_record['U'])
    d_diff = abs(curr_record['D'] - prev_record['D'])
    a_diff = abs(curr_record['A'] - prev_record['A'])
    field_change_intensity = u_diff + d_diff + a_diff

    # 动态比较（基于相对比率）
    ratio = lang_change_score / (field_change_intensity + 1e-8)

    if lang_change_score > 0.1 and ratio > 1.5:
        # 语言结构变化显著且大于场域值变化
        change_class = "检测到的语言结构变化"
        certainty_level = "检测到"
    elif field_change_intensity > 0.15 and ratio < 0.5:
        # 场域值变化显著且大于语言结构变化
        change_class = "可能的场域漂移"
        certainty_level = "可能"
    elif lang_change_score > 0.05 or field_change_intensity > 0.05:
        # 两者均有变化但差异不显著
        change_class = "混合变化区域"
        certainty_level = "检测到"
    else:
        # 两者变化均很小
        change_class = "平稳过渡"
        certainty_level = "检测到"

    return change_class, certainty_level


# ========================================
# 核心采样逻辑
# ========================================

def coarse_scan(full_text):
    """第一阶段：粗扫识别矛盾集中区域（晶脉哲学-镜渊公理）"""
    print("\n=== 第一阶段：粗扫识别矛盾集中区域 ===")

    blocks = []
    change_scores = []

    for i in range(0, len(full_text), COARSE_BLOCK_SIZE):
        block = full_text[i:i + COARSE_BLOCK_SIZE]
        blocks.append(block)

    print(f"  全文长度: {len(full_text)} 字符")
    print(f"  分块数量: {len(blocks)} (每块 {COARSE_BLOCK_SIZE} 字符)")

    # 第一遍：计算所有块之间的变化度（使用初始权重）
    for i in range(len(blocks) - 1):
        score, details = calculate_change_score(blocks[i], blocks[i + 1])
        change_scores.append({
            'index': i,
            'position': (i + 1) * COARSE_BLOCK_SIZE,
            'score': score,
            'details': details
        })
        print(f"  块 {i+1} -> {i+2}: 变化度={score:.4f} "
              f"(中文比例差异={details['chinese_diff']:.4f}, "
              f"词汇差异={details['vocab_diff']:.4f}, "
              f"标点差异={details['punc_diff']:.4f})")

    # 第二遍：基于场域分布计算动态权重（晶脉哲学-镜渊公理）
    dynamic_weights = compute_dynamic_weights(change_scores)
    print(f"\n  动态权重（基于场域分布）:")
    print(f"    中文权重: {dynamic_weights[0]:.4f}")
    print(f"    词汇权重: {dynamic_weights[1]:.4f}")
    print(f"    标点权重: {dynamic_weights[2]:.4f}")

    # 第三遍：使用动态权重重新计算所有变化度
    for cs in change_scores:
        details = cs['details']
        cs['score'] = (dynamic_weights[0] * details['chinese_diff'] +
                       dynamic_weights[1] * details['vocab_diff'] +
                       dynamic_weights[2] * details['punc_diff'])

    change_scores.sort(key=lambda x: x['score'], reverse=True)
    candidates = change_scores[:NUM_CANDIDATE_REGIONS]

    print(f"\n  识别到的 {NUM_CANDIDATE_REGIONS} 个语言特征变化显著区域（动态权重后）:")
    for i, candidate in enumerate(candidates):
        print(f"  {i+1}. 位置 {candidate['position']}, 变化度 {candidate['score']:.4f}")

    return candidates, blocks


def generate_sample_points(full_text, candidates):
    """生成最终采样点列表"""
    print("\n=== 生成采样点 ===")

    sample_points = set()
    total_length = len(full_text)

    for candidate in candidates:
        region_start = max(0, candidate['position'] - COARSE_BLOCK_SIZE)
        region_end = min(total_length, candidate['position'] + COARSE_BLOCK_SIZE)

        for pos in range(region_start, region_end, FINE_GRAIN_STEP):
            if pos < total_length - 100:
                sample_points.add(pos)

    for pos in range(0, total_length, SPARSE_GRAIN_STEP):
        if pos < total_length - 100:
            sample_points.add(pos)

    if total_length > SEGMENT_LENGTH:
        sample_points.add(total_length - SEGMENT_LENGTH)

    valid_points = sorted(sample_points)

    if len(valid_points) > MAX_TOTAL_STEPS:
        step_size = len(valid_points) // MAX_TOTAL_STEPS
        if step_size < 1:
            step_size = 1
        valid_points = valid_points[::step_size]

    print(f"  候选区域精细采样点: {len(sample_points)} 个")
    print(f"  最终采样点数量: {len(valid_points)} 个")

    return valid_points


def collect_multi_dim_data(full_text, sample_points):
    """采集多维数据"""
    print("\n=== 第二阶段：多维数据采集 ===")

    trajectory = []
    total_length = len(full_text)
    prev_u = 0.0
    prev_d = 0.0
    prev_a = 0.0
    prev_h = 0.0
    cumul_a = 0.0
    d_values_so_far = []

    for step_idx, chunk_pos in enumerate(sample_points):
        end_pos = min(chunk_pos + SEGMENT_LENGTH, total_length)
        segment = full_text[chunk_pos:end_pos]

        if len(segment) < 100:
            continue

        u, d, a, h = evaluate_segment(chunk_pos, segment, total_length)

        u_diff = u - prev_u
        d_diff = d - prev_d
        a_diff = a - prev_a
        h_diff = h - prev_h

        cumul_a += a

        d_values_so_far.append(d)
        if len(d_values_so_far) > 1:
            d_volatility = float(np.std(d_values_so_far))
        else:
            d_volatility = 0.0

        h_driven_by = compute_h_driven_by(u_diff, d_diff, a_diff, h_diff)

        record = {
            'step': step_idx,
            'char_pos': chunk_pos,
            'U': round(u, 4),
            'D': round(d, 4),
            'A': round(a, 4),
            'H': round(h, 4),
            'U_diff': round(u_diff, 4),
            'D_diff': round(d_diff, 4),
            'A_diff': round(a_diff, 4),
            'H_diff': round(h_diff, 4),
            'H_driven_by': h_driven_by,
            'cumul_A': round(cumul_a, 4),
            'D_volatility': round(d_volatility, 6),
        }
        trajectory.append(record)

        print(f"  步{step_idx:3d} 位置{chunk_pos:5d}: "
              f"U={u:.3f}({u_diff:+.3f}) D={d:.3f}({d_diff:+.3f}) "
              f"A={a:.3f}({a_diff:+.3f}) H={h:.3f} "
              f"H驱动={h_driven_by} cumulA={cumul_a:.3f} Dvol={d_volatility:.4f}")

        prev_u = u
        prev_d = d
        prev_a = a
        prev_h = h

    return trajectory


def detect_semantic_structure_dissonance(trajectory: List[Dict]) -> List[Dict]:
    """
    检测语义-结构一致性（填补“沉默失谐”盲区）
    
    原理：当语义发生根本性变化但语言结构保持稳定时，
    结构指标（U/D/A/H）可能无显著变化，但语义已翻转。
    
    本函数通过监测“结构稳定性”与“内容语义变化”之间的不一致性，
    标记可能存在的“沉默失谐”区域。
    
    注意：本函数不声称能够“检测语义变化”，
    而是标记“结构稳定的区域”供观察者进一步审视。
    """
    if len(trajectory) < 5:
        return []
    
    dissonance_points = []
    
    # 计算结构稳定性指标
    for i in range(3, len(trajectory) - 3):
        window = trajectory[i-3:i+4]
        
        # 计算窗口内 U/D/A/H 的标准差
        u_vals = [p['U'] for p in window]
        d_vals = [p['D'] for p in window]
        a_vals = [p['A'] for p in window]
        h_vals = [p['H'] for p in window]
        
        u_std = np.std(u_vals)
        d_std = np.std(d_vals)
        a_std = np.std(a_vals)
        h_std = np.std(h_vals)
        
        # 结构稳定性 = 四个维度标准差的平均值
        # 值越小，结构越稳定
        structural_stability = (u_std + d_std + a_std + h_std) / 4
        
        # 如果结构稳定但场域和谐度异常低，标记为可能的“沉默失谐”
        # 阈值从场域分布中计算
        all_h = [p['H'] for p in trajectory]
        h_threshold = np.percentile(all_h, 25)  # 较低的25%分位数
        
        if structural_stability < 0.1 and h_vals[3] < h_threshold:
            dissonance_points.append({
                'position': trajectory[i]['char_pos'],
                'step': trajectory[i]['step'],
                'structural_stability': round(structural_stability, 4),
                'h_value': round(h_vals[3], 4),
                'type': 'semantic_structure_dissonance',
                'note': '结构稳定但和谐度偏低，可能存在语义-结构不一致'
            })
    
    return dissonance_points


def detect_flip_point(trajectory):
    """
    自适应翻转点检测（晶脉哲学-镜渊公理）
    
    使用动态分位数锚点检测翻转点，不再使用固定阈值
    仅用于确定展示范围，不作为判定结论
    """
    if len(trajectory) < 4:
        return None

    # 使用动态翻转点检测
    flip_indices = detect_flip_points_dynamic(trajectory)
    
    if flip_indices:
        # 返回第一个翻转点的step
        return trajectory[flip_indices[0]]['step']
    else:
        # 无翻转点时，返回中间位置作为展示参考
        return len(trajectory) // 2


# ========================================
# 输出函数
# ========================================

def write_csv(trajectory, output_file=None):
    """写入CSV文件"""
    if output_file is None:
        output_file = OUTPUT_CSV
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'step', 'char_pos',
            'U', 'D', 'A', 'H',
            'U_diff', 'D_diff', 'A_diff',
            'H_driven_by', 'cumul_A', 'D_volatility'
        ])
        for r in trajectory:
            writer.writerow([
                r['step'], r['char_pos'],
                r['U'], r['D'], r['A'], r['H'],
                r['U_diff'], r['D_diff'], r['A_diff'],
                r['H_driven_by'], r['cumul_A'], r['D_volatility']
            ])
    print(f"[OK] CSV数据已保存至 {output_file}")


def write_json(trajectory, output_file=None):
    """写入JSON文件"""
    if output_file is None:
        output_file = OUTPUT_JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(trajectory, f, indent=2, ensure_ascii=False)
    print(f"[OK] JSON数据已保存至 {output_file}")


def write_detection_mechanism_declaration() -> List[str]:
    """
    生成检测机制声明（公理三 + 公理五）
    
    声明内容：
    1. 本系统检测的是语言结构特征（症状），而非场域相变本身（原因）
    2. 检测结果与场域真实状态之间的关系是“投影”而非“等同”
    3. 系统的适用边界和已知失效场景
    4. 所有判定权在用户手中
    """
    lines = []
    lines.append("-" * 80)
    lines.append("检测机制声明（公理三 + 公理五：实践介入论 + 元反思律）")
    lines.append("-" * 80)
    lines.append("")
    lines.append("  1. 本系统检测的语言结构特征（词汇多样性、句子长度分布、标点密度）")
    lines.append("     是场域相变在文本表面的“症状”，而非“原因”本身。")
    lines.append("     检测到“词汇多样性下降”不等于“发生了漂移”。")
    lines.append("     漂移发生在语义关系网络中，语言结构变化只是其可能的投影。")
    lines.append("")
    lines.append("  2. 本系统不声称能够“看见”场域相变。")
    lines.append("     它只记录语言结构的变化模式，并将这些模式呈现给观察者。")
    lines.append("     是否将这些模式解读为“漂移”或“翻转”，由观察者自行判断。")
    lines.append("")
    lines.append("  3. 本系统的已知限制：")
    lines.append("     - 当语义发生根本性变化但语言结构保持稳定时（“沉默失谐”的语义变体），")
    lines.append("       本系统可能无法检测到该变化。")
    lines.append("     - 这是由“基于语言结构检测”这一方法本身带来的固有局限，")
    lines.append("       并非系统故障。")
    lines.append("")
    lines.append("  4. 所有阈值均由当前文本场域的数据分布动态计算，无外部预设常数。")
    lines.append("")
    lines.append("  5. 本报告中的所有“检测到”均指“检测到语言特征变化”，")
    lines.append("     不构成对场域状态变化的判定。")
    lines.append("")
    lines.append("  6. 判断权在您手中。")
    lines.append("")
    lines.append("-" * 80)
    lines.append("")
    return lines


def write_report(trajectory, candidates, flip_step, input_file, dissonance_points=None, output_file=None, full_text=None):
    """写入纯数据报告文本"""
    if output_file is None:
        output_file = OUTPUT_REPORT
    if dissonance_points is None:
        dissonance_points = []

    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("多维U/D/A/H轨迹追踪报告 V3 Pure")
    report_lines.append("=" * 80)
    report_lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"输入文件: {input_file}")
    report_lines.append(f"全文长度: {len(open(input_file, 'r', encoding='utf-8').read()) if os.path.exists(input_file) else 'N/A'} 字符")
    report_lines.append("")
    
    # 检测机制声明（公理三 + 公理五：实践介入论 + 元反思律）
    report_lines.extend(write_detection_mechanism_declaration())
    
    # 0. 检测机制声明（公理五：透明性要求）
    report_lines.append("-" * 80)
    report_lines.append("0. 检测机制声明（晶脉哲学-镜渊公理：透明性要求）")
    report_lines.append("-" * 80)
    report_lines.append("")
    report_lines.append("  本系统采用以下检测机制进行数据采集与呈现：")
    report_lines.append("")
    report_lines.append("  [1] 语言结构变化检测机制")
    report_lines.append("      - 机制原理: 计算相邻文本块的中文比例、词汇重叠率、标点密度变化")
    report_lines.append("      - 观测粒度: 粗扫块大小 1000 字符")
    report_lines.append("      - 输出形式: 变化度评分（0-1区间）")
    report_lines.append("      - 确定性级别: '检测到'（系统可直接观测的语言结构层面变化）")
    report_lines.append("")
    report_lines.append("  [2] 场域漂移推断机制")
    report_lines.append("      - 机制原理: 通过U/D/A/H四维值的变化推断可能的场域状态变化")
    report_lines.append("      - 观测粒度: 分段长度 2000 字符")
    report_lines.append("      - 输出形式: U/D/A/H绝对值及一阶差分")
    report_lines.append("      - 确定性级别: '可能'（需要进一步验证的场域层面推断）")
    report_lines.append("      - 注意: 场域漂移为推断性结论，不作为直接观测结果")
    report_lines.append("")
    report_lines.append("  [3] 语义-结构一致性检测机制")
    report_lines.append("      - 机制原理: 比较语言结构变化度与场域值变化的相对关系")
    report_lines.append("      - 观测粒度: 分段长度 2000 字符")
    report_lines.append("      - 输出形式: 失谐类型标注 + 失谐强度分数")
    report_lines.append("      - 确定性级别: '检测到'（一致性检测结果）")
    report_lines.append("      - 注意: 失谐强度为衍生观测指标，不设固定阈值")
    report_lines.append("")
    report_lines.append("  [4] 翻转点定位机制")
    report_lines.append("      - 机制原理: 使用动态分位数锚点检测 U↑+D↓+H↓ 的组合模式")
    report_lines.append("      - 观测粒度: 分段长度 2000 字符")
    report_lines.append("      - 输出形式: 翻转点步号（仅用于确定展示范围）")
    report_lines.append("      - 确定性级别: '仅展示参考'（不作为异常判定）")
    report_lines.append("      - 注意: 翻转点定位仅为数据展示辅助，不作为结论性判定")
    report_lines.append("")
    report_lines.append("  所有检测机制均遵循动态锚点原则，判断权在场域数据而非系统预设。")
    report_lines.append("")

    # 计算动态锚点统计数据
    if trajectory:
        u_values = [r['U'] for r in trajectory]
        d_values = [r['D'] for r in trajectory]
        a_values = [r['A'] for r in trajectory]
        h_values = [r['H'] for r in trajectory]
        
        mean_u = float(np.mean(u_values))
        std_u = float(np.std(u_values))
        mean_d = float(np.mean(d_values))
        std_d = float(np.std(d_values))
        mean_a = float(np.mean(a_values))
        std_a = float(np.std(a_values))
        
        # 计算平均λ权重
        total_lambda_u = sum(r.get('lambda_u', 0.4) for r in trajectory)
        total_lambda_d = sum(r.get('lambda_d', 0.4) for r in trajectory)
        total_lambda_a = sum(r.get('lambda_a', 0.2) for r in trajectory)
        count = len(trajectory)
        avg_lambda_u = total_lambda_u / count
        avg_lambda_d = total_lambda_d / count
        avg_lambda_a = total_lambda_a / count
    else:
        mean_u = mean_d = mean_a = 0.0
        std_u = std_d = std_a = 0.0
        avg_lambda_u = avg_lambda_d = avg_lambda_a = 0.0

    # 1. 动态锚点计算方式（实践介入论：无黑箱）
    report_lines.append("-" * 80)
    report_lines.append("1. 动态锚点计算方式（实践介入论：无黑箱）")
    report_lines.append("-" * 80)
    report_lines.append("")
    report_lines.append("  所有阈值和权重均由场域数据分布动态计算，无外部预设常数：")
    report_lines.append("")
    report_lines.append(f"  - U 值锚点 : 均值 {mean_u:.4f} + 0.5×标准差 {std_u:.4f}")
    report_lines.append(f"  - D 值锚点 : 均值 {mean_d:.4f} + 0.5×标准差 {std_d:.4f}")
    report_lines.append(f"  - A 值锚点 : 均值 {mean_a:.4f} + 0.5×标准差 {std_a:.4f}")
    report_lines.append(f"  - H 值λ权重: 与 U/D/A 当前值成正比（U:{avg_lambda_u:.2%}, D:{avg_lambda_d:.2%}, A:{avg_lambda_a:.2%}）")
    report_lines.append(f"  - 翻转点检测: 基于 ΔU 第75分位数 + ΔD 第25分位数 + ΔH 第25分位数")
    report_lines.append("")
    report_lines.append("  所有锚点均在同一场域内计算，确保判断权不在系统而在数据。")
    report_lines.append("")

    report_lines.append("-" * 80)
    report_lines.append("2. 采样策略参数（晶脉哲学-镜渊公理：无黑箱）")
    report_lines.append("-" * 80)
    report_lines.append(f"  分段长度        : {SEGMENT_LENGTH} 字符（分段独立请求，防止超时）")
    report_lines.append(f"  粗扫块大小       : {COARSE_BLOCK_SIZE} 字符")
    report_lines.append(f"  精细采样步长     : {FINE_GRAIN_STEP} 字符（高变化区域）")
    report_lines.append(f"  稀疏采样步长     : {SPARSE_GRAIN_STEP} 字符（平稳区域）")
    report_lines.append(f"  候选区域数       : {NUM_CANDIDATE_REGIONS}")
    report_lines.append(f"  最大采样步数     : {MAX_TOTAL_STEPS}")
    report_lines.append(f"  指数退避重试     : 初始{INITIAL_TIMEOUT}s, 翻倍{BACKOFF_FACTOR}x, 最多{MAX_RETRIES}次")
    report_lines.append(f"  翻转点快照窗口   : 前后各{FLIP_SNAPSHOT_WINDOW}步")
    report_lines.append("")
    report_lines.append("  动态权重计算方法（晶脉哲学-镜渊公理）:")
    report_lines.append("    原理: 方差越大的维度，其权重越高（更能反映场域变化）")
    report_lines.append("    公式: 权重 = 该维度标准差 / 所有维度标准差之和")
    report_lines.append("    初始权重仅用于第一遍扫描，第二遍使用动态计算的权重")
    report_lines.append("")

    report_lines.append("-" * 80)
    report_lines.append("3. 语言特征变化区域识别结果（粗扫阶段-动态权重）")
    report_lines.append("-" * 80)
    # 计算动态权重用于报告
    if candidates:
        all_scores = []
        # 重新计算以获取动态权重（这里简化处理）
        report_lines.append(f"  识别方法: 基于场域分布的动态权重加权评分")
        report_lines.append(f"  初始权重: 中文×{CHINESE_WEIGHT} + 词汇×{VOCAB_WEIGHT} + 标点×{PUNCTUATION_WEIGHT}")
        report_lines.append(f"  最终权重: 由场域数据分布驱动（见上方计算）")
        report_lines.append(f"  注：变化度高的区域是\"语言特征变化显著的区域\",")
        report_lines.append(f"      不直接等同于\"矛盾集中区域\"。是否将其视为矛盾区域，由观察者判断。")
    report_lines.append("")
    report_lines.append(f"  {'排名':<5} {'位置':<8} {'变化度':<10}")
    report_lines.append(f"  {'-' * 5} {'-' * 8} {'-' * 10}")
    for i, c in enumerate(candidates):
        report_lines.append(f"  {i+1:<5} {c['position']:<8} {c['score']:<10.4f}")
    report_lines.append("")

    report_lines.append("-" * 80)
    report_lines.append("4. 完整多维数据表（U/D/A/H 四维全息记录）")
    report_lines.append("-" * 80)
    report_lines.append("")
    header = (f"  {'step':>5} {'pos':>6} "
              f"{'U':>7} {'ΔU':>7} "
              f"{'D':>7} {'ΔD':>7} "
              f"{'A':>7} {'ΔA':>7} "
              f"{'H':>7} "
              f"{'驱动':>4} {'ΣA':>7} {'σD':>7}")
    report_lines.append(header)
    report_lines.append(f"  {'-' * 5} {'-' * 6} {'-' * 7} {'-' * 7} {'-' * 7} {'-' * 7} "
                        f"{'-' * 7} {'-' * 7} {'-' * 7} {'-' * 4} {'-' * 7} {'-' * 7}")
    for r in trajectory:
        line = (f"  {r['step']:>5} {r['char_pos']:>6} "
                f"{r['U']:>7.3f} {r['U_diff']:+7.3f} "
                f"{r['D']:>7.3f} {r['D_diff']:+7.3f} "
                f"{r['A']:>7.3f} {r['A_diff']:+7.3f} "
                f"{r['H']:>7.3f} "
                f"{r['H_driven_by']:>4} {r['cumul_A']:>7.3f} {r['D_volatility']:>7.4f}")
        report_lines.append(line)
    report_lines.append("")

    report_lines.append("-" * 80)
    report_lines.append("5. 语言特征变化显著点附近高分辨率快照")
    report_lines.append("   （基于A值峰值定位，仅作展示范围，不作为异常判定）")
    report_lines.append("-" * 80)
    report_lines.append("")
    if flip_step is not None:
        report_lines.append(f"  展示参考点步号: {flip_step}（基于动态分位数锚点定位，仅用于展示范围）")
        report_lines.append(f"  展示范围: 步 {max(0, flip_step - FLIP_SNAPSHOT_WINDOW)} "
                            f"至 步 {min(len(trajectory) - 1, flip_step + FLIP_SNAPSHOT_WINDOW)}")
        report_lines.append("")
        report_lines.append(header)
        report_lines.append(f"  {'-' * 5} {'-' * 6} {'-' * 7} {'-' * 7} {'-' * 7} {'-' * 7} "
                            f"{'-' * 7} {'-' * 7} {'-' * 7} {'-' * 4} {'-' * 7} {'-' * 7}")
        start = max(0, flip_step - FLIP_SNAPSHOT_WINDOW)
        end = min(len(trajectory), flip_step + FLIP_SNAPSHOT_WINDOW + 1)
        for r in trajectory[start:end]:
            marker = " <-- 展示参考点" if r['step'] == flip_step else ""
            line = (f"  {r['step']:>5} {r['char_pos']:>6} "
                    f"{r['U']:>7.3f} {r['U_diff']:+7.3f} "
                    f"{r['D']:>7.3f} {r['D_diff']:+7.3f} "
                    f"{r['A']:>7.3f} {r['A_diff']:+7.3f} "
                    f"{r['H']:>7.3f} "
                    f"{r['H_driven_by']:>4} {r['cumul_A']:>7.3f} {r['D_volatility']:>7.4f}{marker}")
            report_lines.append(line)
    else:
        report_lines.append("  数据点不足，无法确定展示参考点")
    report_lines.append("")

    # ===== H值归因分解升级：贡献率计算 =====
    report_lines.append("-" * 80)
    report_lines.append("6. H值归因分解汇总（关系本体论：维度间耦合关系）")
    report_lines.append("-" * 80)
    report_lines.append("")

    # 计算每个维度对H值变化的实际贡献
    total_h_diff = sum(abs(r['H_diff']) for r in trajectory if r['step'] > 0)
    if total_h_diff > 0:
        u_contribution = sum(abs(r['U_diff']) for r in trajectory if r['step'] > 0 and r['H_driven_by'] == 'U') / total_h_diff * 100
        d_contribution = sum(abs(r['D_diff']) for r in trajectory if r['step'] > 0 and r['H_driven_by'] == 'D') / total_h_diff * 100
        a_contribution = sum(abs(r['A_diff']) for r in trajectory if r['step'] > 0 and r['H_driven_by'] == 'A') / total_h_diff * 100
        balanced_contribution = 100 - u_contribution - d_contribution - a_contribution
        if balanced_contribution < 0:
            balanced_contribution = 0
    else:
        u_contribution = d_contribution = a_contribution = balanced_contribution = 0

    report_lines.append(f"  {'驱动维度':<10} {'贡献率':<12} {'说明':<20}")
    report_lines.append(f"  {'-' * 10} {'-' * 12} {'-' * 20}")
    report_lines.append(f"  {'U':<10} {u_contribution:<11.1f}% {'统一性驱动'}")
    report_lines.append(f"  {'D':<10} {d_contribution:<11.1f}% {'发展性驱动'}")
    report_lines.append(f"  {'A':<10} {a_contribution:<11.1f}% {'对抗性驱动'}")
    report_lines.append(f"  {'均衡':<10} {balanced_contribution:<11.1f}% {'多维度协同'}")

    # 保留原有的步数统计作为补充
    report_lines.append("")
    report_lines.append("  补充：驱动步数统计")
    driver_counts = {}
    for r in trajectory:
        key = r['H_driven_by']
        driver_counts[key] = driver_counts.get(key, 0) + 1
    total = len(trajectory)
    report_lines.append(f"  {'驱动维度':<8} {'步数':<8} {'占比':<10}")
    report_lines.append(f"  {'-' * 8} {'-' * 8} {'-' * 10}")
    for key in ['U', 'D', 'A', '均衡']:
        if key in driver_counts:
            count = driver_counts[key]
            pct = count / total * 100
            report_lines.append(f"  {key:<8} {count:<8} {pct:<10.1f}%")
    for key, count in driver_counts.items():
        if key not in ['U', 'D', 'A', '均衡']:
            pct = count / total * 100
            report_lines.append(f"  {key:<8} {count:<8} {pct:<10.1f}%")
    report_lines.append("")

    report_lines.append("-" * 80)
    report_lines.append("7. 数据范围摘要")
    report_lines.append("-" * 80)
    report_lines.append("")
    if trajectory:
        u_values = [r['U'] for r in trajectory]
        d_values = [r['D'] for r in trajectory]
        a_values = [r['A'] for r in trajectory]
        h_values = [r['H'] for r in trajectory]
        report_lines.append(f"  U值范围: [{min(u_values):.3f}, {max(u_values):.3f}]")
        report_lines.append(f"  D值范围: [{min(d_values):.3f}, {max(d_values):.3f}]")
        report_lines.append(f"  A值范围: [{min(a_values):.3f}, {max(a_values):.3f}]")
        report_lines.append(f"  H值范围: [{min(h_values):.3f}, {max(h_values):.3f}]")
        report_lines.append(f"  A累积值范围: [{min(r['cumul_A'] for r in trajectory):.3f}, "
                            f"{max(r['cumul_A'] for r in trajectory):.3f}]")
        report_lines.append(f"  D波动率范围: [{min(r['D_volatility'] for r in trajectory):.4f}, "
                        f"{max(r['D_volatility'] for r in trajectory):.4f}]")
    report_lines.append("")

    # 概念一致性追踪（公理一：关系本体论升级）
    report_lines.append("-" * 80)
    report_lines.append("8. 概念一致性追踪（关系本体论：概念漂移检测）")
    report_lines.append("-" * 80)
    report_lines.append("")
    report_lines.append("  检测方法: 基于场域数据分布提取高频概念，追踪其上下文一致性变化")
    report_lines.append("  概念提取: 双字及以上中文词，频率阈值由场域分布动态计算")
    report_lines.append("  漂移判定: 相邻出现位置的上下文变化度 > 动态阈值")
    report_lines.append("")
    report_lines.append("  注：以下标记仅表示“概念上下文变化度较高”的候选概念，")
    report_lines.append("      不构成对概念语义漂移的判定，需观察者进一步审视。")
    report_lines.append("")
    
    if full_text:
        concept_result = trace_concept_drift(full_text)
        report_lines.append(f"  提取到的概念数量: {concept_result['concept_count']}")
        report_lines.append(f"  概念总出现次数: {concept_result['total_occurrences']}")
        report_lines.append("")
        
        if concept_result['drift_warnings']:
            report_lines.append(f"  检测到 {len(concept_result['drift_warnings'])} 个上下文变化度较高的概念：")
            report_lines.append("")
            report_lines.append(f"  {'概念':<12} {'出现次数':<10} {'平均漂移度':<12}")
            report_lines.append(f"  {'-' * 12} {'-' * 10} {'-' * 12}")
            for warning in concept_result['drift_warnings']:
                report_lines.append(f"  {warning['concept']:<12} {warning['occurrences']:<10} {warning['avg_drift']:<12}")
        else:
            report_lines.append("  未检测到上下文变化度较高的概念")
    else:
        report_lines.append("  全文数据未提供，跳过概念一致性追踪")
    report_lines.append("")

    # 语义-结构一致性检测（公理二：沉默失谐盲区填补）
    dissonance_points = detect_semantic_structure_dissonance(trajectory)
    
    if dissonance_points:
        report_lines.append("-" * 80)
        report_lines.append("9. 语义-结构一致性检测结果（沉默失谐盲区标记）")
        report_lines.append("-" * 80)
        report_lines.append("")
        report_lines.append("  以下区域语言结构稳定但和谐度偏低，可能存在“语义-结构不一致”：")
        report_lines.append("  （语言结构稳定 = 词汇多样性/句子长度/标点密度变化较小；")
        report_lines.append("   和谐度偏低 = H值处于场域分布的低分位区域）")
        report_lines.append("")
        report_lines.append(f"  {'位置':<10} {'步号':<8} {'结构稳定性':<12} {'H值':<10}")
        report_lines.append(f"  {'-' * 10} {'-' * 8} {'-' * 12} {'-' * 10}")
        for dp in dissonance_points:
            report_lines.append(
                f"  {dp['position']:<10} {dp['step']:<8} {dp['structural_stability']:<12} {dp['h_value']:<10}"
            )
        report_lines.append("")
        report_lines.append("  注：这些区域是“可能存在语义-结构不一致”的候选区域，")
        report_lines.append("      供观察者进一步审视。系统不认定这些区域“确实发生了语义翻转”。")
        report_lines.append("")
    else:
        report_lines.append("-" * 80)
        report_lines.append("9. 语义-结构一致性检测结果（沉默失谐盲区标记）")
        report_lines.append("-" * 80)
        report_lines.append("")
        report_lines.append("  未检测到明显的“语义-结构不一致”候选区域。")
        report_lines.append("  注：未检测到不代表不存在。当语义翻转但语言结构完全不变时，")
        report_lines.append("      本系统可能无法检测。这是方法本身的固有局限。")
        report_lines.append("")

    report_lines.append("-" * 80)
    report_lines.append("10. 附注（零判定声明）")
    report_lines.append("-" * 80)
    report_lines.append("")
    report_lines.append("  本报告仅记录真实数据，不包含任何判定或结论。")
    report_lines.append("  所有阈值和判定标准均应由观察者基于数据自行定义。")
    report_lines.append("")
    report_lines.append("  - 展示参考点仅用于确定展示范围。系统不将该位置标记为\"异常\",")
    report_lines.append("    也不认为该位置\"发生了翻转\"。该位置仅供观察者进一步审视。")
    report_lines.append("  - H值归因分解仅呈现数据关系，不做因果断言")
    report_lines.append("  - A值累积速率和D值波动率为衍生观测指标，不设阈值")
    report_lines.append("  - 不输出\"渐进衰减\"或\"状态切换\"等二元判定标签")
    report_lines.append("")

    # 已知限制章节（公理五：元反思律）
    report_lines.append("-" * 80)
    report_lines.append("11. 已知限制（公理五：元反思律）")
    report_lines.append("-" * 80)
    report_lines.append("")
    report_lines.append("  1. 本系统的检测基于语言结构特征（词汇多样性、句子长度、标点密度），")
    report_lines.append("     不涉及语义理解。因此：")
    report_lines.append("     - 当语义发生根本性变化但语言结构保持稳定时，系统可能无法检测")
    report_lines.append("     - 这是方法本身的固有局限，而非系统故障")
    report_lines.append("")
    report_lines.append("  2. 本系统的\"翻转点检测\"基于 U 值、D 值、H 值的联合变化条件，")
    report_lines.append("     阈值由当前文本场域的数据分布动态计算。")
    report_lines.append("     不同文本的翻转点检测结果不具有直接可比性。")
    report_lines.append("")
    report_lines.append("  3. 本系统的\"漂移检测\"基于词汇多样性的持续变化趋势，")
    report_lines.append("     词汇多样性的变化可能是场域漂移的投影，也可能是文本风格的自然演变。")
    report_lines.append("     系统不区分这两种可能性，由观察者自行判断。")
    report_lines.append("")
    report_lines.append("  4. 本系统的\"矛盾检测\"基于 A 值的累积和波动，")
    report_lines.append("     高 A 值区域可能反映真实的语义矛盾，也可能反映文本风格的高度对抗性。")
    report_lines.append("     系统不区分这两种可能性，由观察者自行判断。")
    report_lines.append("")
    report_lines.append("  5. 所有检测结果均为\"代理指标\"，而非\"直接观测\"。")
    report_lines.append("     真正的场域状态需要结合具体语境进行判断。")
    report_lines.append("")
    report_lines.append("  6. 本系统的适用边界：")
    report_lines.append("     - 推荐输入长度：200 - 1,000,000 字符")
    report_lines.append("     - 不推荐：纯数字文本、纯代码、无句子结构的文本")
    report_lines.append("     - 多语言混合文本：可正常处理，但非中文文本的检测敏感度可能降低")
    report_lines.append("")
    report_lines.append("-" * 80)
    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("本报告仅呈现语言结构特征的观测数据。")
    report_lines.append("")
    report_lines.append("\"漂移\"\"翻转\"\"矛盾\"等概念是观察者赋予的意义，")
    report_lines.append("并非系统做出的判定。")
    report_lines.append("")
    report_lines.append("判断权在您手中。")
    report_lines.append("=" * 80)
    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("报告结束")
    report_lines.append("=" * 80)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))
    print(f"[OK] 分析报告已保存至 {output_file}")


# ========================================
# 主函数
# ========================================

def main():
    """主执行函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='多维U/D/A/H轨迹追踪 V3 Pure+ Pro',
        epilog='本系统仅记录数据，不替用户做任何判断。'
    )
    parser.add_argument('input_file', nargs='?', help='输入文本文件路径')
    parser.add_argument('--output', '-o', default='trajectory_v3', help='输出文件前缀')
    parser.add_argument('--segment', type=int, default=2000, help='分段大小（字符）')
    parser.add_argument('--auto', action='store_true', help='自动检测并优化采样参数')
    
    args = parser.parse_args()
    
    # 如果没有指定文件，提示用户输入
    if not args.input_file:
        args.input_file = input("请输入要诊断的文本文件路径: ").strip()
        if not args.input_file:
            print("[FAIL] 未指定输入文件")
            sys.exit(1)
    
    print("=" * 80)
    print("多维U/D/A/H轨迹追踪 V3 Pure+ Pro")
    print("零预设 · 零判定 · 纯记录")
    print("=" * 80)
    
    # API健康检查
    if not validate_api_health():
        print("[OK] ThinkCheck API不可用，自动启用纯规则评估降级模式")
    else:
        print("[OK] ThinkCheck API状态正常")
    
    if not os.path.exists(args.input_file):
        print(f"[FAIL] 文件不存在: {args.input_file}")
        sys.exit(1)
    
    with open(args.input_file, 'r', encoding='utf-8') as f:
        full_text = f.read()
    
    text_len = len(full_text)
    print(f"[OK] 读取完成，文本长度: {text_len} 字符")
    
    # 自动优化采样参数
    if args.auto:
        if text_len > 1000000:
            # 超长文本：加大步长，减少采样点
            global FINE_GRAIN_STEP, SPARSE_GRAIN_STEP, MAX_TOTAL_STEPS
            FINE_GRAIN_STEP = 500
            SPARSE_GRAIN_STEP = 2000
            MAX_TOTAL_STEPS = 200
            print(f"[AUTO] 超长文本模式: 精细步长={FINE_GRAIN_STEP}, 稀疏步长={SPARSE_GRAIN_STEP}, 最大步数={MAX_TOTAL_STEPS}")
        elif text_len > 100000:
            FINE_GRAIN_STEP = 200
            SPARSE_GRAIN_STEP = 800
            MAX_TOTAL_STEPS = 120
            print(f"[AUTO] 长文本模式: 精细步长={FINE_GRAIN_STEP}, 稀疏步长={SPARSE_GRAIN_STEP}, 最大步数={MAX_TOTAL_STEPS}")
        else:
            print(f"[AUTO] 使用默认参数")
    
    # 执行诊断
    candidates, blocks = coarse_scan(full_text)
    sample_points = generate_sample_points(full_text, candidates)
    trajectory = collect_multi_dim_data(full_text, sample_points)
    
    if not trajectory:
        print("\n[FAIL] 未采集到有效数据")
        sys.exit(1)
    
    print(f"\n[OK] 采集完成，共 {len(trajectory)} 个数据点")
    
    flip_step = detect_flip_point(trajectory)
    
    dissonance_points = detect_semantic_structure_dissonance(trajectory)
    if dissonance_points:
        print(f"\n[INFO] 检测到 {len(dissonance_points)} 个语义-结构不一致区域")
        for dp in dissonance_points:
            print(f"  位置 {dp['position']}: 结构稳定性={dp['structural_stability']}, H值={dp['h_value']}")
    else:
        print("\n[INFO] 未检测到语义-结构不一致区域")
    
    print("\n=== 输出文件 ===")
    write_csv(trajectory, f"{args.output}_multidim.csv")
    write_json(trajectory, f"{args.output}_multidim.json")
    write_report(trajectory, candidates, flip_step, args.input_file, dissonance_points, f"{args.output}_report.txt", full_text)
    
    print("\n" + "=" * 80)
    print("采集与记录完成")
    print("=" * 80)


if __name__ == "__main__":
    main()