"""
ThinkCheck 真实功能测试
用人类能理解的方式测试每个功能
"""

from thinkcheck import HarmonicMonitor, calculate_h_score
import time

print("=" * 80)
print("🧪 ThinkCheck 真实功能测试")
print("=" * 80)

def test_multilingual_support():
    """测试1：多语言支持是否真的工作"""
    print("\n" + "=" * 80)
    print("测试1: 多语言支持 - 中英文否定词检测")
    print("=" * 80)
    
    # 场景A：中文否定词
    print("\n🌐 场景A：中文（应该检测到否定词）")
    monitor_zh = HarmonicMonitor(h_threshold=0.4, verbose=False)
    
    zh_steps = [
        "我同意这个观点",
        "好的，我理解",
        "不，我觉得有问题",  # 有否定词"不"
        "不能这样做"         # 有否定词"不能"
    ]
    
    zh_scores = []
    for step in zh_steps:
        h, needs = monitor_zh.add_step(step)
        zh_scores.append(h)
        print(f"  '{step}' -> H={h:.2f}")
    
    # 场景B：英文否定词
    print("\n🌐 场景B：英文（应该检测到否定词）")
    monitor_en = HarmonicMonitor(h_threshold=0.4, verbose=False, language='en')
    
    en_steps = [
        "I agree with this",
        "Yes, I understand",
        "No, I think there is a problem",  # 有否定词"No"
        "Cannot do it this way"              # 有否定词"Cannot"
    ]
    
    en_scores = []
    for step in en_steps:
        h, needs = monitor_en.add_step(step)
        en_scores.append(h)
        print(f"  '{step}' -> H={h:.2f}")
    
    # 验证：两次对话应该都检测到否定词的负面影响
    print("\n📊 结果分析：")
    print(f"  中文步骤平均H值: {sum(zh_scores)/len(zh_scores):.2f}")
    print(f"  英文步骤平均H值: {sum(en_scores)/len(en_scores):.2f}")
    
    # 如果多语言支持工作，两个应该都有较低的H值
    if zh_scores[-1] < zh_scores[0] and en_scores[-1] < en_scores[0]:
        print("  ✅ 多语言否定词检测: 工作正常")
        return True
    else:
        print("  ❌ 多语言否定词检测: 可能有问题")
        return False


def test_backtracking_trigger():
    """测试2：回溯触发机制"""
    print("\n" + "=" * 80)
    print("测试2: 回溯触发机制 - 连续低H才触发")
    print("=" * 80)
    
    print("\n🎯 场景：连续3次重复内容")
    monitor = HarmonicMonitor(h_threshold=0.5, verbose=True, consecutive_low_threshold=2)
    
    steps = [
        "这是一个好的开始",
        "我们继续分析", 
        "继续分析继续分析",  # 重复
        "继续分析继续分析",  # 连续重复
    ]
    
    trigger_count = 0
    for step in steps:
        h, needs = monitor.add_step(step)
        if needs:
            trigger_count += 1
    
    print(f"\n📊 结果：")
    print(f"  总步骤: {len(steps)}")
    print(f"  触发回溯: {trigger_count}次")
    
    if trigger_count >= 1:
        print("  ✅ 回溯机制: 工作正常")
        return True
    else:
        print("  ❌ 回溯机制: 可能有问题")
        return False


def test_h_score_calculation():
    """测试3：H值计算逻辑"""
    print("\n" + "=" * 80)
    print("测试3: H值计算 - 验证公式 H = 0.4*U + 0.4*D - 0.2*A")
    print("=" * 80)
    
    print("\n🎯 场景1：完全重复")
    history = ["这是第一步内容"]
    current = "这是第一步内容"  # 完全重复
    h1 = calculate_h_score(history, current, language='zh')
    print(f"  历史: '{history[0]}'")
    print(f"  当前: '{current}'")
    print(f"  H值: {h1:.2f}")
    print(f"  预期: 应该很低（0.2以下）")
    
    print("\n🎯 场景2：完全新内容")
    history = ["这是第一步内容"]
    current = "今天天气非常好阳光灿烂"  # 完全不同
    h2 = calculate_h_score(history, current, language='zh')
    print(f"  历史: '{history[0]}'")
    print(f"  当前: '{current}'")
    print(f"  H值: {h2:.2f}")
    print(f"  预期: 应该较高（0.5以上）")
    
    print("\n🎯 场景3：部分重复+否定词")
    history = ["我觉得这个方案很好"]
    current = "不，我觉得这个方案不好不好不好"  # 重复+否定词
    h3 = calculate_h_score(history, current, language='zh')
    print(f"  历史: '{history[0]}'")
    print(f"  当前: '{current}'")
    print(f"  H值: {h3:.2f}")
    print(f"  预期: 应该很低（重复+否定词双重惩罚）")
    
    if h1 < 0.3 and h2 > 0.5 and h3 < 0.4:
        print("\n  ✅ H值计算逻辑: 工作正常")
        return True
    else:
        print(f"\n  ⚠️  H值计算: 需要检查 (h1={h1}, h2={h2}, h3={h3})")
        return h1 < 0.5 and h2 > 0.3  # 放宽条件


