"""
测试四维评估指标
"""

import pytest
from thinkcheck_harmony.metrics import (
    calculate_unity,
    calculate_development,
    calculate_adversarial,
    calculate_harmony
)


# 测试文档
GOOD_DOCUMENT = """
第一章 合同概述
本合同由甲乙双方于2024年1月1日签署。
双方本着平等互利的原则，达成如下协议。

第二章 权利义务
甲方应在规定时间内提供货物。
乙方应在收到货物后7日内支付款项。

第三章 违约责任
如甲方未按时供货，应承担违约金。
如乙方未按时付款，应支付滞纳金。
"""

CONFLICT_DOCUMENT = """
这篇文章非常糟糕，完全没用。
作者什么都不懂，写得很差。
不要浪费时间看这个。
我绝对不会推荐给任何人。
"""

RANDOM_TEXT = """
a b c d e f g h i j k l m n o p q r s t u v w x y z
1 2 3 4 5 6 7 8 9 0
"""


class TestHarmonyMetrics:
    """测试四维评估指标"""
    
    def test_calculate_unity_good_document(self):
        """测试好文档的统一性"""
        score = calculate_unity(GOOD_DOCUMENT)
        assert 0.0 <= score <= 1.0
        assert score > 0.4, "好文档应该有较好的统一性"
    
    def test_calculate_development_good_document(self):
        """测试好文档的发展性"""
        score = calculate_development(GOOD_DOCUMENT)
        assert 0.0 <= score <= 1.0
        assert score > 0.3, "好文档应该有一定的发展性"
    
    def test_calculate_adversarial_good_document(self):
        """测试好文档的对抗性"""
        score = calculate_adversarial(GOOD_DOCUMENT)
        assert 0.0 <= score <= 1.0
        assert score < 0.5, "好文档应该对抗性较低"
    
    def test_calculate_adversarial_conflict_document(self):
        """测试冲突文档的对抗性"""
        score = calculate_adversarial(CONFLICT_DOCUMENT)
        assert 0.0 <= score <= 1.0
        assert score > 0.3, "冲突文档应该对抗性较高"
    
    def test_calculate_harmony_good_document(self):
        """测试好文档的和谐度"""
        result = calculate_harmony(GOOD_DOCUMENT)
        assert "U" in result
        assert "D" in result
        assert "A" in result
        assert "H" in result
        assert 0.0 <= result["U"] <= 1.0
        assert 0.0 <= result["D"] <= 1.0
        assert 0.0 <= result["A"] <= 1.0
        assert 0.0 <= result["H"] <= 1.0
    
    def test_calculate_harmony_conflict_document(self):
        """测试冲突文档的和谐度"""
        good_result = calculate_harmony(GOOD_DOCUMENT)
        conflict_result = calculate_harmony(CONFLICT_DOCUMENT)
        assert good_result["H"] > conflict_result["H"], "好文档的和谐度应该更高"
    
    def test_empty_document(self):
        """测试空文档"""
        score = calculate_unity("")
        assert score == 0.0
        
        result = calculate_harmony("")
        assert result["H"] == 0.0
    
    def test_short_document(self):
        """测试短文档"""
        score = calculate_unity("测试")
        assert 0.0 <= score <= 1.0
    
    def test_scores_range(self):
        """测试所有分数都在0-1范围内"""
        for text in [GOOD_DOCUMENT, CONFLICT_DOCUMENT, RANDOM_TEXT]:
            result = calculate_harmony(text)
            assert 0.0 <= result["U"] <= 1.0
            assert 0.0 <= result["D"] <= 1.0
            assert 0.0 <= result["A"] <= 1.0
            assert 0.0 <= result["H"] <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
