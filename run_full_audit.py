"""
万象渊鉴·场域诊断测试集 - 完整场域审计脚本
文件：万象渊鉴·场域诊断测试集.txt（约12万字）
窗格大小：2000字符，共60个窗格
"""

import sys
import os
import re
import numpy as np
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'thinkcheck-harmony'))

from thinkcheck_harmony.evaluator import HarmonyEvaluator
from thinkcheck_harmony.concept_graph import ConceptGraph
from thinkcheck_harmony.core import compute_U, compute_D, compute_A, compute_harmony
from thinkcheck_harmony.contradiction_detector import ContradictionDetector
from datetime import datetime

LAMBDA_U = 0.4
LAMBDA_D = 0.4
LAMBDA_A = 0.2
PANE_SIZE = 2000

def read_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def split_into_panes(content, pane_size=PANE_SIZE):
    panes = []
    total_chars = len(content)
    for i in range((total_chars + pane_size - 1) // pane_size):
        start = i * pane_size
        end = min((i + 1) * pane_size, total_chars)
        panes.append({
            "number": i + 1,
            "start": start,
            "end": end,
            "content": content[start:end]
        })
    return panes

def calculate_development(text):
    sentences = re.split(r'[.!?。！？]', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if len(sentences) < 2:
        return 0.0
    words = re.findall(r'[\w\u4e00-\u9fff]+', text)
    if not words:
        return 0.0
    ttr = len(set(words)) / len(words)
    sentence_lengths = [len(s.split()) for s in sentences]
    len_std = np.std(sentence_lengths) / np.mean(sentence_lengths) if len(sentence_lengths) >= 2 else 0
    info_progress = min(1.0, len(sentences) / 5)
    return min(1.0, 0.4 * ttr + 0.3 * len_std + 0.3 * info_progress)

def detect_contradictions(text):
    contradictions = []
    
    numeric_pattern = r'(\d+)\s*(日|天|个月|周|年|美元|元|%)'
    numbers = re.findall(numeric_pattern, text)
    if len(numbers) >= 2:
        for i in range(len(numbers)):
            for j in range(i + 1, len(numbers)):
                if numbers[i][1] == numbers[j][1]:
                    diff = abs(int(numbers[i][0]) - int(numbers[j][0]))
                    if diff > 5:
                        contradictions.append({
                            "type": "数值矛盾",
                            "weight": 0.8,
                            "details": f"{numbers[i][0]}{numbers[i][1]} vs {numbers[j][0]}{numbers[j][1]}"
                        })
    
    opposition_pairs = [("唯一", "选择"), ("被迫", "主动"), ("不会", "可能"), 
                        ("支持", "反对"), ("符合", "不符合"), ("是", "不是"),
                        ("有", "没有"), ("能", "不能"), ("应该", "不应该")]
    for pair in opposition_pairs:
        if pair[0] in text and pair[1] in text:
            contradictions.append({
                "type": "语义对立",
                "weight": 0.5,
                "details": f"'{pair[0]}' 与 '{pair[1]}'"
            })
    
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
                            positive_words = {'好', '强', '高', '优秀', '稳定', '先进', '透明', '合理'}
                            negative_words = {'差', '弱', '低', '问题', '风险', '担忧', '不合理'}
                            has_positive = any(w in before for w in positive_words)
                            has_negative = any(w in after for w in negative_words)
                            if has_positive and has_negative:
                                contradictions.append({
                                    "type": "评价矛盾",
                                    "weight": 0.6,
                                    "details": f"'{before[:20]}...' {conj} '{after[:20]}...'"
                                })
    
    return contradictions

def extract_core_terms(text, top_n=10):
    words = re.findall(r'[\w\u4e00-\u9fff]{2,}', text)
    stop_words = {'的', '是', '在', '我', '有', '和', '了', '不', '人', '都', '一', '一个',
                  '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看',
                  '好', '自己', '这', '我们', '他们', '但是', '什么', '因为', '所以',
                  '可以', '如果', '就是', '知道', '应该', '现在', '已经', '不过', '还是',
                  '其实', '可能', '觉得', '认为', '需要', '这个', '那个', '这些', '那些'}
    filtered = [w for w in words if w not in stop_words]
    counter = Counter(filtered)
    return [term for term, _ in counter.most_common(top_n)]

def detect_flip_points(pane_results):
    flip_points = []
    for i in range(1, len(pane_results)):
        prev = pane_results[i - 1]
        curr = pane_results[i]
        delta_u = curr['u'] - prev['u']
        delta_d = curr['d'] - prev['d']
        delta_h = curr['h'] - prev['h']
        if delta_u > 0.15 and delta_d < -0.10 and delta_h < -0.08:
            flip_points.append({
                "position": curr['number'],
                "prev_u": prev['u'],
                "prev_d": prev['d'],
                "prev_h": prev['h'],
                "curr_u": curr['u'],
                "curr_d": curr['d'],
                "curr_h": curr['h'],
                "summary": curr['summary'][:50]
            })
    return flip_points

def evaluate_pane(pane, evaluator, detector):
    text = pane['content']
    concept_graph = ConceptGraph(text, [])
    u = compute_U(concept_graph)
    d = calculate_development(text)
    a_base = compute_A(text, detector)
    contradictions = detect_contradictions(text)
    a_enhanced = min(1.0, a_base + len(contradictions) * 0.15)
    h = compute_harmony(u, d, a_enhanced, LAMBDA_U, LAMBDA_D, LAMBDA_A)
    
    sentences = re.split(r'[.!?。！？]', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    flip_points_in_pane = []
    if len(sentences) >= 3:
        for j in range(1, len(sentences)):
            prev_has_positive = any(w in sentences[j-1] for w in ['好', '强', '高', '支持', '认可'])
            curr_has_negative = any(w in sentences[j] for w in ['差', '弱', '低', '反对', '担忧'])
            if prev_has_positive and curr_has_negative:
                flip_points_in_pane.append({
                    "position": j,
                    "description": f"第{j}句出现评价翻转"
                })
    
    return {
        "number": pane['number'],
        "start": pane['start'],
        "end": pane['end'],
        "u": u,
        "d": d,
        "a": a_enhanced,
        "h": h,
        "summary": text[:100].replace("\n", " ").replace("\r", " "),
        "contradictions": contradictions,
        "flip_points": flip_points_in_pane,
        "core_terms": extract_core_terms(text, 5)
    }

def main():
    file_path = "万象渊鉴·场域诊断测试集.txt"
    content = read_file(file_path)
    panes = split_into_panes(content)
    
    evaluator = HarmonyEvaluator(domain="general", enable_observations=False)
    detector = ContradictionDetector()
    
    output_lines = []
    
    output_lines.append("=" * 80)
    output_lines.append("[万象渊鉴·场域诊断审计报告]")
    output_lines.append("文件路径: " + file_path)
    output_lines.append("总字符数: " + str(len(content)))
    output_lines.append("总窗格数: " + str(len(panes)))
    output_lines.append("窗格大小: " + str(PANE_SIZE) + " 字符")
    output_lines.append("生成时间: " + datetime.now().isoformat())
    output_lines.append("=" * 80)
    output_lines.append("")
    
    pane_results = []
    
    for pane in panes:
        result = evaluate_pane(pane, evaluator, detector)
        pane_results.append(result)
        
        output_lines.append("")
        output_lines.append("[窗格 " + str(result['number']) + " / 总计 " + str(len(panes)) + "]")
        output_lines.append("位置范围：字符 [" + str(result['start']) + "] - [" + str(result['end']) + "]")
        output_lines.append("内容摘要：" + result['summary'])
        output_lines.append("")
        output_lines.append("U 值：" + "{:.4f}".format(result['u']))
        output_lines.append("D 值：" + "{:.4f}".format(result['d']))
        output_lines.append("A 值：" + "{:.4f}".format(result['a']))
        output_lines.append("H 值：" + "{:.4f}".format(result['h']))
        
        harmony_status = "在窗口内" if 0.4 <= result['h'] <= 0.7 else ("高于窗口" if result['h'] > 0.7 else "低于窗口")
        output_lines.append("谐振窗口状态：" + harmony_status)
        
        if result['contradictions']:
            output_lines.append("")
            output_lines.append("矛盾点定位（" + str(len(result['contradictions'])) + "处）：")
            for j, cp in enumerate(result['contradictions'], 1):
                output_lines.append("   - 矛盾 " + str(j) + "：" + cp['details'])
                output_lines.append("     A 值：" + "{:.2f}".format(cp['weight']))
                output_lines.append("     类型：" + cp['type'])
        else:
            output_lines.append("")
            output_lines.append("矛盾点定位：未检测到矛盾")
        
        if result['flip_points']:
            output_lines.append("")
            output_lines.append("翻转点检测（" + str(len(result['flip_points'])) + "处）：")
            for j, fp in enumerate(result['flip_points'], 1):
                output_lines.append("   - 翻转点位置：第" + str(fp['position']) + "句")
                output_lines.append("     描述：" + fp['description'])
        else:
            output_lines.append("")
            output_lines.append("翻转点检测：未检测到翻转点")
        
        if result['core_terms']:
            output_lines.append("")
            output_lines.append("核心术语：" + ", ".join(result['core_terms']))
        
        output_lines.append("-" * 60)
    
    u_values = [r['u'] for r in pane_results]
    d_values = [r['d'] for r in pane_results]
    a_values = [r['a'] for r in pane_results]
    h_values = [r['h'] for r in pane_results]
    
    all_contradictions = []
    for r in pane_results:
        for cp in r['contradictions']:
            all_contradictions.append({
                "pane": r['number'],
                "type": cp['type'],
                "weight": cp['weight'],
                "details": cp['details']
            })
    
    flip_points = detect_flip_points(pane_results)
    
    unresolved_contradictions = all_contradictions
    
    output_lines.append("")
    output_lines.append("=" * 80)
    output_lines.append("[完整场域审计汇总报告]")
    output_lines.append("=" * 80)
    
    output_lines.append("")
    output_lines.append("1. 全文整体指标快照")
    output_lines.append("-" * 60)
    output_lines.append("   平均 U 值：" + "{:.4f}".format(np.mean(u_values)))
    output_lines.append("   平均 D 值：" + "{:.4f}".format(np.mean(d_values)))
    output_lines.append("   平均 A 值：" + "{:.4f}".format(np.mean(a_values)))
    output_lines.append("   平均 H 值：" + "{:.4f}".format(np.mean(h_values)))
    output_lines.append("   U 值标准差：" + "{:.4f}".format(np.std(u_values)))
    output_lines.append("   D 值标准差：" + "{:.4f}".format(np.std(d_values)))
    output_lines.append("   A 值标准差：" + "{:.4f}".format(np.std(a_values)))
    output_lines.append("   H 值标准差：" + "{:.4f}".format(np.std(h_values)))
    output_lines.append("   U 值最高：" + "{:.4f}".format(max(u_values)) + " (窗格" + str(pane_results[np.argmax(u_values)]['number']) + ")")
    output_lines.append("   U 值最低：" + "{:.4f}".format(min(u_values)) + " (窗格" + str(pane_results[np.argmin(u_values)]['number']) + ")")
    output_lines.append("   A 值最高：" + "{:.4f}".format(max(a_values)) + " (窗格" + str(pane_results[np.argmax(a_values)]['number']) + ")")
    output_lines.append("   H 值最低：" + "{:.4f}".format(min(h_values)) + " (窗格" + str(pane_results[np.argmin(h_values)]['number']) + ")")
    
    high_a_panes = [(r['number'], r['a'], r['summary'][:50]) for r in pane_results if r['a'] > 0.3]
    output_lines.append("")
    output_lines.append("2. 矛盾点总清单（A 值 > 0.3）")
    output_lines.append("-" * 60)
    if high_a_panes:
        for num, a_val, summary in high_a_panes:
            output_lines.append("   窗格" + str(num) + ": A=" + "{:.4f}".format(a_val) + " - " + summary)
    else:
        output_lines.append("   无 A 值超过 0.3 的窗格")
    
    output_lines.append("")
    output_lines.append("3. 翻转点时间线")
    output_lines.append("-" * 60)
    if flip_points:
        for fp in flip_points:
            output_lines.append("   窗格" + str(fp['position']) + ": 翻转前 U/D/H=" + "{:.2f}".format(fp['prev_u']) + "/" + "{:.2f}".format(fp['prev_d']) + "/" + "{:.2f}".format(fp['prev_h']) + " -> 翻转后 U/D/H=" + "{:.2f}".format(fp['curr_u']) + "/" + "{:.2f}".format(fp['curr_d']) + "/" + "{:.2f}".format(fp['curr_h']))
    else:
        output_lines.append("   未检测到翻转点")
    
    output_lines.append("")
    output_lines.append("4. 核心术语漂移曲线")
    output_lines.append("-" * 60)
    all_terms = []
    for r in pane_results:
        all_terms.extend(r['core_terms'])
    top_terms = [term for term, _ in Counter(all_terms).most_common(10)]
    for term in top_terms:
        occurrences = [str(r['number']) for r in pane_results if term in r['core_terms']]
        output_lines.append("   " + term + ": 出现在窗格 " + ", ".join(occurrences))
    
    output_lines.append("")
    output_lines.append("5. 建设性冲突 vs 破坏性冲突对比表")
    output_lines.append("-" * 60)
    constructive = [(r['number'], r['a'], r['d']) for r in pane_results if r['a'] > 0.3 and r['d'] > 0.5]
    destructive = [(r['number'], r['a'], r['d']) for r in pane_results if r['a'] > 0.3 and r['d'] <= 0.5]
    consensus = [(r['number'], r['a'], r['d']) for r in pane_results if r['a'] <= 0.3]
    output_lines.append("   建设性冲突（高A+高D）：" + str(len(constructive)) + "个窗格")
    output_lines.append("   破坏性冲突（高A+低D）：" + str(len(destructive)) + "个窗格")
    output_lines.append("   共识窗格（低A）：" + str(len(consensus)) + "个窗格")
    
    output_lines.append("")
    output_lines.append("6. 未解矛盾优先级清单")
    output_lines.append("-" * 60)
    unresolved_sorted = sorted(unresolved_contradictions, key=lambda x: x['weight'], reverse=True)
    if unresolved_sorted:
        for i, cp in enumerate(unresolved_sorted[:10], 1):
            output_lines.append("   " + str(i) + ". 窗格" + str(cp['pane']) + " - " + cp['details'] + " (权重=" + "{:.2f}".format(cp['weight']) + ", 类型=" + cp['type'] + ")")
    else:
        output_lines.append("   无未解矛盾")
    
    output_lines.append("")
    output_lines.append("7. 沉默失谐窗格汇总")
    output_lines.append("-" * 60)
    low_a_high_potential = [(r['number'], r['a'], r['summary'][:30]) for r in pane_results 
                           if r['a'] < 0.2 and len(r['contradictions']) > 0]
    if low_a_high_potential:
        output_lines.append("   警告：以下窗格 A 值可能被低估")
        for num, a_val, summary in low_a_high_potential:
            output_lines.append("   窗格" + str(num) + ": A=" + "{:.4f}".format(a_val) + " - " + summary)
    else:
        output_lines.append("   无检测到沉默失谐窗格")
    
    output_lines.append("")
    output_lines.append("8. 诊断结论")
    output_lines.append("-" * 60)
    avg_h = np.mean(h_values)
    avg_a = np.mean(a_values)
    if avg_h > 0.7:
        output_lines.append("   全文场域状态：高和谐度")
    elif avg_h > 0.4:
        output_lines.append("   全文场域状态：中和谐度")
    else:
        output_lines.append("   全文场域状态：低和谐度")
    
    if avg_a > 0.3:
        output_lines.append("   全文对抗性：偏高")
    else:
        output_lines.append("   全文对抗性：正常")
    
    output_lines.append("")
    output_lines.append("   检测到的矛盾点总数：" + str(len(all_contradictions)))
    output_lines.append("   检测到的翻转点总数：" + str(len(flip_points)))
    output_lines.append("   未解矛盾总数：" + str(len(unresolved_contradictions)))
    
    output_lines.append("")
    output_lines.append("=" * 80)
    output_lines.append("未解矛盾汇总")
    output_lines.append("=" * 80)
    if unresolved_sorted:
        for cp in unresolved_sorted:
            output_lines.append("   窗格" + str(cp['pane']) + " - " + cp['type'] + ": " + cp['details'])
    else:
        output_lines.append("   无未解矛盾")
    
    output_lines.append("")
    output_lines.append("本报告仅呈现诊断数据，判断权在您手中")
    
    with open("full_audit_report.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    
    print("审计报告已生成：full_audit_report.txt")

if __name__ == "__main__":
    main()