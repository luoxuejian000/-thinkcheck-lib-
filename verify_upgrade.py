#!/usr/bin/env python3
"""
ThinkCheck 项目升级验证脚本
测试A值修复、长文本处理、权重配置等功能
"""

import sys
sys.path.insert(0, '.')

from thinkcheck_agent.core.evaluator import DocumentEvaluator
from thinkcheck_harmony.evaluator import HarmonyEvaluator

# 初始化评估器
evaluator = DocumentEvaluator({'thinkcheck': {}})
harmony = HarmonyEvaluator()

print("=" * 60)
print("ThinkCheck 升级验证报告")
print("=" * 60)

# 测试1：A值核心修复（纯语义矛盾）
print("\n测试1：A值核心修复")
text1 = "功能强大，但完全没用。"
result1 = evaluator.evaluate(text1)
h_report = result1.get('harmony_report', {})
print(f"  文本：{text1}")
print(f"  A值：{h_report.get('A', 'N/A')}")
print(f"  H值：{h_report.get('H', 'N/A')}")
a1 = h_report.get('A', 0)
print(f"  结果：{'PASS' if a1 > 0.2 else 'FAIL'}（预期A > 0.2）")

# 测试2：A值兼容性（否定词矛盾）
print("\n测试2：A值兼容性")
text2 = "产品非常好，但质量极差。"
result2 = evaluator.evaluate(text2)
h_report2 = result2.get('harmony_report', {})
print(f"  文本：{text2}")
print(f"  A值：{h_report2.get('A', 'N/A')}")
a2 = h_report2.get('A', 0)
print(f"  结果：{'PASS' if a2 > 0 else 'FAIL'}（预期A > 0）")

# 测试3：假阳性防御
print("\n测试3：假阳性防御")
text3 = "我喜欢吃苹果。苹果公司发布了新手机。"
result3 = evaluator.evaluate(text3)
h_report3 = result3.get('harmony_report', {})
print(f"  文本：{text3}")
print(f"  A值：{h_report3.get('A', 'N/A')}")
a3 = h_report3.get('A', 0)
print(f"  结果：{'PASS' if a3 < 0.5 else 'WARN'}（预期A不应显著升高）")

# 测试4：长文本多轮对话
print("\n测试4：长文本多轮对话")
text4 = "第一轮：投资回报率很高。第二轮：市场存在波动风险。第三轮：项目流动性较差。第四轮：长期前景看好。第五轮：短期资金链紧张。第六轮：机遇与挑战并存。"
result4 = evaluator.evaluate(text4)
h_report4 = result4.get('harmony_report', {})
print(f"  A值：{h_report4.get('A', 'N/A')}")
print(f"  H值：{h_report4.get('H', 'N/A')}")
a4 = h_report4.get('A', 0)
print(f"  结果：{'PASS' if a4 > 0 else 'CHECK'}（检查跨轮次矛盾是否被检测）")

# 测试5：U跨术语一致性
print("\n测试5：U跨术语一致性")
text5 = "这款手机价格非常实惠。它的拍照效果却不如人意。"
result5 = evaluator.evaluate(text5)
h_report5 = result5.get('harmony_report', {})
print(f"  文本：{text5}")
print(f"  U值：{h_report5.get('U', 'N/A')}")
print(f"  H值：{h_report5.get('H', 'N/A')}")

# 测试6：D真伪创新区分
print("\n测试6：D真伪创新区分")
text6 = "人工智能正在改变世界。AI 技术正在重塑我们的未来。智能算法已经渗透到各行各业。"
result6 = evaluator.evaluate(text6)
h_report6 = result6.get('harmony_report', {})
print(f"  文本：{text6}")
print(f"  D值：{h_report6.get('D', 'N/A')}")
print(f"  H值：{h_report6.get('H', 'N/A')}")

# 测试7：H权重可配置
print("\n测试7：H权重可配置")
print(f"  默认权重：U={harmony.lambda_u}, D={harmony.lambda_d}, A={harmony.lambda_a}")
harmony.update_weights(lambda_a=0.4)
print(f"  修改后权重：U={harmony.lambda_u}, D={harmony.lambda_d}, A={harmony.lambda_a}")
result7 = harmony.evaluate(text1)
# 注意：HarmonyReport 的 to_dict() 才返回字典
scores_dict7 = result7.to_dict()
print(f"  修改权重后H值：{scores_dict7.get('H', 'N/A')}")
harmony.update_weights(lambda_a=0.2)

# 测试8：审计信息
print("\n测试8：审计信息")
audit = harmony.get_audit_info()
print(f"  审计信息：{audit}")

print("\n" + "=" * 60)
print("升级验证完成")
print("=" * 60)
