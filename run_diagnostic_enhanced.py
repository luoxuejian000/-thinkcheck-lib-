"""
万象渊鉴·场域诊断测试集 - 增强版评估脚本
使用 DocumentEvaluator 进行更完整的诊断
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'thinkcheck-harmony'))

from thinkcheck_harmony.evaluator import HarmonyEvaluator
from thinkcheck_harmony.concept_graph import ConceptGraph
from thinkcheck_harmony.core import compute_U, compute_D, compute_A, compute_harmony
from thinkcheck_harmony.contradiction_detector import ContradictionDetector
from datetime import datetime
import re
import numpy as np

# 读取测试集文件
with open("万象渊鉴·场域诊断测试集.txt", "r", encoding="utf-8") as f:
    content = f.read()

# 分割为6个场景
scenarios = []
sections = content.split("=" * 80)
for i, section in enumerate(sections):
    section = section.strip()
    if section:
        if i == 0:
            continue
        lines = section.split("\n")
        title = lines[0].strip() if lines else ""
        text = "\n".join(lines[1:]).strip()
        if title and text:
            scenarios.append({"title": title, "text": text})

# 增强的矛盾检测
def detect_contradictions(text: str) -> list:
    """检测文本中的矛盾"""
    contradictions = []
    
    # 检测数字矛盾（如付款期限30日 vs 45天）
    date_patterns = re.findall(r'(\d+)\s*(日|天|个月|周)', text)
    if len(date_patterns) >= 2:
        dates = [(int(p[0]), p[1]) for p in date_patterns]
        for i, d1 in enumerate(dates):
            for j, d2 in enumerate(dates):
                if i < j and d1[1] == d2[1] and abs(d1[0] - d2[0]) > 5:
                    contradictions.append({
                        "type": "数值矛盾",
                        "weight": 0.8,
                        "details": f"检测到同类时间表述不一致：{d1[0]}{d1[1]} vs {d2[0]}{d2[1]}"
                    })
    
    # 检测对立陈述
    opposition_pairs = [
        ("唯一", "选择"),
        ("被迫", "主动"),
        ("不会", "可能"),
        ("支持", "反对"),
        ("符合", "不符合"),
    ]
    for pair in opposition_pairs:
        if pair[0] in text and pair[1] in text:
            contradictions.append({
                "type": "语义对立",
                "weight": 0.5,
                "details": f"检测到潜在语义对立：'{pair[0]}' 与 '{pair[1]}'"
            })
    
    # 检测转折连词后的矛盾
    contrast_conjunctions = ['但', '然而', '却', '不过', '只是', '相反', '尽管如此']
    for conj in contrast_conjunctions:
        if conj in text:
            sentences = re.split(r'[.!?。！？]', text)
            for sent in sentences:
                if conj in sent:
                    parts = sent.split(conj)
                    if len(parts) >= 2:
                        before = parts[0].strip()
                        after = parts[1].strip()
                        if before and after:
                            # 检测积极/消极词对立
                            positive_words = {'好', '强', '高', '优秀', '稳定', '先进', '透明', '合理'}
                            negative_words = {'差', '弱', '低', '差', '问题', '风险', '担忧', '不合理'}
                            has_positive = any(w in before for w in positive_words)
                            has_negative = any(w in after for w in negative_words)
                            if has_positive and has_negative:
                                contradictions.append({
                                    "type": "评价矛盾",
                                    "weight": 0.6,
                                    "details": f"转折后评价对立：'{before[:20]}...' {conj} '{after[:20]}...'"
                                })
    
    return contradictions

# 增强的D值计算
def calculate_development_enhanced(text: str) -> float:
    """增强的发展性计算"""
    sentences = re.split(r'[.!?。！？]', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) < 2:
        return 0.0
    
    # 词汇丰富度
    words = re.findall(r'[\w\u4e00-\u9fff]+', text)
    if not words:
        return 0.0
    
    unique_words = set(words)
    ttr = len(unique_words) / len(words)
    
    # 句子多样性
    sentence_lengths = [len(s.split()) for s in sentences]
    if len(sentence_lengths) >= 2:
        len_std = np.std(sentence_lengths) / np.mean(sentence_lengths)
    else:
        len_std = 0
    
    # 信息推进度
    info_progress = min(1.0, len(sentences) / 5)
    
    # 综合得分
    return min(1.0, 0.4 * ttr + 0.3 * len_std + 0.3 * info_progress)

# 初始化评估器
evaluator = HarmonyEvaluator(domain="general", enable_observations=False)
detector = ContradictionDetector()

results = []

print("=" * 80)
print("【万象渊鉴·场域诊断报告】")
print("生成时间:", datetime.now().isoformat())
print("=" * 80)

for i, scenario in enumerate(scenarios, 1):
    print(f"\n--- 场景{i}: {scenario['title']} ---")
    
    try:
        text = scenario['text']
        
        # 基础评估
        concept_graph = ConceptGraph(text, [])
        u = compute_U(concept_graph)
        d = calculate_development_enhanced(text)
        a_base = compute_A(text, detector)
        
        # 增强的矛盾检测
        contradictions = detect_contradictions(text)
        a_enhanced = min(1.0, a_base + len(contradictions) * 0.15)
        
        # 计算和谐度
        h = compute_harmony(u, d, a_enhanced, 0.4, 0.4, 0.2)
        
        print(f"U值（统一性）: {u:.4f}")
        print(f"D值（发展性）: {d:.4f}")
        print(f"A值（对抗性）: {a_enhanced:.4f}")
        print(f"H值（和谐度）: {h:.4f}")
        
        if contradictions:
            print(f"\n矛盾点定位 ({len(contradictions)}处):")
            for j, cp in enumerate(contradictions, 1):
                print(f"  {j}. 类型: {cp['type']}, 权重: {cp['weight']:.4f}, 详情: {cp['details']}")
        else:
            print("\n矛盾点定位: 未检测到矛盾")
        
        print("\n翻转点检测:")
        sentences = re.split(r'[.!?。！？]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        if len(sentences) >= 3:
            flip_points = []
            for j in range(1, len(sentences)):
                prev_has_positive = any(w in sentences[j-1] for w in ['好', '强', '高', '支持', '认可'])
                curr_has_negative = any(w in sentences[j] for w in ['差', '弱', '低', '反对', '担忧'])
                if prev_has_positive and curr_has_negative:
                    flip_points.append({
                        "position": j,
                        "description": f"第{j}句出现评价翻转"
                    })
            if flip_points:
                for j, fp in enumerate(flip_points, 1):
                    print(f"  {j}. 位置: {fp['position']}, {fp['description']}")
            else:
                print("  未检测到翻转点")
        else:
            print("  句子数不足，跳过翻转点检测")
        
        unresolved_count = len(contradictions)
        if unresolved_count > 0:
            print(f"\n未解矛盾 ({unresolved_count}处):")
            for j, cp in enumerate(contradictions, 1):
                print(f"  {j}. {cp['details']}")
        else:
            print("\n未解矛盾: 无")
        
        results.append({
            "scenario": i,
            "title": scenario['title'],
            "u": u,
            "d": d,
            "a": a_enhanced,
            "h": h,
            "contradiction_count": len(contradictions),
            "flip_point_count": len(flip_points) if 'flip_points' in locals() else 0,
            "unresolved_count": unresolved_count,
        })
        
    except Exception as e:
        print(f"评估失败: {e}")
        import traceback
        traceback.print_exc()
        results.append({
            "scenario": i,
            "title": scenario['title'],
            "error": str(e)
        })

print("\n" + "=" * 80)
print("【汇总报告】")
print("=" * 80)

print("\n一、各场景U/D/A/H轨迹对比")
print("-" * 70)
print(f"{'场景':<25} {'U值':<8} {'D值':<8} {'A值':<8} {'H值':<8}")
print("-" * 70)
for r in results:
    if 'error' not in r:
        title_short = r['title'][:25] if len(r['title']) > 25 else r['title']
        print(f"{title_short:<25} {r['u']:<8.4f} {r['d']:<8.4f} {r['a']:<8.4f} {r['h']:<8.4f}")

total_contradictions = sum(r['contradiction_count'] for r in results if 'error' not in r)
total_flip_points = sum(r['flip_point_count'] for r in results if 'error' not in r)
total_unresolved = sum(r['unresolved_count'] for r in results if 'error' not in r)

print(f"\n二、统计汇总")
print(f"  - 检测到的矛盾点总数: {total_contradictions}")
print(f"  - 检测到的翻转点总数: {total_flip_points}")
print(f"  - 未解矛盾总数: {total_unresolved}")

print(f"\n三、文本类型与诊断结果对应关系")
print("-" * 70)
type_map = {
    1: "合同文本",
    2: "对话转录",
    3: "会议纪要",
    4: "政策文件",
    5: "技术文档",
    6: "新闻报道"
}
for r in results:
    if 'error' not in r:
        text_type = type_map.get(r['scenario'], "未知")
        a_level = "高对抗性" if r['a'] > 0.5 else ("中对抗性" if r['a'] > 0.2 else "低对抗性")
        h_level = "高和谐度" if r['h'] > 0.7 else ("中和谐度" if r['h'] > 0.4 else "低和谐度")
        print(f"  {text_type:<10} | A值={r['a']:.4f}({a_level}) | H值={r['h']:.4f}({h_level}) | 矛盾={r['contradiction_count']}处")