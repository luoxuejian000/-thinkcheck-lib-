
"""
ThinkCheck 改进版本示例
展示如何正确集成和使用
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from thinkcheck.improved import (
    ImprovedHarmonicMonitor,
    ImprovedRetryStrategy,
    monitor_streaming_reasoning
)
import time


def example_1_multilingual_support():
    """示例1: 多语言支持"""
    print("=" * 70)
    print("示例1: 多语言支持 - 中英文都能工作")
    print("=" * 70)
    
    # 中文测试
    print("\n--- 中文测试 ---")
    monitor_zh = ImprovedHarmonicMonitor(language='zh', verbose=True)
    steps_zh = [
        "我来分析这个数学问题",
        "首先，我们理解题目要求",
        "不，等等，我刚才的思路有问题",
        "让我换个角度重新考虑"
    ]
    for step in steps_zh:
        monitor_zh.add_step(step)
        time.sleep(0.1)
    
    # 英文测试
    print("\n--- 英文测试 ---")
    monitor_en = ImprovedHarmonicMonitor(language='en', verbose=True)
    steps_en = [
        "Let me analyze this math problem",
        "First, let's understand what's being asked",
        "No, wait, my previous approach was wrong",
        "Let me reconsider from a different angle"
    ]
    for step in steps_en:
        monitor_en.add_step(step)
        time.sleep(0.1)
    
    print(f"\n✅ 中英文都能正确处理否定词！")


def example_2_streaming_monitoring():
    """示例2: 流式推理监控 - 真正能看到推理过程！"""
    print("\n" + "=" * 70)
    print("示例2: 流式推理监控 - 这才是正确的集成方式")
    print("=" * 70)
    
    # 模拟AI的逐步推理生成器
    def fake_reasoning_generator():
        """模拟AI一步步推理的过程"""
        steps = [
            "好的，让我来解决这个问题...",
            "首先，我需要理解问题：求圆的面积",
            "圆的面积公式是...嗯...",
            "我想想...我想想...我想想...",  # 开始重复
            "圆的面积等于...让我再想想...",
            "哦对了！面积公式是πr²",
            "假设半径r=5，那么面积就是π×5²=25π≈78.5",
            "所以最终答案是约78.5"
        ]
        
        for i, step in enumerate(steps):
            print(f"  [AI 推理] {step}")
            time.sleep(0.2)
            yield step
    
    monitor = ImprovedHarmonicMonitor(verbose=True)
    
    print("\n开始监控推理过程...")
    final_answer, details = monitor_streaming_reasoning(fake_reasoning_generator, monitor)
    
    print(f"\n📊 推理摘要:")
    print(f"  总步数: {details['summary']['total_steps']}")
    print(f"  平均H值: {details['summary']['average_h']:.2f}")
    print(f"  触发回溯: {details['summary']['backtrack_triggers']}次")
    print(f"  最终答案: {final_answer}")


def example_3_improved_backtracking():
    """示例3: 改进的回溯策略"""
    print("\n" + "=" * 70)
    print("示例3: 改进的回溯策略 - 真正有意义的重试")
    print("=" * 70)
    
    # 模拟一个AI函数
    def fake_ai_function(prompt: str, temperature: float = 0.7, attempt: int = 0, **kwargs):
        """模拟AI函数，接受temperature等参数"""
        print(f"\n🤖 调用AI (attempt={attempt+1}, temp={temperature:.2f})")
        
        if attempt == 0:
            return "这个问题...让我想想...这个问题..."
        elif attempt == 1:
            return "好的，换个角度，这个问题涉及数学计算..."
        else:
            return "让我重新梳理：首先我们需要确定公式，然后代入数值计算。"
    
    strategy = ImprovedRetryStrategy(max_retries=3)
    
    original_prompt = "如何计算圆的面积？"
    print(f"\n原始提示: {original_prompt}")
    
    for attempt in range(strategy.max_retries):
        result, info = strategy.execute(
            fake_ai_function,
            original_prompt,
            attempt
        )
        
        print(f"  结果: {result}")
        print(f"  提示修改: {'是' if info['prompt_was_modified'] else '否'}")
        
        # 检查质量（实际应该用h_score）
        if "重新梳理" in result or "公式" in result:
            print(f"✅ 第{attempt+1}次尝试成功！")
            break
    
    print(f"\n💡  改进点：每次重试都用不同的temperature和修改后的提示词！")


def example_4_comparison():
    """示例4: 改进前后对比"""
    print("\n" + "=" * 70)
    print("示例4: 改进前后对比")
    print("=" * 70)
    
    print("\n📋 主要改进汇总:")
    
    comparisons = [
        ("语言支持", "仅中文", "支持中、英、日、韩等"),
        ("回溯策略", "原样重试/返回缓存", "调整temperature+修改提示"),
        ("集成方式", "装饰器（只看结果）", "流式监控（看推理过程）"),
        ("触发机制", "单次低H就触发", "连续低H或下降趋势才触发"),
        ("否定词检测", "硬编码中文", "多语言配置"),
        ("分词", "简单正则", "语言特定处理")
    ]
    
    for feature, old, new in comparisons:
        print(f"\n  {feature}:")
        print(f"    旧版: ❌ {old}")
        print(f"    新版: ✅ {new}")


def main():
    """运行所有示例"""
    print("🚀 ThinkCheck 改进版本示例\n")
    
    example_1_multilingual_support()
    example_2_streaming_monitoring()
    example_3_improved_backtracking()
    example_4_comparison()
    
    print("\n" + "=" * 70)
    print("✨ 所有示例完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()
