import sys
sys.path.insert(0, '.')

from thinkcheck_agent.core.evaluator import DocumentEvaluator
from thinkcheck_harmony.evaluator import HarmonyEvaluator

config = {
    'thinkcheck': {
        'default_domain': 'general',
        'harmony_threshold': 0.7,
        'adversarial_threshold': 0.3,
        'lambda_u': 0.4,
        'lambda_d': 0.4,
        'lambda_a': 0.2,
        'enable_suggestions': True
    }
}

evaluator = DocumentEvaluator(config)
harmony = HarmonyEvaluator()

print("=" * 70)
print("ThinkCheck Demo 案例测试报告")
print("=" * 70)

# 案例1：纯语义矛盾检测（核心修复验证）
print("\n" + "=" * 70)
print("案例1：纯语义矛盾检测（核心修复验证）")
print("=" * 70)
text1 = "功能强大，但完全没用。"
result1 = evaluator.evaluate(text1)
h_report1 = result1.get('harmony_report', {})
print(f"文本：{text1}")
print(f"U值：{h_report1.get('U', 'N/A')}")
print(f"D值：{h_report1.get('D', 'N/A')}")
print(f"A值：{h_report1.get('A', 'N/A')}")
print(f"H值：{h_report1.get('H', 'N/A')}")
print(f"判定：{result1.get('verdict', 'N/A')}")
a1 = h_report1.get('A', 0)
expected_pass = "PASS" if a1 > 0.2 else "FAIL"
print(f"预期：A > 0.2，实际：{a1:.3f} [{expected_pass}]")

# 案例2：否定词矛盾检测（兼容性验证）
print("\n" + "=" * 70)
print("案例2：否定词矛盾检测（兼容性验证）")
print("=" * 70)
text2 = "产品非常好，但质量极差。"
result2 = evaluator.evaluate(text2)
h_report2 = result2.get('harmony_report', {})
print(f"文本：{text2}")
print(f"U值：{h_report2.get('U', 'N/A')}")
print(f"D值：{h_report2.get('D', 'N/A')}")
print(f"A值：{h_report2.get('A', 'N/A')}")
print(f"H值：{h_report2.get('H', 'N/A')}")
print(f"判定：{result2.get('verdict', 'N/A')}")
a2 = h_report2.get('A', 0)
expected_pass = "PASS" if a2 > 0 else "FAIL"
print(f"预期：A > 0，实际：{a2:.3f} [{expected_pass}]")

# 案例3：假阳性防御
print("\n" + "=" * 70)
print("案例3：假阳性防御")
print("=" * 70)
text3 = "我喜欢吃苹果。苹果公司发布了新手机。"
result3 = evaluator.evaluate(text3)
h_report3 = result3.get('harmony_report', {})
print(f"文本：{text3}")
print(f"U值：{h_report3.get('U', 'N/A')}")
print(f"D值：{h_report3.get('D', 'N/A')}")
print(f"A值：{h_report3.get('A', 'N/A')}")
print(f"H值：{h_report3.get('H', 'N/A')}")
print(f"判定：{result3.get('verdict', 'N/A')}")
a3 = h_report3.get('A', 0)
expected_pass = "PASS" if a3 < 0.1 else "WARN"
print(f"预期：A值不应显著升高，实际：{a3:.3f} [{expected_pass}]")

# 案例4：多轮对话矛盾
print("\n" + "=" * 70)
print("案例4：多轮对话矛盾")
print("=" * 70)
text4 = "第一轮：这个项目投资回报率很高。第二轮：不过市场存在波动风险。第三轮：项目流动性较差。第四轮：长期前景看好。第五轮：短期资金链紧张。"
result4 = evaluator.evaluate(text4)
h_report4 = result4.get('harmony_report', {})
print(f"文本：{text4[:50]}...")
print(f"文本长度：{len(text4)} 字符")
print(f"U值：{h_report4.get('U', 'N/A')}")
print(f"D值：{h_report4.get('D', 'N/A')}")
print(f"A值：{h_report4.get('A', 'N/A')}")
print(f"H值：{h_report4.get('H', 'N/A')}")
print(f"判定：{result4.get('verdict', 'N/A')}")
a4 = h_report4.get('A', 0)
expected_pass = "PASS" if a4 > 0 else "CHECK"
print(f"预期：A > 0（反映跨轮次对立），实际：{a4:.3f} [{expected_pass}]")

