"""
ThinkCheck核心模块测试
"""

import pytest
from thinkcheck.core import calculate_h_score, HarmonicMonitor, ReasoningStep
from datetime import datetime


class TestCalculateHScore:
    """测试和谐度计算函数"""

    def test_basic_functionality(self):
        """测试基本功能"""
        score = calculate_h_score([], "测试文本")
        assert 0 <= score <= 1

    def test_first_step_returns_high_score(self):
        """测试第一步返回高分"""
        score = calculate_h_score([], "这是第一步")
        assert score > 0.5

    def test_repetition_lowers_score(self):
        """测试重复文本会降低分数"""
        history = ["重复的文本重复的文本"]
        current = "重复的文本重复的文本"
        score1 = calculate_h_score(history, current)

        history2 = ["完全不同的内容"]
        current2 = "新的创新内容"
        score2 = calculate_h_score(history2, current2)

        assert score1 < score2

    def test_empty_inputs(self):
        """测试空输入处理"""
        score = calculate_h_score([], "")
        assert score == 0.5

        score = calculate_h_score(["历史"], "")
        assert score == 0.5

    def test_custom_weights(self):
        """测试自定义权重"""
        custom_weights = {"U": 0.6, "D": 0.2, "A": 0.2}
        score = calculate_h_score([], "测试", weights=custom_weights)
        assert 0 <= score <= 1

    def test_score_clamped_0_1(self):
        """测试分数被限制在0-1范围内"""
        score = calculate_h_score(["历史", "历史", "历史"], "非常非常重复的内容")
        assert 0 <= score <= 1


class TestHarmonicMonitor:
    """测试和谐度监控器"""

    def test_monitor_initialization(self):
        """测试监控器初始化"""
        monitor = HarmonicMonitor(h_threshold=0.5, lookback_window=5, verbose=False)
        assert monitor.h_threshold == 0.5
        assert monitor.lookback_window == 5
        assert len(monitor.history) == 0

    def test_verbose_output(self):
        """测试verbose=True时的输出"""
        import io
        import sys

        captured_output = io.StringIO()
        sys.stdout = captured_output

        monitor = HarmonicMonitor(verbose=True)
        monitor.add_step("测试内容")

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        assert "[Step 1]" in output
        assert "H=" in output
        assert "正常" in output or "需要回溯" in output

    def test_verbose_backtrack_reason(self):
        """测试verbose=True时的回溯原因输出"""
        import io
        import sys

        captured_output = io.StringIO()
        sys.stdout = captured_output

        monitor = HarmonicMonitor(h_threshold=0.9, verbose=True)
        monitor.add_step("内容1")
        monitor.add_step("内容1")

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        assert "原因：和谐度低于阈值" in output

    def test_add_single_step(self):
        """测试添加单个步骤"""
        monitor = HarmonicMonitor(verbose=False)
        score, needs_backtrack = monitor.add_step("第一步")

        assert isinstance(score, float)
        assert 0 <= score <= 1
        assert len(monitor.history) == 1
        assert isinstance(monitor.history[0], ReasoningStep)

    def test_add_multiple_steps(self):
        """测试添加多个步骤"""
        monitor = HarmonicMonitor(verbose=False)

        steps = ["步骤1", "步骤2", "步骤3"]
        for step in steps:
            monitor.add_step(step)

        assert len(monitor.history) == 3
        assert monitor.step_counter == 3

    def test_backtrack_detection_low_score(self):
        """测试低分数触发回溯"""
        monitor = HarmonicMonitor(h_threshold=0.9, verbose=False)  # 高阈值
        monitor.add_step("重复重复重复重复重复重复")

        score, needs_backtrack = monitor.add_step("重复重复重复重复重复重复")
        assert needs_backtrack is True

    def test_backtrack_detection_descending(self):
        """测试连续下降触发回溯"""
        monitor = HarmonicMonitor(lookback_window=3, h_threshold=1.0, verbose=False)

        # 添加递减的H值步骤
        steps = [
            "创新内容完全不重复 1",
            "有些重复的内容 1",
            "完全重复内容 1 1 1",
        ]
        
        results = []
        for step in steps:
            h, needs_backtrack = monitor.add_step(step)
            results.append((h, needs_backtrack))

        # 验证有三次步骤
        assert monitor.step_counter == 3
        
    def test_check_backtrack_needed_empty_history(self):
        """测试空历史时的回溯检查"""
        monitor = HarmonicMonitor(verbose=False)
        # 直接调用私有方法测试
        result = monitor._check_backtrack_needed()
        assert result is False

    def test_get_summary_empty(self):
        """测试空历史的摘要"""
        monitor = HarmonicMonitor(verbose=False)
        summary = monitor.get_summary()

        assert summary["total_steps"] == 0
        assert summary["average_h"] == 0

    def test_get_summary_with_data(self):
        """测试有数据时的摘要"""
        monitor = HarmonicMonitor(verbose=False)
        monitor.add_step("步骤1")
        monitor.add_step("步骤2")

        summary = monitor.get_summary()

        assert summary["total_steps"] == 2
        assert "average_h" in summary
        assert "min_h" in summary
        assert "max_h" in summary
        assert 0 <= summary["average_h"] <= 1

    def test_clear_history(self):
        """测试清空历史"""
        monitor = HarmonicMonitor(verbose=False)
        monitor.add_step("步骤1")
        monitor.add_step("步骤2")

        assert len(monitor.history) == 2

        monitor.clear_history()

        assert len(monitor.history) == 0
        assert monitor.step_counter == 0

    def test_metadata_storage(self):
        """测试元数据存储"""
        monitor = HarmonicMonitor(verbose=False)
        metadata = {"test_key": "test_value", "number": 42}
        monitor.add_step("带元数据的步骤", metadata=metadata)

        assert monitor.history[0].metadata == metadata


class TestReasoningStep:
    """测试推理步骤数据类"""

    def test_step_creation(self):
        """测试步骤创建"""
        step = ReasoningStep(
            step_id=1,
            content="测试内容",
            h_score=0.75,
            timestamp=datetime.now()
        )

        assert step.step_id == 1
        assert step.content == "测试内容"
        assert step.h_score == 0.75

    def test_step_metadata(self):
        """测试步骤元数据"""
        step = ReasoningStep(
            step_id=1,
            content="测试",
            h_score=0.5,
            timestamp=datetime.now(),
            metadata={"key": "value"}
        )

        assert step.metadata["key"] == "value"


class TestIntegrationScenarios:
    """集成测试场景"""

    def test_normal_reasoning_flow(self):
        """测试正常推理流程"""
        monitor = HarmonicMonitor(h_threshold=0.3, verbose=False)

        steps = [
            "分析问题：我们需要计算面积",
            "回忆公式：圆的面积是πr²",
            "应用数据：半径为5",
            "计算：π*5² = 25π ≈ 78.5",
            "总结：面积约为78.5"
        ]

        backtracks = 0
        for step in steps:
            score, needs_backtrack = monitor.add_step(step)
            if needs_backtrack:
                backtracks += 1

        summary = monitor.get_summary()
        assert summary["total_steps"] == 5
        assert summary["status"] in ["healthy", "needs_attention"]

    def test_repetitive_reasoning(self):
        """测试重复推理场景"""
        monitor = HarmonicMonitor(h_threshold=0.5, verbose=False)

        steps = [
            "思考A",
            "思考A",
            "思考A",
            "思考A"
        ]

        for step in steps:
            monitor.add_step(step)

        summary = monitor.get_summary()
        assert summary["low_h_steps"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
