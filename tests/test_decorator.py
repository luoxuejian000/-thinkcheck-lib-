"""
ThinkCheck装饰器模块测试
"""

import pytest
from thinkcheck.decorator import (
    thinkcheck,
    thinkcheck_simple,
    thinkcheck_retry,
    SimpleBacktrack,
    RetryBacktrack
)
from thinkcheck.core import HarmonicMonitor


class TestDecoratorBasic:
    """测试装饰器基本功能"""

    def test_decorator_apply(self):
        """测试装饰器可以正常应用到函数"""

        @thinkcheck(verbose=False)
        def sample_function():
            return "测试结果"

        result = sample_function()
        assert result == "测试结果"

    def test_decorator_with_arguments(self):
        """测试带参数的装饰器"""

        @thinkcheck(h_threshold=0.5, max_backtracks=3, verbose=False)
        def func_with_args():
            return "成功"

        result = func_with_args()
        assert result == "成功"

    def test_decorator_preserves_metadata(self):
        """测试装饰器保留函数元数据"""

        def original_func(x, y):
            """这是原函数的文档"""
            return x + y

        decorated = thinkcheck(verbose=False)(original_func)

        assert decorated.__name__ == "original_func"
        assert decorated.__doc__ == "这是原函数的文档"

    def test_function_with_parameters(self):
        """测试装饰器可以处理带参数的函数"""

        @thinkcheck(verbose=False)
        def add(a, b):
            return a + b

        result = add(2, 3)
        assert result == 5


class TestThinkcheckRetry:
    """测试重试装饰器"""

    def test_thinkcheck_retry_decorator(self):
        """测试thinkcheck_retry快捷装饰器"""

        @thinkcheck_retry(verbose=False)
        def retry_func():
            return "重试结果"

        result = retry_func()
        assert result == "重试结果"

    def test_retry_strategy_class(self):
        """测试RetryBacktrack策略类"""
        strategy = RetryBacktrack(max_retries=2)
        assert strategy.max_retries == 2


class TestSimpleBacktrack:
    """测试简单回溯策略"""

    def test_simple_backtrack_instantiation(self):
        """测试SimpleBacktrack可以实例化"""
        strategy = SimpleBacktrack()
        assert strategy is not None

    def test_simple_backtrack_with_history(self):
        """测试有历史记录时的简单回溯"""
        strategy = SimpleBacktrack()
        monitor = HarmonicMonitor(verbose=False)

        def dummy_func():
            return "result"

        history = ["first", "second"]
        result = strategy.execute(dummy_func, (), {}, history, monitor)

        assert result == "first"

    def test_simple_backtrack_no_history(self):
        """测试无历史记录时的简单回溯"""
        strategy = SimpleBacktrack()
        monitor = HarmonicMonitor(verbose=False)

        def dummy_func():
            return "result"

        history = []
        result = strategy.execute(dummy_func, (), {}, history, monitor)

        assert result is None


class TestBacktrackStrategies:
    """测试回溯策略"""

    def test_backtrack_strategy_selection(self):
        """测试可以选择不同的回溯策略"""

        @thinkcheck(backtrack_strategy="simple", verbose=False)
        def simple_func():
            return "simple"

        @thinkcheck(backtrack_strategy="retry", verbose=False)
        def retry_func():
            return "retry"

        assert simple_func() == "simple"
        assert retry_func() == "retry"


class TestThinkcheckSimple:
    """测试thinkcheck_simple快捷装饰器"""

    def test_thinkcheck_simple(self):
        """测试thinkcheck_simple"""

        @thinkcheck_simple(verbose=False)
        def simple_decorated():
            return "test"

        result = simple_decorated()
        assert result == "test"