# 案例5：U跨术语一致性
print("\n" + "=" * 70)
print("案例5：U跨术语一致性")
print("=" * 70)
text5 = "这款手机价格非常实惠。它的拍照效果却不如人意。"
result5 = evaluator.evaluate(text5)
h_report5 = result5.get('harmony_report', {})
print(f"文本：{text5}")
print(f"U值：{h_report5.get('U', 'N/A')}")
print(f"D值：{h_report5.get('D', 'N/A')}")
print(f"A值：{h_report5.get('A', 'N/A')}")
print(f"H值：{h_report5.get('H', 'N/A')}")
print(f"判定：{result5.get('verdict', 'N/A')}")
u5 = h_report5.get('U', 0)
print(f"说明：U值({u5:.3f})反映'手机价格'与'拍照效果'两个话题间的语义距离")

# 案例6：D真伪创新区分
print("\n" + "=" * 70)
print("案例6：D真伪创新区分")
print("=" * 70)
text6 = "人工智能正在改变世界。AI 技术正在重塑我们的未来。智能算法已经渗透到各行各业。"
result6 = evaluator.evaluate(text6)
h_report6 = result6.get('harmony_report', {})
print(f"文本：{text6}")
print(f"U值：{h_report6.get('U', 'N/A')}")
print(f"D值：{h_report6.get('D', 'N/A')}")
print(f"A值：{h_report6.get('A', 'N/A')}")
print(f"H值：{h_report6.get('H', 'N/A')}")
print(f"判定：{result6.get('verdict', 'N/A')}")
d6 = h_report6.get('D', 0)
print(f"说明：D值({d6:.3f})不过高，因为三句话在重复同一观点（伪创新）")

# 案例7：H权重可配置
print("\n" + "=" * 70)
print("案例7：H权重可配置")
print("=" * 70)
text7 = "功能强大，但完全没用。"
print(f"文本：{text7}")
print(f"默认权重：λ_U={harmony.lambda_u}, λ_D={harmony.lambda_d}, λ_A={harmony.lambda_a}")
result7_default = harmony.evaluate(text7)
if hasattr(result7_default, 'scores'):
    h7_default = result7_default.scores.get('H', 0)
else:
    h7_default = result7_default.get('harmony_report', {}).get('H', 0)
print(f"默认权重下H值：{h7_default:.4f}")

harmony.update_weights(lambda_a=0.4)
print(f"修改后权重：λ_U={harmony.lambda_u}, λ_D={harmony.lambda_d}, λ_A={harmony.lambda_a}")
result7_modified = harmony.evaluate(text7)
if hasattr(result7_modified, 'scores'):
    h7_modified = result7_modified.scores.get('H', 0)
else:
    h7_modified = result7_modified.get('harmony_report', {}).get('H', 0)
print(f"修改权重后H值：{h7_modified:.4f}")

harmony.update_weights(lambda_a=0.2)

expected_pass = "PASS" if h7_modified < h7_default else "FAIL"
print(f"预期：H值随A权重增加而降低，实际变化：{h7_default:.4f} → {h7_modified:.4f} [{expected_pass}]")

# 案例8：长文本（完整多轮对话）
print("\n" + "=" * 70)
print("案例8：长文本（完整多轮对话）")
print("=" * 70)
text8 = """第一轮：这个项目的投资回报率非常高，预计年化收益可达15%以上。
第二轮：不过需要提醒的是，市场存在波动风险，过去的表现不代表未来。
第三轮：从资产配置的角度看，该项目可以作为分散风险的工具。
第四轮：但是，该项目的流动性较差，可能需要持有较长时间才能变现。
第五轮：综合考虑，对于风险承受能力较强的投资者，可以适当配置，但不宜超过总资产的20%。
第六轮：然而，最近的政策变化可能会对该项目产生不利影响，需要密切关注。
第七轮：尽管如此，项目的基本面仍然稳健，长期前景看好。
第八轮：可是，短期内可能会面临资金链紧张的问题，需要做好充分准备。
第九轮：总的来说，这个项目机遇与挑战并存，需要根据市场变化灵活调整策略。
第十轮：最后提醒，投资有风险，入市需谨慎，以上分析不构成投资建议。"""
result8 = evaluator.evaluate(text8)
h_report8 = result8.get('harmony_report', {})
print(f"文本轮数：10轮")
print(f"文本长度：{len(text8)} 字符")
print(f"U值：{h_report8.get('U', 'N/A')}")
print(f"D值：{h_report8.get('D', 'N/A')}")
print(f"A值：{h_report8.get('A', 'N/A')}")
print(f"H值：{h_report8.get('H', 'N/A')}")
print(f"判定：{result8.get('verdict', 'N/A')}")
a8 = h_report8.get('A', 0)
expected_pass = "PASS" if a8 > 0 else "CHECK"
print(f"预期：A > 0（反映整体矛盾张力），实际：{a8:.3f} [{expected_pass}]")

print("\n" + "=" * 70)
print("Demo案例测试完成")
print("=" * 70)
