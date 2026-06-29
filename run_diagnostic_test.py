"""
万象渊鉴·场域诊断测试集 - 批量评估脚本
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'thinkcheck-harmony'))

from thinkcheck_harmony.evaluator import HarmonyEvaluator
from thinkcheck_harmony.report_generator import DiagnosticReport
from datetime import datetime

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
            # 跳过标题行
            continue
        # 提取场景标题和内容
        lines = section.split("\n")
        title = lines[0].strip() if lines else ""
        text = "\n".join(lines[1:]).strip()
        if title and text:
            scenarios.append({"title": title, "text": text})

# 初始化评估器
evaluator = HarmonyEvaluator(domain="general", enable_observations=False)

# 存储所有诊断结果
results = []

print("=" * 80)
print("【万象渊鉴·场域诊断报告】")
print("生成时间:", datetime.now().isoformat())
print("=" * 80)

for i, scenario in enumerate(scenarios, 1):
    print(f"\n--- 场景{i}: {scenario['title']} ---")
    
    try:
        # 评估文本
        report = evaluator.evaluate(scenario['text'])
        
        # 提取四维指标
        u = report.U
        d = report.D
        a = report.A
        h = report.H
        
        # 获取矛盾点
        contradiction_points = []
        if hasattr(report, 'micro_details') and report.micro_details:
            edges_detail = report.micro_details.get('edges_detail', {})
            if edges_detail:
                for edge in edges_detail.get('edges', []):
                    contradiction_points.append({
                        "type": edge.get('type', 'unknown'),
                        "weight": edge.get('weight', 0),
                        "details": edge.get('details', '')
                    })
        
        # 获取翻转点
        flip_points = []
        if hasattr(report, 'meso_details') and report.meso_details:
            flip_points = report.meso_details.get('flip_points', [])
        
        # 获取未解矛盾
        unresolved_contradictions = []
        if hasattr(report, 'drift_warnings') and report.drift_warnings:
            for warning in report.drift_warnings:
                unresolved_contradictions.append(warning.get('message', ''))
        
        # 输出结果
        print(f"U值（统一性）: {u:.4f}")
        print(f"D值（发展性）: {d:.4f}")
        print(f"A值（对抗性）: {a:.4f}")
        print(f"H值（和谐度）: {h:.4f}")
        
        if contradiction_points:
            print(f"\n矛盾点定位 ({len(contradiction_points)}处):")
            for j, cp in enumerate(contradiction_points, 1):
                print(f"  {j}. 类型: {cp['type']}, 权重: {cp['weight']:.4f}, 详情: {cp['details']}")
        else:
            print("\n矛盾点定位: 未检测到矛盾")
        
        if flip_points:
            print(f"\n翻转点检测 ({len(flip_points)}处):")
            for j, fp in enumerate(flip_points, 1):
                print(f"  {j}. 位置: {fp.get('position', 'N/A')}, ΔU={fp.get('u_delta', 'N/A')}, ΔD={fp.get('d_delta', 'N/A')}, ΔH={fp.get('h_delta', 'N/A')}")
        else:
            print("\n翻转点检测: 未检测到翻转点")
        
        if unresolved_contradictions:
            print(f"\n未解矛盾 ({len(unresolved_contradictions)}处):")
            for j, uc in enumerate(unresolved_contradictions, 1):
                print(f"  {j}. {uc}")
        else:
            print("\n未解矛盾: 无")
        
        # 保存结果
        results.append({
            "scenario": i,
            "title": scenario['title'],
            "u": u,
            "d": d,
            "a": a,
            "h": h,
            "contradiction_count": len(contradiction_points),
            "flip_point_count": len(flip_points),
            "unresolved_count": len(unresolved_contradictions),
            "contradiction_points": contradiction_points,
            "flip_points": flip_points
        })
        
    except Exception as e:
        print(f"评估失败: {e}")
        results.append({
            "scenario": i,
            "title": scenario['title'],
            "error": str(e)
        })

# 生成汇总报告
print("\n" + "=" * 80)
print("【汇总报告】")
print("=" * 80)

print("\n一、各场景U/D/A/H轨迹对比")
print("-" * 60)
print(f"{'场景':<20} {'U值':<8} {'D值':<8} {'A值':<8} {'H值':<8}")
print("-" * 60)
for r in results:
    if 'error' not in r:
        print(f"{r['title']:<20} {r['u']:<8.4f} {r['d']:<8.4f} {r['a']:<8.4f} {r['h']:<8.4f}")

total_contradictions = sum(r['contradiction_count'] for r in results if 'error' not in r)
total_flip_points = sum(r['flip_point_count'] for r in results if 'error' not in r)
total_unresolved = sum(r['unresolved_count'] for r in results if 'error' not in r)

print(f"\n二、统计汇总")
print(f"  - 检测到的矛盾点总数: {total_contradictions}")
print(f"  - 检测到的翻转点总数: {total_flip_points}")
print(f"  - 未解矛盾总数: {total_unresolved}")

print(f"\n三、文本类型与诊断结果对应关系")
print("-" * 60)
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