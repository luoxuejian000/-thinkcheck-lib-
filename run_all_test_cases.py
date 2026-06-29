from thinkcheck_harmony.evaluator import HarmonyEvaluator

# 定义所有测试案例
test_cases = [
    {
        "name": "案例1：真实商业文本（减资分析报告）",
        "text": "根据搜索结果，我为您详细解释了公司从500万元减资到10万元的原因和具体操作流程。减资的主要原因包括：应对新公司法要求、资本过剩与实际经营需求不匹配、弥补累积亏损、解决出资瑕疵。安徽宿嘉宴餐饮服务有限公司从500万减至10万，很可能是因为原注册资本远超出实际经营需要。减资的具体操作流程分为五个步骤。第一步是内部决策程序，召开股东会形成减少注册资本的决议，必须经代表三分之二以上表决权的股东通过。第二步是编制财务文件，包括资产负债表和财产清单。第三步是债权人通知与公告。第四步是办理变更登记。第五步是特殊规定。对公司合作的影响评估方面，积极方面包括合规经营、务实调整、降低风险。需要注意的方面包括偿债能力降低、商业信誉影响、合同履行能力。建议关注公司减资后的实际经营状况。宿凤亮至少关联四个餐饮经营实体，包括一个有限责任公司、一个分公司、两个个体工商户。公司注册资本十万元，员工两人，属于典型的小微企业。"
    },
    {
        "name": "案例2：纯语义矛盾",
        "text": "功能强大，但完全没用。"
    },
    {
        "name": "案例3：否定词矛盾（兼容性验证）",
        "text": "产品非常好，但质量极差。"
    },
    {
        "name": "案例4：假阳性防御",
        "text": "我喜欢吃苹果。苹果公司发布了新手机。"
    },
    {
        "name": "案例5：多轮对话矛盾",
        "text": "第一轮：这个项目投资回报率很高。第二轮：不过市场存在波动风险。第三轮：项目流动性较差。第四轮：长期前景看好。第五轮：短期资金链紧张。第六轮：机遇与挑战并存。"
    },
    {
        "name": "案例6：U跨术语一致性",
        "text": "这款手机价格非常实惠。它的拍照效果却不如人意。"
    },
    {
        "name": "案例7：D真伪创新区分",
        "text": "人工智能正在改变世界。AI技术正在重塑我们的未来。智能算法已经渗透到各行各业。"
    },
    {
        "name": "案例8：法律文书矛盾",
        "text": "根据公司章程，持有公司51%股权的股东享有控股权。因此，该股东并未持有多数股权。"
    },
    {
        "name": "案例9：长文本多轮对话（10轮投资分析）",
        "text": "第一轮：这个项目的投资回报率非常高，预计年化收益可达15%以上。第二轮：不过需要提醒的是，市场存在波动风险，过去的表现不代表未来。第三轮：从资产配置的角度看，该项目可以作为分散风险的工具。第四轮：但是，该项目的流动性较差，可能需要持有较长时间才能变现。第五轮：综合考虑，对于风险承受能力较强的投资者，可以适当配置，但不宜超过总资产的20%。第六轮：然而，最近的政策变化可能会对该项目产生不利影响，需要密切关注。第七轮：尽管如此，项目的基本面仍然稳健，长期前景看好。第八轮：可是，短期内可能会面临资金链紧张的问题，需要做好充分准备。第九轮：总的来说，这个项目机遇与挑战并存，需要根据市场变化灵活调整策略。第十轮：最后提醒，投资有风险，入市需谨慎，以上分析不构成投资建议。"
    },
    {
        "name": "案例10：正常文本（无矛盾）",
        "text": "人工智能是计算机科学的一个分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。该领域的研究包括机器人、语言识别、图像识别、自然语言处理和专家系统等。"
    }
]

# 创建评估器
evaluator = HarmonyEvaluator()

# 评估每个案例
for i, case in enumerate(test_cases, 1):
    print("=" * 80)
    print(case["name"])
    print("=" * 80)
    
    # 进行评估
    result = evaluator.evaluate(case["text"])
    
    # 输出基本指标
    print(f"U值: {result.scores['U']:.4f}")
    print(f"D值: {result.scores['D']:.4f}")
    print(f"A值: {result.scores['A']:.4f}")
    print(f"H值: {result.scores['H']:.4f}")
    print()
    
    # 病理判定
    print("病理判定:")
    if result.scores['A'] > 0.5:
        verdict = "高对抗性内容，建议仔细检查"
    elif result.scores['H'] < 0.3:
        verdict = "文档和谐度过低，建议进行全面审查"
    elif result.scores['H'] < 0.6:
        verdict = "需调谐"
    else:
        verdict = "合格"
    print(f"  {verdict}")
    print()
    
    # 调谐建议（前3条）
    print("调谐建议:")
    if result.suggestions:
        for j, suggestion in enumerate(result.suggestions[:3], 1):
            print(f"  {j}. {suggestion}")
    else:
        print("  无")
    print()
    
    # A值构成分解
    print("A值构成分解 (edges_detail):")
    a_detail = result.scores.get('A_detail', {})
    print(f"  总边数: {a_detail.get('total_edges', 0)}")
    print(f"  最大权重: {a_detail.get('max_weight', 0):.4f}")
    print(f"  平均权重: {a_detail.get('avg_weight', 0):.4f}")
    print(f"  interpretation: {a_detail.get('interpretation', 'N/A')}")
    print()
    
    # 每条边的详细信息
    edges = a_detail.get('edges', [])
    if edges:
        print("  每条边的详细信息:")
        for j, edge in enumerate(edges, 1):
            print(f"    {j}. 类型: {edge['type']}, 权重: {edge['weight']:.4f}, 详情: {edge['detail']}")
    else:
        print("  无矛盾边")
    
    print()

print("=" * 80)
print("全部案例评估完成")
print("=" * 80)