import os
import json
import sys
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# 强制阈值设为 0.99，确保任何文档都会触发 API 调用
os.environ['THINKCHECK_HARMONY_THRESHOLD'] = '0.99'

from thinkcheck_harmony import HarmonyEvaluator
from thinkcheck_agent.core.actuator import HarmonyActuator

def main():
    print("\n" + "="*60)
    print(" ThinkCheck Agent - 强制 API 调用演示")
    print("="*60)

    with open("low_harmony_case.txt", "r", encoding="utf-8") as f:
        doc = f.read().strip()
    print("\n【原始文档】\n", doc)

    evaluator = HarmonyEvaluator()
    scores = evaluator.evaluate(doc)
    scores_dict = scores.to_dict()
    print("\n【四维评估原始分数】")
    print(f"U (统一性): {scores_dict.get('U', 0):.4f}")
    print(f"D (发展性): {scores_dict.get('D', 0):.4f}")
    print(f"A (对抗性): {scores_dict.get('A', 0):.4f}")
    print(f"H (和谐度): {scores_dict.get('H', 0):.4f}")
    print(f"建议: {scores_dict.get('suggestions', [])}")
    print(f"警告: {scores_dict.get('warnings', [])}")

    actuator = HarmonyActuator()
    
    # 强制诊断为需要调谐
    diagnosis = scores_dict.copy()
    diagnosis['needs_tuning'] = True
    diagnosis['pathology'] = '逻辑自杀'
    
    print("\n【调用 DeepSeek API】...")
    try:
        result = actuator.tune(doc, diagnosis)
        fixed_doc = result.get('tuned_text', doc)
        usage = result.get('usage', {})
        
        if result.get('success', False):
            print("API 调用成功")
            print(f"策略: {result.get('strategy')}")
        else:
            print("API 调用完成")
        
        print(f"Token 使用量: {usage}")
    except Exception as e:
        print(f"调用失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print("\n【修复后文档】")
    print(fixed_doc)

    new_scores = evaluator.evaluate(fixed_doc)
    new_scores_dict = new_scores.to_dict()
    print("\n【四维评估修复后分数】")
    print(f"U: {new_scores_dict.get('U', 0):.4f} (变化: {new_scores_dict.get('U',0)-scores_dict.get('U',0):+.4f})")
    print(f"D: {new_scores_dict.get('D', 0):.4f} (变化: {new_scores_dict.get('D',0)-scores_dict.get('D',0):+.4f})")
    print(f"A: {new_scores_dict.get('A', 0):.4f} (变化: {new_scores_dict.get('A',0)-scores_dict.get('A',0):+.4f})")
    print(f"H: {new_scores_dict.get('H', 0):.4f} (变化: {new_scores_dict.get('H',0)-scores_dict.get('H',0):+.4f})")

    # 保存报告
    report = {
        "timestamp": datetime.now().isoformat(),
        "original_doc": doc,
        "original_scores": scores_dict,
        "fixed_doc": fixed_doc,
        "fixed_scores": new_scores_dict,
        "token_usage": usage
    }
    with open("force_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print("\n【报告已保存】force_report.json")
    print("="*60)
    print("演示完成。")

if __name__ == "__main__":
    main()