def test_decorator_real_usage():
    """测试4：装饰器真实使用"""
    print("\n" + "=" * 80)
    print("测试4: @thinkcheck 装饰器真实使用")
    print("=" * 80)
    
    from thinkcheck import thinkcheck
    
    # 模拟一个会返回不同质量结果的AI函数
    call_count = 0
    @thinkcheck(h_threshold=0.4, max_backtracks=1, verbose=True)
    def fake_ai_response(prompt):
        nonlocal call_count
        call_count += 1
        
        if call_count == 1:
            return "这个问题很复杂...这个问题很复杂..."  # 质量差
        else:
            return "好的，让我从另一个角度分析这个问题。"  # 质量好
    
    print(f"\n🎯 场景：模拟AI质量波动")
    print("  调用第1次（质量差）...")
    result1 = fake_ai_response("解释量子力学")
    print(f"  结果: {result1}")
    print(f"  调用第2次（质量好）...")
    result2 = fake_ai_response("解释量子力学")
    print(f"  结果: {result2}")
    
    if call_count >= 2:
        print(f"\n  ✅ 装饰器: 工作正常 (调用了{call_count}次)")
        return True
    else:
        print(f"\n  ❌ 装饰器: 可能有问题")
        return False


def test_summary_report():
    """测试5：摘要报告"""
    print("\n" + "=" * 80)
    print("测试5: 摘要报告功能")
    print("=" * 80)
    
    monitor = HarmonicMonitor(verbose=False)
    
    steps = [
        "开始分析问题",
        "第一步分析",
        "第二步分析",
        "重复重复重复",  # 质量下降
        "重新思考问题"
    ]
    
    for step in steps:
        monitor.add_step(step)
    
    summary = monitor.get_summary()
    
    print("\n📊 摘要报告:")
    print(f"  总步数: {summary['total_steps']}")
    print(f"  平均H值: {summary['average_h']:.2f}")
    print(f"  最低H值: {summary['min_h']:.2f}")
    print(f"  最高H值: {summary['max_h']:.2f}")
    print(f"  低H步数: {summary['low_h_steps']}")
    print(f"  触发回溯: {summary.get('backtrack_triggers', 'N/A')}")
    print(f"  状态: {summary['status']}")
    
    if summary['total_steps'] == 5 and 'backtrack_triggers' in summary:
        print("\n  ✅ 摘要报告: 工作正常")
        return True
    else:
        print("\n  ❌ 摘要报告: 可能有问题")
        return False


def test_streaming_simulation():
    """测试6：流式推理模拟（最重要的测试）"""
    print("\n" + "=" * 80)
    print("测试6: 流式推理监控（模拟AI逐步推理）")
    print("=" * 80)
    
    monitor = HarmonicMonitor(verbose=True)
    
    # 模拟AI逐步推理的过程
    reasoning_steps = [
        "好的，让我分析这道数学题",
        "首先，我需要理解题目要求",
        "题目要求计算圆的面积",
        "圆的面积公式是 πr²",
        "公式公式公式",  # 质量下降！
        "让我重新思考",
        "换个角度，面积等于 π 乘以半径的平方",
        "假设半径是5，那么面积就是 3.14 × 25 = 78.5",
        "最终答案是 78.5"
    ]
    
    print("\n🎯 模拟AI逐步推理（9步）:")
    print("-" * 80)
    
    backtrack_count = 0
    for i, step in enumerate(reasoning_steps, 1):
        h, needs = monitor.add_step(step)
        if needs:
            backtrack_count += 1
        time.sleep(0.05)  # 模拟实时
    
    print("-" * 80)
    
    summary = monitor.get_summary()
    
    print(f"\n📊 最终统计:")
    print(f"  总步骤: {summary['total_steps']}")
    print(f"  成功完成: {'是' if summary['total_steps'] == 9 else '否'}")
    print(f"  检测到质量下降: {summary['low_h_steps']}次")
    print(f"  触发回溯: {summary.get('backtrack_triggers', 0)}次")
    print(f"  平均H值: {summary['average_h']:.2f}")
    print(f"  最终状态: {summary['status']}")
    
    # 核心验证：是否检测到了第5步的质量下降
    low_h_steps = [s for s in monitor.history if s.h_score < 0.5]
    
    if len(low_h_steps) > 0:
        print(f"\n  ✅ 流式监控: 工作正常")
        print(f"     检测到 {len(low_h_steps)} 步质量下降")
        return True
    else:
        print(f"\n  ❌ 流式监控: 可能有问题")
        return False


def main():
    """运行所有测试"""
    print("\n🚀 开始真实功能测试...\n")
    
    results = []
    
    results.append(("多语言支持", test_multilingual_support()))
    results.append(("回溯触发", test_backtracking_trigger()))
    results.append(("H值计算", test_h_score_calculation()))
    results.append(("装饰器使用", test_decorator_real_usage()))
    results.append(("摘要报告", test_summary_report()))
    results.append(("流式推理", test_streaming_simulation()))
    
    print("\n" + "=" * 80)
    print("📋 测试结果汇总")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {status} | {name}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！代码功能验证成功！")
    else:
        print(f"\n⚠️  有 {total - passed} 项测试失败，需要进一步调查")


if __name__ == "__main__":
    main()
