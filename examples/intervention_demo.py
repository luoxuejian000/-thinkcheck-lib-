'''矛盾捕获器演示'''
import sys
sys.path.insert(0, '..')
from thinkcheck_harmony import HarmonyEvaluator

evaluator = HarmonyEvaluator(domain="legal", enable_suggestions=True)

text = """
本案涉及善意取得制度。根据《民法典》第三百一十一条，善意取得需满足善意、合理价格、交付三要件。
张三在购买时不知李四系无权处分，且支付了市场价，手机已交付。故张三可善意取得该手机。
但是，我们必须指出，关于善意的判断存在重大争议。然而，张三的行为是否符合诚实信用原则，有待商榷。
"""

report = evaluator.evaluate(text)

print("=" * 60)
print("ThinkCheck 3.0 评估报告（含矛盾捕获器建议）")
print("=" * 60)
print(f"和谐度 H = {report.H:.3f}")
print(f"U = {report.U:.3f}, D = {report.D:.3f}, A = {report.A:.3f}")
print("\n📊 漂移警告:")
for w in report.drift_warnings:
    print(f"  - {w['term']}: 一致性 {w['consistency']:.3f}")

print("\n💡 矛盾捕获器调谐建议:")
if report.suggestions:
    for i, s in enumerate(report.suggestions, 1):
        print(f"{i}. {s}")
else:
    print("  无需额外干预，系统处于健康谐振态。")
