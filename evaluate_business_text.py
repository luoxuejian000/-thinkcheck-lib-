from thinkcheck_harmony.evaluator import HarmonyEvaluator

text = """根据搜索结果，我为您详细解释了公司从500万元减资到10万元的原因和具体操作流程。

减资的主要原因包括：应对新公司法要求、资本过剩与实际经营需求不匹配、弥补累积亏损、解决出资瑕疵。安徽宿嘉宴餐饮服务有限公司从500万减至10万，很可能是因为原注册资本远超出实际经营需要。

减资的具体操作流程分为五个步骤。第一步是内部决策程序，召开股东会形成减少注册资本的决议，必须经代表三分之二以上表决权的股东通过。第二步是编制财务文件，包括资产负债表和财产清单。第三步是债权人通知与公告，自股东会作出减资决议之日起十日内通知所有已知债权人。第四步是办理变更登记，向公司登记机关申请办理变更登记。第五步是特殊规定，公司减少注册资本应当按照股东出资比例相应减少出资额。

对公司合作的影响评估方面，积极方面包括合规经营、务实调整、降低风险。需要注意的方面包括偿债能力降低、商业信誉影响、合同履行能力。建议关注公司减资后的实际经营状况，核实公司是否已妥善处理所有债务。

宿凤亮至少关联四个餐饮经营实体，包括一个有限责任公司、一个分公司、两个个体工商户。这些企业都集中在合肥市，主要从事餐饮服务、餐饮管理、快餐盒饭等业务。公司注册资本十万元，员工两人，属于典型的小微企业。门店数量至少有三个正式注册的实体，另外可能还有二至四个未独立注册的门店。公司自2018年成立以来持续经营，虽然规模不大但经营状态正常，无公开风险信息。"""

evaluator = HarmonyEvaluator()
result = evaluator.evaluate(text)

print('='*70)
print('ThinkCheck 四维评估报告')
print('='*70)
print(f"1. U（统一性）值: {result.scores['U']:.4f}")
print(f"2. D（发展性）值: {result.scores['D']:.4f}")
print(f"3. A（对抗性）值: {result.scores['A']:.4f}")
print(f"4. H（和谐度）值: {result.scores['H']:.4f}")
print()

print('5. 病理判定:')
if result.scores['A'] > 0.5:
    print('   判定：高对抗性内容，建议仔细检查')
elif result.scores['H'] < 0.3:
    print('   判定：文档和谐度过低，建议进行全面审查')
elif result.scores['H'] < 0.6:
    print('   判定：需调谐')
else:
    print('   判定：合格')

print()
print('6. 调谐建议:')
for i, suggestion in enumerate(result.suggestions, 1):
    print(f'   {i}. {suggestion}')

print()
print('7. A值的构成分解:')
a_detail = result.scores.get('A_detail', {})
print(f"   矛盾边总数: {a_detail.get('total_edges', 0)}")
print(f"   最大权重: {a_detail.get('max_weight', 0):.4f}")
print(f"   平均权重: {a_detail.get('avg_weight', 0):.4f}")
print(f"   interpretation: {a_detail.get('interpretation', 'N/A')}")
print()
print('   每条边的详细信息:')
for i, edge in enumerate(a_detail.get('edges', []), 1):
    print(f"   {i}. 类型: {edge['type']}, 权重: {edge['weight']:.4f}, 详情: {edge['detail']}")