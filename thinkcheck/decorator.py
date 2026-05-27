"""
ThinkCheck装饰器模块
提供@thinkcheck装饰器，用于监控函数调用
"""

import functools
import time
from typing import Callable, Any, Optional, Dict
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
        self.attempt = 0  # 记录尝试次数
    
    def execute(self, func: Callable, args: tuple, kwargs: dict, 
                history: list, monitor: HarmonicMonitor) -> Any:
        for attempt in range(self.max_retries):
            self.attempt = attempt
            
            # 修改参数或添加提示（这里是基础版）
            # 如果有温度等参数，可以在这修改
            modified_kwargs = kwargs.copy()
            
            # 调用函数
            result = func(*args, **modified_kwargs)
            
            # 计算新结果的H值（传递monitor的language）
            if history:
                h_score = calculate_h_score([history[-1]], result, 
                                           language=monitor.language if hasattr(monitor, 'language') else 'zh')
                if h_score >= monitor.h_threshold:
                    return result
            
            time.sleep(0.1)  # 短暂延迟
        
        return None

def thinkcheck(h_threshold: float = 0.3, 
               max_backtracks: int = 2,
               backtrack_strategy: str = "simple",
               verbose: bool = True,
               language: str = 'zh',  # 新增：语言支持
               consecutive_low_threshold: int = 1):  # 新增：连续阈值
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
            # 初始化监控器（传递新参数）
            monitor = HarmonicMonitor(
                h_threshold=h_threshold,
                verbose=verbose,
                language=language,
                consecutive_low_threshold=consecutive_low_threshold
            )
            
            # 选择回溯策略
            if backtrack_strategy == "retry":
                strategy = RetryBacktrack(max_retries=max_backtracks)
            else:
                strategy = SimpleBacktrack()
            
            backtrack_count = 0
            results_history = []
            
            while backtrack_count <= max_backtracks:
                # 执行被装饰的函数
                result = func(*args, **kwargs)
                results_history.append(result)
                
                # 计算和谐度
                previous_results = [str(r) for r in results_history[:-1]]
                h_score, needs_backtrack = monitor.add_step(
                    str(result),
                    {"attempt": backtrack_count + 1}
                )
                
                # 检查是否需要回溯
                if needs_backtrack and backtrack_count < max_backtracks:
                    backtrack_count += 1
                    
                    if verbose:
                        print(f"触发第{backtrack_count}次回溯（策略：{backtrack_strategy}）")
                    
                    # 执行回溯
                    backtrack_result = strategy.execute(
                        func, args, kwargs, results_history, monitor
                    )
                    
                    if backtrack_result is not None:
                        results_history.append(backtrack_result)
                        return backtrack_result
                    else:
                        # 回溯失败，继续循环
                        continue
                
                return result
            
            # 达到最大回溯次数，返回最后一次结果
            if verbose and backtrack_count >= max_backtracks:
                print(f"达到最大回溯次数({max_backtracks})，返回当前结果")
            
            return results_history[-1] if results_history else None
        
        return wrapper
    return decorator

# 快捷装饰器
thinkcheck_simple = thinkcheck
thinkcheck_retry = lambda **kwargs: thinkcheck(backtrack_strategy="retry", **kwargs)

__all__ = ["thinkcheck", "thinkcheck_simple", "thinkcheck_retry"]