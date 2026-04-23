"""
2.0法律专业版演示脚本
展示谐振评估器对概念漂移的检测能力，体现压力测试原则
"""
# 直接导入同目录下的模块
from thinkcheck_legal.legal_monitor import StandaloneLegalMonitor

# 正常法律推理（概念使用一致）
normal_text = """
本案涉及善意取得制度。根据《民法典》第三百一十一条，善意取得需满足以下要件：
（一）受让人受让该不动产或者动产时是善意；
（二）以合理的价格转让；
（三）转让的不动产或者动产依照法律规定应当登记的已经登记，不需要登记的已经交付给受让人。
张三在购买时不知李四系无权处分，且支付了市场价，手机已交付。故张三可善意取得该手机。
"""

# 存在概念漂移的推理（"善意"从物权法含义滑向合同法诚实信用）
drift_text = """
本案涉及善意取得制度。根据《民法典》第三百一十一条，善意取得需满足以下要件：
（一）受让人受让该不动产或者动产时是善意；
（二）以合理的价格转让；
（三）转让的不动产或者动产依照法律规定应当登记的已经登记，不需要登记的已经交付给受让人。
张三在购买时不知李四系无权处分，且支付了市场价，手机已交付。故张三可善意取得该手机。
关于善意的判断，我们认为张三在交易中遵循了诚实信用原则，尽到了交易上必要的注意，因此其善意成立。
"""

def main():
    monitor = StandaloneLegalMonitor()
    
    print("=" * 60)
    print("ThinkCheck 2.0 法律专业版 - 概念漂移检测演示")
    print("=" * 60)
    
    # 评估正常文本
    score_normal = monitor.evaluate(normal_text)
    report_normal = monitor.get_report()
    
    print("\n【正常推理评估结果】")
    print(f"和谐度 H = {score_normal:.3f}")
    print(f"U(统一性) = {report_normal['U']:.3f}")
    print(f"D(发展性) = {report_normal['D']:.3f}")
    print(f"A(对抗性) = {report_normal['A']:.3f}")
    if report_normal['drift_warnings']:
        print("⚠️ 漂移警告：")
        for w in report_normal['drift_warnings']:
            print(f"   - 术语 '{w['term']}' 一致性={w['consistency']} (阈值{w['threshold']})")
    else:
        print("✅ 未检测到概念漂移")
    
    # 评估漂移文本
    score_drift = monitor.evaluate(drift_text)
    report_drift = monitor.get_report()
    
    print("\n【概念漂移推理评估结果】")
    print(f"和谐度 H = {score_drift:.3f}")
    print(f"U(统一性) = {report_drift['U']:.3f}")
    print(f"D(发展性) = {report_drift['D']:.3f}")
    print(f"A(对抗性) = {report_drift['A']:.3f}")
    if report_drift['drift_warnings']:
        print("⚠️ 检测到概念漂移：")
        for w in report_drift['drift_warnings']:
            print(f"   - 术语 '{w['term']}' 一致性={w['consistency']} (阈值{w['threshold']})")
            print(f"     出现次数: {w['occurrences']}")
            for i, s in enumerate(w['sentences'][:2], 1):
                print(f"     第{i}处: {s[:50]}...")
    else:
        print("✅ 未检测到概念漂移")
    
    print("\n" + "=" * 60)
    print(f"分数变化: {score_normal:.3f} → {score_drift:.3f} (下降 {score_normal - score_drift:.3f})")
    if score_normal > score_drift:
        print("✓ 评估器成功检测到概念漂移导致的和谐度下降")
        print("✓ 晶脉哲学的关系本体论在代码中得到验证：关注的是术语间关系的一致性")
    else:
        print("✗ 未检测到预期下降，请检查阈值设置或模型选择")
    print("=" * 60)

if __name__ == "__main__":
    main()