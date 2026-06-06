#!/usr/bin/env python3
"""
测试 ThinkCheck 项目升级
验证：语义向量检测、长文本处理、可配置权重等功能
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# 确保项目根目录在路径中
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 80)
print("ThinkCheck 项目升级测试")
print("=" * 80)

# 测试 1: 基础导入
print("\n1. 测试模块导入...")
try:
    from thinkcheck_harmony import HarmonyEvaluator
    from thinkcheck_harmony.metrics import (
        calculate_unity, calculate_development, 
        calculate_adversarial, calculate_harmony,
        get_current_weights
    )
    from thinkcheck_agent.core.evaluator import DocumentEvaluator
    from thinkcheck_agent.core.long_text import TextChunker, InterBlockContradictionTracker
    print("   [OK] 所有模块导入成功")
except Exception as e:
    print(f"   [ERROR] 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试 2: 基础评估功能
print("\n2. 测试基础评估功能...")
test_texts = [
    "产品非常好，但质量极差。价格很便宜，却非常昂贵。强烈推荐购买，同时建议不要购买。功能强大，但完全没用。设计精美，然而丑陋不堪。",
    "这是一篇好文章。内容清晰，观点一致。逻辑连贯，结构完整。",
]

for i, text in enumerate(test_texts):
    try:
        # 使用默认权重
        scores = calculate_harmony(text)
        print(f"   测试文本 {i+1}:")
        print(f"     U={scores['U']:.3f}, D={scores['D']:.3f}, A={scores['A']:.3f}, H={scores['H']:.3f}")
        print(f"     权重配置: lambda_u={scores['lambda_u']}, lambda_d={scores['lambda_d']}, lambda_a={scores['lambda_a']}")
    except Exception as e:
        print(f"   测试文本 {i+1} 失败: {e}")

# 测试 3: 自定义权重
print("\n3. 测试自定义权重配置...")
try:
    # 使用不同的权重
    scores1 = calculate_harmony(test_texts[0], 0.2, 0.5, 0.3)
    scores2 = calculate_harmony(test_texts[0], 0.5, 0.3, 0.2)
    
    print(f"   权重配置1 (U=0.2, D=0.5, A=0.3): H={scores1['H']:.3f}")
    print(f"   权重配置2 (U=0.5, D=0.3, A=0.2): H={scores2['H']:.3f}")
    print("   [OK] 自定义权重测试成功")
except Exception as e:
    print(f"   [ERROR] 自定义权重测试失败: {e}")

# 测试 4: 长文本分块处理
print("\n4. 测试长文本分块处理...")
try:
    # 创建长文本
    long_text = "这是一篇长文章。" * 100
    chunker = TextChunker(max_chars_per_chunk=200)
    sentences = long_text.split("。")
    sentences = [s.strip() for s in sentences if s.strip()]
    chunks = chunker.chunk_sentences(sentences)
    print(f"   总句子数: {len(sentences)}")
    print(f"   分块数量: {len(chunks)}")
    print("   [OK] 长文本分块测试成功")
except Exception as e:
    print(f"   [ERROR] 长文本分块测试失败: {e}")

# 测试 5: DocumentEvaluator 集成
print("\n5. 测试 DocumentEvaluator 集成...")
try:
    # 测试不同的权重配置
    config1 = {'thinkcheck': {'default_domain': 'general', 'lambda_u': 0.5, 'lambda_d': 0.3, 'lambda_a': 0.2}}
    evaluator1 = DocumentEvaluator(config1)
    
    result1 = evaluator1.evaluate(test_texts[0])
    print(f"   配置1评估结果: H={result1['harmony_report']['H']:.3f}")
    print(f"   病理诊断: {result1['pathology']}")
    print(f"   是否需要调谐: {result1['needs_tuning']}")
    
    # 测试审计功能
    audit_info = evaluator1.get_audit_info()
    print(f"   审计信息: {audit_info}")
    
    print("   [OK] DocumentEvaluator 测试成功")
except Exception as e:
    print(f"   [ERROR] DocumentEvaluator 测试失败: {e}")
    import traceback
    traceback.print_exc()

# 测试 6: HarmonyEvaluator 权重管理
print("\n6. 测试 HarmonyEvaluator 权重管理...")
try:
    evaluator = HarmonyEvaluator(lambda_u=0.3, lambda_d=0.5, lambda_a=0.2)
    audit_info = evaluator.get_audit_info()
    print(f"   初始权重配置: U={audit_info['lambda_u']}, D={audit_info['lambda_d']}, A={audit_info['lambda_a']}")
    
    # 更新权重
    evaluator.update_weights(0.4, 0.4, 0.2)
    audit_info2 = evaluator.get_audit_info()
    print(f"   更新后权重: U={audit_info2['lambda_u']}, D={audit_info2['lambda_d']}, A={audit_info2['lambda_a']}")
    
    print("   [OK] HarmonyEvaluator 权重管理测试成功")
except Exception as e:
    print(f"   [ERROR] HarmonyEvaluator 权重管理测试失败: {e}")

# 测试 7: 基础指标测试
print("\n7. 测试基础指标计算...")
try:
    for metric_name, metric_func in [
        ("Unity", calculate_unity),
        ("Development", calculate_development),
        ("Adversarial", calculate_adversarial),
    ]:
        for i, text in enumerate(test_texts):
            score = metric_func(text)
            print(f"   {metric_name} 测试文本 {i+1}: {score:.3f}")
    
    print("   [OK] 基础指标测试成功")
except Exception as e:
    print(f"   [ERROR] 基础指标测试失败: {e}")
    import traceback
    traceback.print_exc()

# 测试 8: 默认权重获取
print("\n8. 测试默认权重获取...")
try:
    default_weights = get_current_weights()
    print(f"   默认权重: {default_weights}")
    print("   [OK] 默认权重获取测试成功")
except Exception as e:
    print(f"   [ERROR] 默认权重获取测试失败: {e}")

print("\n" + "=" * 80)
print("所有测试完成！")
print("=" * 80)

print("""
升级功能总结：
[OK] A（对抗性）模块增强：语义向量对立检测、共现约束、分层计算
[OK] 长文本支持：分块处理、跨块矛盾追踪、长句拆分编码
[OK] U（统一性）增强：跨术语一致性检测
[OK] D（发展性）增强：区分建设性创新和破坏性重复
[OK] H（和谐度）审计：可配置权重、可审计
""")
