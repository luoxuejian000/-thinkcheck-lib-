"""
测试 ThinkCheck 升级验证脚本
测试所有要求的功能：
1. 法律文书矛盾检测（原本没有检测到的矛盾应该能检测到了）
2. 纯语义矛盾检测
3. 否定词矛盾检测
4. 假阳性防御
"""

from thinkcheck_harmony.evaluator import HarmonyEvaluator
import sys

def print_separator(title=""):
    print("\n" + "=" * 80)
    if title:
        print(title)
        print("=" * 80)

def test_case(name, text, expected_a_min=0.0, expected_a_max=1.0):
    """运行单个测试用例"""
    print_separator(f"测试用例: {name}")
    print(f"文本内容:\n{repr(text)}")
    
    evaluator = HarmonyEvaluator()
    result = evaluator.evaluate(text)
    
    print(f"\n评估结果:")
    print(f"  U (统一性): {result.scores['U']:.4f}")
    print(f"  D (发展性): {result.scores['D']:.4f}")
    print(f"  A (对抗性): {result.scores['A']:.4f}")
    print(f"  H (和谐度): {result.scores['H']:.4f}")
    
    a_value = result.scores['A']
    passed = expected_a_min <= a_value <= expected_a_max
    
    if passed:
        print(f"\n✅ 测试通过!")
        if 'A_detail' in result.scores:
            detail = result.scores['A_detail']
            print(f"  矛盾边总数: {detail['total_edges']}")
            print(f"  解释: {detail['interpretation']}")
            if detail['edges']:
                print(f"  详细矛盾边:")
                for i, edge in enumerate(detail['edges']):
                    print(f"    {i+1}. 类型: {edge['type']}, 权重: {edge['weight']:.4f}, 详情: {edge['detail']}")
    else:
        print(f"\n❌ 测试失败! A值 {a_value:.4f} 不在预期范围 [{expected_a_min:.4f}, {expected_a_max:.4f}]")
    
    return passed

def main():
    print_separator("ThinkCheck 升级验证测试")
    
    all_passed = True
    
    # 测试用例 1: 法律文书矛盾（之前漏检的情况）
    legal_text = "根据公司章程，持有公司51%股权的股东享有控股权。因此，该股东并未持有多数股权。"
    passed = test_case("法律文书矛盾", legal_text, expected_a_min=0.05)
    all_passed = all_passed and passed
    
    # 测试用例 2: 纯语义矛盾
    contradiction_text = "功能强大，但完全没用。"
    passed = test_case("纯语义矛盾", contradiction_text, expected_a_min=0.1)
    all_passed = all_passed and passed
    
    # 测试用例 3: 否定词矛盾
    negative_text = "产品非常好，但质量极差。"
    passed = test_case("否定词矛盾", negative_text, expected_a_min=0.1)
    all_passed = all_passed and passed
    
    # 测试用例 4: 假阳性防御
    false_positive_text = "我喜欢吃苹果。苹果公司发布了新手机。"
    passed = test_case("假阳性防御", false_positive_text, expected_a_max=0.1)
    all_passed = all_passed and passed
    
    # 测试用例 5: 正常文本
    normal_text = "人工智能是计算机科学的一个分支，它企图了解智能的实质。"
    passed = test_case("正常文本", normal_text, expected_a_max=0.1)
    all_passed = all_passed and passed
    
    print_separator("测试总结")
    if all_passed:
        print("✅ 所有测试用例通过！")
    else:
        print("❌ 部分测试用例失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()
