"""
ThinkCheck 改进版本
更适合流式推理和实际 LLM 集成
"""

import re
import inspect
import statistics
from typing import List, Tuple, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ReasoningStep:
    """改进的推理步骤记录"""
    step_id: int
    content: str
    h_score: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_backtrack_trigger: bool = False


class ImprovedHarmonicMonitor:
    """和谐度监控器（改进版）"""

    # 多语言否定词支持
    NEGATION_WORDS = {
        'zh': {"不", "没有", "无", "非", "否", "别", "没", "不要", "不能", "不会"},
        'en': {"no", "not", "never", "none", "nothing", "nobody", "nowhere", "neither", "nor"},
        'ja': {"ない", "ません", "ず", "ぬ", "ん"},
        'ko': {"아니", "않", "없", "못", "말"}
    }

    def __init__(self,
                 h_threshold: float = 0.35,
                 lookback_window: int = 4,
                 verbose: bool = True,
                 language: str = 'zh',
                 consecutive_low_threshold: int = 2):
        """
        初始化改进的监控器

        参数：
        h_threshold: 和谐度阈值
        lookback_window: 回溯窗口大小
        verbose: 是否打印详细信息
        language: 语言代码，支持 'zh', 'en', 'ja', 'ko'
        consecutive_low_threshold: 连续多少次低H才触发回溯
        """
        self.h_threshold = h_threshold
        self.lookback_window = lookback_window
        self.verbose = verbose
        self.language = language
        self.consecutive_low_threshold = consecutive_low_threshold
        self.history: List[ReasoningStep] = []
        self.step_counter = 0
        self.consecutive_low_h = 0

    def preprocess(self, text: str) -> List[str]:
        if self.language == 'zh':
            return [char for char in text if char.strip()]
        else:
            return [word.lower() for word in re.findall(r'\w+', text)]

    def calculate_h_score(self, history: List[str], current_text: str,
                          weights: Optional[Dict[str, float]] = None) -> float:
        if not current_text or not isinstance(current_text, str):
            return 0.5

        weights = weights or {"U": 0.35, "D": 0.4, "A": 0.25}
        current_words = self.preprocess(current_text)

        if not current_words:
            return 0.5

        # U: 新颖性
        if not history:
            U = 1.0
        else:
            historical_words = set()
            for past_text in history:
                historical_words.update(self.preprocess(past_text))
            new_words = [w for w in current_words if w not in historical_words]
            U = len(new_words) / max(len(current_words), 1)

        # D: 探索性
        if not history:
            D = 1.0
        else:
            similarities = []
            for past_text in history:
                if not past_text:
                    continue
                past_words = self.preprocess(past_text)
                set1, set2 = set(current_words), set(past_words)
                if not set1 and not set2:
                    similarity = 0
                else:
                    intersection = len(set1 & set2)
                    union = len(set1 | set2)
                    similarity = intersection / union if union > 0 else 0
                similarities.append(similarity)
            avg_similarity = statistics.mean(similarities) if similarities else 0
            D = 1 - avg_similarity

        # A: 对抗性
        negations = self.NEGATION_WORDS.get(self.language, set())

        word_counts = {}
        for word in current_words:
            word_counts[word] = word_counts.get(word, 0) + 1
        repeated_words = sum(1 for count in word_counts.values() if count > 2)
        repetition_score = repeated_words / max(len(current_words), 1)

        negation_count = sum(1 for word in current_words if word in negations)
        contradiction_score = min(negation_count * 0.08, 1.0)

        A = 0.6 * repetition_score + 0.4 * contradiction_score

        H = weights["U"] * U + weights["D"] * D - weights["A"] * A
        H = max(0.0, min(1.0, H))

        return round(H, 3)

    def add_step(self, content: str, metadata: Optional[Dict] = None) -> Tuple[float, bool]:
        self.step_counter += 1

        previous_contents = [step.content for step in self.history[-self.lookback_window:]]
        h_score = self.calculate_h_score(previous_contents, content)

        step = ReasoningStep(
            step_id=self.step_counter,
            content=content,
            h_score=h_score,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )

        needs_backtrack = self._check_backtrack_needed(h_score)
        step.is_backtrack_trigger = needs_backtrack
        self.history.append(step)

        if self.verbose:
            status = "🚨 需要回溯" if needs_backtrack else "✅ 正常"
            print(f"[Step {self.step_counter}] H={h_score:.2f} {status}")
            if needs_backtrack:
                print(f"    原因: {self._get_backtrack_reason()}")

        return h_score, needs_backtrack

    def _check_backtrack_needed(self, current_h: float) -> bool:
        if not self.history:
            return False

        if current_h < self.h_threshold:
            self.consecutive_low_h += 1
            if self.consecutive_low_h >= self.consecutive_low_threshold:
                return True
        else:
            self.consecutive_low_h = 0

        if len(self.history) >= 3:
            recent_h = [s.h_score for s in self.history[-3:]] + [current_h]
            is_descending = all(recent_h[i] > recent_h[i + 1] for i in range(len(recent_h) - 1))
            if is_descending and recent_h[-1] < 0.5:
                return True

        return False

    def _get_backtrack_reason(self) -> str:
        """获取回溯原因描述"""
        if self.consecutive_low_h >= self.consecutive_low_threshold:
            return f"连续{self.consecutive_low_h}次和谐度低于阈值"
        return "推理质量呈下降趋势"

    def get_summary(self) -> Dict[str, Any]:
        if not self.history:
            return {"total_steps": 0, "status": "empty"}

        h_scores = [s.h_score for s in self.history]
        return {
            "total_steps": len(self.history),
            "average_h": statistics.mean(h_scores),
            "min_h": min(h_scores),
            "max_h": max(h_scores),
            "low_h_steps": sum(1 for h in h_scores if h < self.h_threshold),
            "backtrack_triggers": sum(1 for s in self.history if s.is_backtrack_trigger),
            "status": "healthy" if h_scores[-1] >= self.h_threshold else "needs_attention"
        }

    def clear_history(self):
        self.history.clear()
        self.step_counter = 0
        self.consecutive_low_h = 0


