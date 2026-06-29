import os
import json
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from thinkcheck_harmony import HarmonyEvaluator
from thinkcheck_agent.core.actuator import HarmonyActuator

def main():
    with open("complex_case.txt", "r", encoding="utf-8") as f:
        doc = f.read()
    print("原始文档:\n", doc)

    eva = HarmonyEvaluator()
    scores = eva.evaluate(doc)
    scores_dict = scores.to_dict()
    print("\n原始评分:", json.dumps(scores_dict, indent=2, ensure_ascii=False))

    act = HarmonyActuator()
    result = act.harmonize_document(doc, diagnosis=scores_dict)
    fixed = result.get('tuned_text', doc)
    usage = result.get('usage', {})
    print("\n修复后文档:\n", fixed)
    print("\nToken使用:", usage)

    new_scores = eva.evaluate(fixed)
    new_scores_dict = new_scores.to_dict()
    print("\n修复后评分:", json.dumps(new_scores_dict, indent=2, ensure_ascii=False))

    with open("report.json", "w", encoding="utf-8") as f:
        json.dump({
            "original": doc,
            "original_scores": scores_dict,
            "fixed": fixed,
            "fixed_scores": new_scores_dict,
            "token_usage": usage,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2, ensure_ascii=False)
    print("\n详细报告已保存至 report.json")

if __name__ == "__main__":
    main()
