"""
ThinkCheck核心算法模块
包含和谐度计算器和监控器
"""

import re
import json
from typing import List, Tuple, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import statistics

@dataclass
class ReasoningStep:
    """推理步骤记录"""
    step_id: int
    content: str
    h_score: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

class HarmonicMonitor:
    """和谐度监控器"""
    
    def __init__(self, 
                 h_threshold: float = 0.3,
                 lookback_window: int = 3,
                 verbose: bool = True):
        """
        初始化监控器
        
        参数：
        h_threshold: 和谐度阈值，低于此值触发警告
        lookback_window: 回溯窗口大小
        verbose: 是否打印详细信息
        """
        self.h_threshold = h_threshold
        self.lookback_window = lookback_window
        self.verbose = verbose
        self.history: List[ReasoningStep] = []
        self.step_counter = 0
        
    def add_step(self, content: str, metadata: Optional[Dict] = None) -> Tuple[float, bool]:
        """
        添加推理步骤并计算和谐度
        
        返回：
        (h_score, needs_backtrack)
        """
        self.step_counter += 1
        
        # 计算和谐度
        previous_contents = [step.content for step in self.history[-self.lookback_window:]]
        h_score = calculate_h_score(previous_contents, content)
        
        # 创建步骤记录
        step = ReasoningStep(
            step_id=self.step_counter,
            content=content,
            h_score=h_score,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        # 添加到历史
        self.history.append(step)
        
        # 检查是否需要回溯
        needs_backtrack = self._check_backtrack_needed()
        
        if self.verbose:
            status = "需要回溯" if needs_backtrack else "正常"
            print(f"[Step {self.step_counter}] H={h_score:.2f} {status} | {content[:50]}...")
            
            if needs_backtrack:
                print(f"    原因：和谐度低于阈值 {h_score:.2f} < {self.h_threshold}")
        
        return h_score, needs_backtrack
    
    def _check_backtrack_needed(self) -> bool:
        """检查是否需要回溯"""
        if not self.history:
            return False
        
        current_step = self.history[-1]
        
        # 规则1：当前H值低于阈值
        if current_step.h_score < self.h_threshold:
            return True
        
        # 规则2：最近几步连续下降
        recent_steps = self.history[-min(self.lookback_window, len(self.history)):]
        if len(recent_steps) >= 3:
            h_scores = [step.h_score for step in recent_steps]
            # 检查是否连续下降
            is_descending = all(h_scores[i] > h_scores[i+1] for i in range(len(h_scores)-1))
            if is_descending:
                return True
        
        return False
    
    def get_summary(self) -> Dict[str, Any]:
        """获取监控摘要"""
        if not self.history:
            return {"total_steps": 0, "average_h": 0, "status": "empty"}
        
        h_scores = [step.h_score for step in self.history]
        
        return {
            "total_steps": len(self.history),
            "average_h": statistics.mean(h_scores),
            "min_h": min(h_scores),
            "max_h": max(h_scores),
            "low_h_steps": sum(1 for h in h_scores if h < self.h_threshold),
            "last_h": h_scores[-1],
            "status": "healthy" if h_scores[-1] >= self.h_threshold else "needs_attention"
        }
    
    def clear_history(self):
        """清空历史记录"""
        self.history.clear()
        self.step_counter = 0

def calculate_h_score(history: List[str], current_text: str, 
                     weights: Optional[Dict[str, float]] = None) -> float:
    """
    计算和谐度H = w_u*U + w_d*D - w_a*A
    
    参数：
    history: 历史文本列表
    current_text: 当前文本
    weights: 权重字典，默认{"U": 0.4, "D": 0.4, "A": 0.2}
    
    返回：
    和谐度H (0-1)
    """
    if not current_text or not isinstance(current_text, str):
        return 0.5  # 默认中值
    
    # 设置默认权重
    weights = weights or {"U": 0.4, "D": 0.4, "A": 0.2}
    
    # 预处理：转换为小写并分词
    def preprocess(text: str) -> List[str]:
        # 简单分词，可按需扩展
        return [word.lower() for word in re.findall(r'\w+', text)]
    
    current_words = preprocess(current_text)
    
    if not current_words:
        return 0.5
    
    # 1. 计算新颖性U（新信息比例）
    if not history:
        U = 1.0  # 第一步默认高分
    else:
        # 合并历史中的词汇
        historical_words = set()
        for past_text in history[-3:]:  # 只看最近3条
            historical_words.update(preprocess(past_text))
        
        # 新词汇比例
        new_words = [w for w in current_words if w not in historical_words]
        U = len(new_words) / len(current_words)
    
    # 2. 计算探索性D（与历史的差异度）
    if not history:
        D = 1.0
    else:
        # 计算与最近历史文本的相似度
        similarities = []
        for past_text in history[-3:]:
            if not past_text:
                continue
            past_words = preprocess(past_text)
            
            # Jaccard相似度
            set1 = set(current_words)
            set2 = set(past_words)
            
            if not set1 and not set2:
                similarity = 0
            else:
                intersection = len(set1 & set2)
                union = len(set1 | set2)
                similarity = intersection / union if union > 0 else 0
            
            similarities.append(similarity)
        
        avg_similarity = statistics.mean(similarities) if similarities else 0
        D = 1 - avg_similarity  # 相似度越低，探索性越高
    
    # 3. 计算对抗性A（重复/矛盾程度）
    # 3.1 重复性
    word_counts = {}
    for word in current_words:
        word_counts[word] = word_counts.get(word, 0) + 1
    
    repeated_words = sum(1 for count in word_counts.values() if count > 1)
    repetition_score = repeated_words / len(current_words) if current_words else 0
    
    # 3.2 矛盾检测（简单版：检查否定词）
    negation_words = {"不", "没有", "无", "非", "否", "别"}
    negation_count = sum(1 for word in current_words if word in negation_words)
    contradiction_score = min(negation_count * 0.1, 1.0)  # 每个否定词增加0.1
    
    A = 0.7 * repetition_score + 0.3 * contradiction_score
    
    # 4. 计算和谐度H
    H = weights["U"] * U + weights["D"] * D - weights["A"] * A
    
    # 限制在0-1之间
    H = max(0.0, min(1.0, H))
    
    return round(H, 3)

__all__ = ["HarmonicMonitor", "calculate_h_score", "ReasoningStep"]