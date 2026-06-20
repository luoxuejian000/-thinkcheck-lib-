"""
ThinkCheck装饰器模块
提供@thinkcheck装饰器，用于监控函数调用
"""

import functools
import time
from typing import Callable, Any
from .core import HarmonicMonitor, calculate_h_score


class BacktrackStrategy:
    """回溯策略基类"""

    def execute(self, func: Callable, args: tuple, kwargs: dict,
                history: list, monitor: HarmonicMonitor) -> Any:
        """执行回溯策略"""
        raise NotImplementedError


class SimpleBacktrack(BacktrackStrategy):
    """简单回溯：返回上一步结果"""

    def execute(self, func: Callable, args: tuple, kwargs: dict,
                history: list, monitor: HarmonicMonitor) -> Any:
        if len(history) >= 2:
            return history[-2]  # 返回上一步
        return None


class RetryBacktrack(BacktrackStrategy):
    """重试回溯：使用修改后的参数重新调用"""

    def __init__(self, max_retries: int = 2):
        self.max_retries = max_retries

    def execute(self, func: Callable, args: tuple, kwargs: dict,
                history: list, monitor: HarmonicMonitor) -> Any:
        previous_results = [str(r) for r in history]
        language = monitor.language if hasattr(monitor, 'language') else 'zh'

        for _ in range(self.max_retries):
            modified_kwargs = kwargs.copy()
            result = func(*args, **modified_kwargs)

            h_score = calculate_h_score(previous_results, str(result),
                                        language=language)
            if h_score >= monitor.h_threshold:
                return result

            time.sleep(0.1)

        return None


def thinkcheck(h_threshold: float = 0.3,
               max_backtracks: int = 2,
               backtrack_strategy: str = "simple",
               verbose: bool = True,
               language: str = 'zh',
               consecutive_low_threshold: int = 1):
    """
    ThinkCheck装饰器工厂函数

    参数：
    h_threshold: 和谐度阈值，低于此值触发回溯
    max_backtracks: 最大回溯次数
    backtrack_strategy: 回溯策略，可选"simple"或"retry"
    verbose: 是否打印详细信息
    language: 语言支持，默认中文
    consecutive_low_threshold: 连续多少次低H才触发回溯（默认1，保持兼容性）
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            monitor = HarmonicMonitor(
                h_threshold=h_threshold,
                verbose=verbose,
                language=language,
                consecutive_low_threshold=consecutive_low_threshold
            )

            if backtrack_strategy == "retry":
                strategy = RetryBacktrack(max_retries=max_backtracks)
            else:
                strategy = SimpleBacktrack()

            backtrack_count = 0
            results_history = []

            while backtrack_count <= max_backtracks:
                result = func(*args, **kwargs)
                results_history.append(result)

                previous_results = [str(r) for r in results_history[:-1]]
                h_score, needs_backtrack = monitor.add_step(
                    str(result),
                    {"attempt": backtrack_count + 1}
                )

                if needs_backtrack and backtrack_count < max_backtracks:
                    backtrack_count += 1

                    if verbose:
                        print(f"触发第{backtrack_count}次回溯（策略：{backtrack_strategy}）")

                    backtrack_result = strategy.execute(
                        func, args, kwargs, results_history, monitor
                    )

                    if backtrack_result is not None:
                        backtrack_h = calculate_h_score(
                            previous_results,
                            str(backtrack_result),
                            language=monitor.language
                        )
                        if backtrack_h >= monitor.h_threshold:
                            results_history.append(backtrack_result)
                            monitor.add_step(
                                str(backtrack_result),
                                {"attempt": backtrack_count + 1, "backtrack_result": True}
                            )
                            return backtrack_result

                        results_history.append(backtrack_result)

                    continue

                return result

            if verbose and backtrack_count >= max_backtracks:
                print(f"达到最大回溯次数({max_backtracks})，返回当前结果")

            return results_history[-1] if results_history else None

        return wrapper
    return decorator


# 快捷装饰器
thinkcheck_simple = thinkcheck


def thinkcheck_retry(**kwargs):
    """使用 retry 策略的 ThinkCheck 装饰器"""
    return thinkcheck(backtrack_strategy="retry", **kwargs)


__all__ = ["thinkcheck", "thinkcheck_simple", "thinkcheck_retry"]
