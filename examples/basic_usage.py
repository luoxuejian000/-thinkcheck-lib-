"""
ThinkCheck基本使用示例
展示如何使用@thinkcheck装饰器监控AI推理
"""

import time
import random
import sys
import os

# 添加父目录加入路径，方便直接运行示例
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from thinkcheck import thinkcheck, thinkcheck_retry, HarmonicMonitor

# 示例1：使用装饰器监控函数
@thinkcheck(h_threshold=0.4, max_backtracks=2, verbose=True)
def ai_math_solver(problem: str) -> str:
    """模拟AI解数学题"""
    solutions = {
        "2+2": ["4", "4（二加二等于四）", "答案是4", "4"],
        "圆的面积": ["πr²", "π乘以半径的平方", "πr²", "πr²"],
        "解方程": ["x=5", "解得x=5", "x等于5", "x=5"],
    }
    
    # 模拟不同的回答质量
    key = problem.split()[0] if problem else "2+2"
    options = solutions.get(key, ["我不知道"])
    
    # 添加一些随机性：30%低质量 / 30%重复 / 40%高质量
    r = random.random()
    if r < 0.3:
        return "这个...让我想想..."  # 低质量
    elif r < 0.6:
        return options[0]  # 可能重复
    else:
        return random.choice(options)  # 高质量

# 示例2：使用重试策略
@thinkcheck_retry(h_threshold=0.5, max_backtracks=3, verbose=True)
def ai_code_generator(task: str) -> str:
    """模拟AI生成代码"""
    responses = [
        f"# {task}\ndef solution():\n    pass",
        f"# 实现{task}\nfunction solve() {{}}",
        f"// {task}\nconst handler = () => {{}};",
        f"# {task}\nprint('hello')",  # 可能重复
        f"# {task}\nprint('hello')",  # 重复
    ]
    
    # 模拟AI可能陷入重复
    step = getattr(ai_code_generator, 'call_count', 0)
    ai_code_generator.call_count = step + 1
    
    idx = min(step, len(responses) - 1)
    return responses[idx]

# 示例3：直接使用监控器
def use_monitor_directly():
    """直接使用HarmonicMonitor监控推理过程"""
    print("\n" + "="*60)
    print("示例3：直接使用HarmonicMonitor")
    print("="*60)
    
    monitor = HarmonicMonitor(h_threshold=0.4, verbose=True)
    
    # 模拟推理步骤
    reasoning_steps = [
        "首先，我们需要分析这个问题",
        "这个问题涉及多个方面",
        "我们需要考虑所有可能性",
        "我们需要考虑所有可能性",  # 开始重复
        "换个角度思考这个问题",  # 尝试变化
        "综上所述，解决方案是...",
    ]
    
    for i, step in enumerate(reasoning_steps, 1):
        print(f"\n步骤{i}: {step}")
        h_score, needs_backtrack = monitor.add_step(step)
        
        if needs_backtrack:
            print(f"  → 检测到推理质量下降，建议调整思路")
            # 在实际应用中，这里可以触发回溯逻辑
    
    # 获取摘要
    summary = monitor.get_summary()
    print(f"\n📊 推理摘要:")
    print(f"  总步数: {summary['total_steps']}")
    print(f"  平均H值: {summary['average_h']:.2f}")
    print(f"  最低H值: {summary['min_h']:.2f}")
    print(f"  需要关注步数: {summary['low_h_steps']}")

def main():
    """主函数：运行所有示例"""
    print("="*60)
    print("ThinkCheck 使用示例")
    print("="*60)
    
    # 重置计数器
    if hasattr(ai_code_generator, 'call_count'):
        delattr(ai_code_generator, 'call_count')
    
    # 示例1：数学解题
    print("\n示例1：AI数学解题监控")
    print("-"*40)
    
    problems = ["2+2", "圆的面积公式", "解方程 x+3=8"]
    for problem in problems:
        print(f"\n问题: {problem}")
        result = ai_math_solver(problem)
        print(f"答案: {result}")
        time.sleep(0.5)
    
    # 示例2：代码生成
    print("\n\n示例2：AI代码生成监控（使用重试策略）")
    print("-"*40)
    
    tasks = ["写一个排序函数", "实现用户登录", "创建API端点"]
    for task in tasks:
        print(f"\n任务: {task}")
        result = ai_code_generator(task)
        print(f"生成代码:\n{result}")
        time.sleep(0.5)
    
    # 示例3：直接使用监控器
    use_monitor_directly()
    
    print("\n" + "="*60)
    print("示例运行完成！")
    print("="*60)

if __name__ == "__main__":
    main()