class ImprovedRetryStrategy:
    """针对 LLM 调用的重试策略"""

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.attempt_history = []

    def generate_modified_prompt(self, original_prompt: str, attempt: int) -> str:
        modifiers = [
            original_prompt,
            f"{original_prompt}\n\n请换一个角度思考，不要重复之前的内容。",
            f"{original_prompt}\n\n请重新分析，确保每个步骤都有新的进展。",
            f"{original_prompt}\n\n让我们从头开始，一步步仔细推理。"
        ]
        return modifiers[min(attempt, len(modifiers) - 1)]

    def get_temperature(self, attempt: int) -> float:
        temps = [0.7, 0.9, 1.0, 0.5]
        return temps[min(attempt, len(temps) - 1)]

    def execute(self, func: Callable, original_prompt: str,
                attempt: int, **kwargs) -> Tuple[Any, Dict]:
        """只传入 func 实际接受的 prompt/temperature/attempt，避免 TypeError。"""
        modified_prompt = self.generate_modified_prompt(original_prompt, attempt)
        temperature = self.get_temperature(attempt)

        self.attempt_history.append({
            "attempt": attempt + 1,
            "prompt": modified_prompt,
            "temperature": temperature
        })

        sig = inspect.signature(func)
        param_names = set(sig.parameters.keys())

        call_kwargs = dict(kwargs)
        if "prompt" in param_names:
            call_kwargs["prompt"] = modified_prompt
        if "temperature" in param_names:
            call_kwargs["temperature"] = temperature
        if "attempt" in param_names:
            call_kwargs["attempt"] = attempt

        result = func(**call_kwargs)

        return result, {
            "attempt": attempt + 1,
            "temperature": temperature,
            "prompt_was_modified": attempt > 0
        }


def monitor_streaming_reasoning(reasoning_generator: Callable,
                                monitor: ImprovedHarmonicMonitor) -> Tuple[str, Dict]:
    all_steps = []

    for step_content in reasoning_generator():
        h_score, needs_backtrack = monitor.add_step(step_content)
        all_steps.append({
            "content": step_content,
            "h_score": h_score,
            "needs_backtrack": needs_backtrack
        })

        if needs_backtrack:
            # 这里可以实际中断推理并触发回溯
            print(f"⚠️  检测到推理问题，考虑回溯...")

    summary = monitor.get_summary()
    final_answer = all_steps[-1]["content"] if all_steps else ""

    return final_answer, {"steps": all_steps, "summary": summary}