class TestIntegrationDecoratorScenarios:
    """装饰器集成测试场景"""

    def test_multiple_calls(self):
        """测试多次调用被装饰的函数"""
        call_count = 0

        @thinkcheck(verbose=False)
        def counted_func():
            nonlocal call_count
            call_count += 1
            return f"call_{call_count}"

        results = [counted_func() for _ in range(3)]

        assert results == ["call_1", "call_2", "call_3"]
        assert call_count == 3

    def test_different_return_types(self):
        """测试不同的返回类型"""

        @thinkcheck(verbose=False)
        def return_string():
            return "hello"

        @thinkcheck(verbose=False)
        def return_number():
            return 42

        @thinkcheck(verbose=False)
        def return_list():
            return [1, 2, 3]

        assert return_string() == "hello"
        assert return_number() == 42
        assert return_list() == [1, 2, 3]

    def test_complex_parameters(self):
        """测试复杂的参数"""

        @thinkcheck(verbose=False)
        def process_data(data, options=None):
            options = options or {}
            return {"data": data, "options": options}

        result = process_data(
            {"key": "value"},
            options={"option1": True, "option2": "test"}
        )

        assert result["data"]["key"] == "value"
        assert result["options"]["option1"] is True


class TestRetryBacktrackExecute:
    """测试RetryBacktrack的execute方法"""

    def test_retry_backtrack_execute_with_history_low_h(self):
        """测试有历史记录但H分数低的情况"""
        strategy = RetryBacktrack(max_retries=2)
        monitor = HarmonicMonitor(h_threshold=0.9, verbose=False)
        
        call_count = 0
        def dummy_func():
            nonlocal call_count
            call_count += 1
            return "重复内容"
        
        history = ["重复内容"]
        # 这里我们需要模拟time.sleep以加快测试
        import unittest.mock
        with unittest.mock.patch('time.sleep') as mock_sleep:
            result = strategy.execute(dummy_func, (), {}, history, monitor)
        
        # H分数低时会尝试所有重试
        assert call_count == 2
        assert result is None
        assert mock_sleep.call_count == 2

    def test_retry_backtrack_execute_no_history(self):
        """测试无历史记录时的重试回溯"""
        strategy = RetryBacktrack(max_retries=2)
        monitor = HarmonicMonitor(verbose=False)

        call_count = 0
        def dummy_func():
            nonlocal call_count
            call_count += 1
            return f"结果_{call_count}"

        history = []
        import unittest.mock
        with unittest.mock.patch('time.sleep') as mock_sleep:
            result = strategy.execute(dummy_func, (), {}, history, monitor)

        # 无历史时，第一次结果的新颖性/探索性为最高，应直接返回
        assert result == "结果_1"
        assert call_count == 1
        assert mock_sleep.call_count == 0

class TestBacktrackTriggerInDecorator:
    """测试装饰器中的回溯触发"""

    def test_decorator_verbose_backtrack_message(self):
        """测试装饰器verbose时的回溯消息"""
        import io
        import sys

        captured_output = io.StringIO()
        sys.stdout = captured_output

        @thinkcheck(h_threshold=0.9, max_backtracks=1, verbose=True)
        def func_with_possible_backtrack():
            return "重复内容"

        result = func_with_possible_backtrack()

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        assert "触发第1次回溯" in output or "达到最大回溯次数" in output

    def test_decorator_max_backtracks_reached(self):
        """测试达到最大回溯次数的情况"""
        import io
        import sys

        captured_output = io.StringIO()
        sys.stdout = captured_output

        # 设置高阈值确保需要回溯
        @thinkcheck(h_threshold=0.9, max_backtracks=2, verbose=True)
        def func_always_low_quality():
            return "低质量内容"

        result = func_always_low_quality()

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        # 验证返回了最后一次结果
        assert result is not None

class TestBacktrackStrategyBase:
    """测试回溯策略基类"""

    def test_backtrack_strategy_base_class(self):
        """测试BacktrackStrategy基类"""
        from thinkcheck.decorator import BacktrackStrategy
        
        class TestStrategy(BacktrackStrategy):
            def execute(self, func, args, kwargs, history, monitor):
                return "test_result"
        
        strategy = TestStrategy()
        monitor = HarmonicMonitor(verbose=False)
        
        def dummy():
            return "dummy"
        
        result = strategy.execute(dummy, (), {}, [], monitor)
        assert result == "test_result"

class TestEdgeCases:
    """测试边界情况"""

    def test_empty_function(self):
        """测试空函数"""

        @thinkcheck(verbose=False)
        def empty_func():
            pass

        result = empty_func()
        assert result is None

    def test_function_raising_exception(self):
        """测试会抛出异常的函数"""

        @thinkcheck(verbose=False)
        def error_func():
            raise ValueError("测试错误")

        with pytest.raises(ValueError):
            error_func()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
