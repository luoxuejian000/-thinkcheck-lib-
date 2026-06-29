"""
简化的 ThinkCheck 升级验证测试脚本
"""

from thinkcheck_harmony.evaluator import HarmonyEvaluator
from thinkcheck_harmony.metrics import ContradictionDetector

def print_separator(title=""):
    print("\n" + "=" * 80)
    if title:
        print(title)
        print("=" * 80)

def test_detector_directly():
    """直接测试 ContradictionDetector 的功能"""
    print_separator("直接测试 ContradictionDetector")
    
    detector = ContradictionDetector()
    
    # 测试法律文书案例
    text = "根据公司章程，持有公司51%股权的股东享有控股权。因此，该股东并未持有多数股权。"
    
    # 测试直接矛盾
    contradictions = detector.detect_contradictions(text)
    print("直接矛盾检测结果:")
    for i, c in enumerate(contradictions):
        print(f"  {i+1}. {c}")
    
    # 测试否定词检测
    negation = detector.detect_negation(text)
    print(f"\n否定词检测结果: {negation:.4f}")
    
    # 测试语义对立
    opposition = detector.detect_semantic_opposition(text)
    print(f"语义对立检测结果: {opposition:.4f}")
    
    # 测试综合对抗性
    a_value, detail = detector.calculate_adversarial(text)
    print(f"\n综合对抗性A值: {a_value:.4f}")
    print(f"详细信息:")
    print(f"  总边数: {detail['total_edges']}")
    for i, edge in enumerate(detail['edges']):
        print(f"  {i+1}. 类型: {edge['type']}, 权重: {edge['weight']:.4f}")
    
    return a_value

def main():
    print_separator("ThinkCheck 升级验证测试")
    
    a_value = test_detector_directly()
    
    print_separator("HarmonyEvaluator 测试")
    
    evaluator = HarmonyEvaluator()
    
    # 测试用例
    test_cases = [
        {
            "name": "法律文书矛盾",
            "text": "根据公司章程，持有公司51%股权的股东享有控股权。因此，该股东并未持有多数股权。"
        },
        {
            "name": "纯语义矛盾",
            "text": "功能强大，但完全没用。"
        },
        {
            "name": "否定词矛盾",
            "text": "产品非常好，但质量极差。"
        },
        {
            "name": "假阳性防御",
            "text": "我喜欢吃苹果。苹果公司发布了新手机。"
        }
    ]
    
    for case in test_cases:
        print_separator(f"测试用例: {case['name']}")
        result = evaluator.evaluate(case['text'])
        print(f"U: {result.scores['U']:.4f}")
        print(f"D: {result.scores['D']:.4f}")
        print(f"A: {result.scores['A']:.4f}")
        print(f"H: {result.scores['H']:.4f}")
        
        if 'A_detail' in result.scores:
            detail = result.scores['A_detail']
            print(f"\nA值详细:")
            print(f"  解释: {detail['interpretation']}")
            print(f"  边数: {detail['total_edges']}")
            for i, edge in enumerate(detail['edges']):
                print(f"  {i+1}. {edge['type']}: {edge['weight']:.4f}")
    
    print_separator("测试完成")

if __name__ == "__main__":
    main()
