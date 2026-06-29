"""
ThinkCheck Agent 真实示例
演示完整的文档评估和修复流程
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger

from config import settings
from thinkcheck_agent.core.orchestration import Orchestrator, TaskContext
from thinkcheck_agent.core.evaluator import DocumentEvaluator
from thinkcheck_agent.core.actuator import HarmonyActuator


# 示例文档
SAMPLE_DOCUMENT = """
合同协议
甲方：张三
乙方：李四

第一条 服务内容
甲方应该为乙方提供服务，但乙方也不能什么都不做。

第二条 付款方式
乙方应该按时付款，但如果有困难可以拖延。

第三条 争议解决
如有争议，双方协商解决，协商不成可以起诉也可以仲裁。
"""


async def main():
    print("="*80)
    print("ThinkCheck Agent - 真实示例")
    print("="*80)
    
    # 1. 初始化组件
    print("\n[1/5] 初始化组件...")
    evaluator = DocumentEvaluator({})
    actuator = HarmonyActuator({})
    orchestrator = Orchestrator(evaluator, actuator, {}, enable_ochr=True)
    
    # 2. 显示原始文档
    print("\n[2/5] 原始文档:")
    print("-"*80)
    print(SAMPLE_DOCUMENT)
    print("-"*80)
    
    # 3. 创建上下文
    print("\n[3/5] 创建任务上下文...")
    context = TaskContext(
        file_path="sample_contract.txt",
        original_content=SAMPLE_DOCUMENT,
        workflow_type="legal_review",
        config={}
    )
    
    # 4. 执行协调
    print("\n[4/5] 执行评估和修复...")
    print("这可能需要一些时间...")
    
    result = await orchestrator.orchestrate(context, auto_fix=True)
    
    # 5. 显示结果
    print("\n[5/5] 处理结果:")
    print("="*80)
    
    print(f"\n状态: {result.get('status', 'unknown')}")
    
    if result.get('initial_scores'):
        s = result['initial_scores']
        print(f"\n初始分数:")
        print(f"  统一性 (U): {s['U']:.3f}")
        print(f"  发展性 (D): {s['D']:.3f}")
        print(f"  对抗性 (A): {s['A']:.3f}")
        print(f"  和谐度 (H): {s['H']:.3f}")
    
    if result.get('final_scores'):
        s = result['final_scores']
        print(f"\n最终分数:")
        print(f"  统一性 (U): {s['U']:.3f}")
        print(f"  发展性 (D): {s['D']:.3f}")
        print(f"  对抗性 (A): {s['A']:.3f}")
        print(f"  和谐度 (H): {s['H']:.3f}")
        print(f"\n和谐度改进: {result.get('improvement', 0):+.3f}")
    
    if result.get('suggestions'):
        print(f"\n建议:")
        for i, suggestion in enumerate(result['suggestions'], 1):
            print(f"  {i}. {suggestion}")
    
    if result.get('warnings'):
        print(f"\n警告:")
        for i, warning in enumerate(result['warnings'], 1):
            print(f"  {i}. {warning}")
    
    if result.get('fix_strategy'):
        print(f"\n修复策略: {result['fix_strategy']}")
    
    if result.get('fixed_content'):
        print(f"\n修复后的文档:")
        print("-"*80)
        print(result['fixed_content'])
        print("-"*80)
        
        # 保存修复后的文档
        output_path = project_root / "output_fixed.txt"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result['fixed_content'])
        print(f"\n修复后的文档已保存到: {output_path}")
    
    if result.get('error'):
        print(f"\n错误: {result['error']}")
    
    # 会话摘要
    summary = orchestrator.get_session_summary()
    if summary:
        print(f"\n会话摘要:")
        print(f"  总评估数: {summary.get('total_evaluations', 0)}")
        print(f"  总修复数: {summary.get('total_repairs', 0)}")
    
    print("\n" + "="*80)
    print("示例完成!")
    print("="*80)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n用户中断")
    except Exception as e:
        logger.exception(f"运行示例失败: {e}")
