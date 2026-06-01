"""
DeepSeek 调谐执行器
根据评估诊断结果，调用 DeepSeek 大模型对文档进行谐振调谐。
"""
import os
from typing import Dict, Any
from openai import OpenAI
from loguru import logger


class HarmonyActuator:
    """基于 DeepSeek 的文档调谐引擎。"""

    def __init__(self, config: Dict[str, Any]):
        ds_config = config.get('deepseek', {})
        api_key = os.environ.get("DEEPSEEK_API_KEY", ds_config.get('api_key'))
        if not api_key or api_key == "${DEEPSEEK_API_KEY}":
            logger.error("DeepSeek API Key 未设置。")
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key, base_url=ds_config.get('base_url', 'https://api.deepseek.com/v1'))
        self.model = ds_config.get('model', 'deepseek-chat')
        self.max_tokens = ds_config.get('max_tokens', 4000)
        self.temperature = ds_config.get('temperature', 0.1)

    def tune(self, original_text: str, diagnosis: Dict) -> Dict[str, Any]:
        if not self.client:
            logger.error("API 客户端不可用，无法执行调谐。")
            return {"tuned_text": original_text, "strategy": "failed"}
        if not diagnosis.get('needs_tuning'):
            return {"tuned_text": original_text, "strategy": "none"}
        pathology = diagnosis.get('pathology', '需调谐')
        strategy = self._select_strategy(pathology, diagnosis)
        prompt = self._build_tuning_prompt(original_text, diagnosis, strategy, pathology)
        try:
            response = self.client.chat.completions.create(model=self.model, messages=[{"role": "user", "content": prompt}], max_tokens=self.max_tokens, temperature=self.temperature)
            tuned_text = response.choices[0].message.content
            logger.info(f"调谐完成，策略: {strategy}。")
            return {"tuned_text": tuned_text, "strategy": strategy}
        except Exception as e:
            logger.exception(f"调用 DeepSeek API 时发生错误: {e}")
            return {"tuned_text": original_text, "strategy": "failed"}

    def _select_strategy(self, pathology: str, diagnosis: Dict) -> str:
        strategies = {"逻辑自杀": "重构逻辑链，消除显性矛盾", "逻辑空洞": "引入新论据，增强发展性(D)", "度假合格": "补充对立论点，增加健康的对抗性(A)"}
        if pathology in strategies: return strategies[pathology]
        suggestions = diagnosis.get('suggestions', [])
        return suggestions[0][:80] if suggestions else "优化术语一致性和论证流畅度"

    def _build_tuning_prompt(self, text: str, diagnosis: Dict, strategy: str, pathology: str) -> str:
        harmony_report = diagnosis.get('harmony_report', {})
        return f"""你是一个基于“晶脉哲学与谐振理论”的文档调谐专家。
当前文档病理诊断：{pathology}
调谐目标：将H值从 {harmony_report.get('H'):.3f} 提升至 0.7 以上。
关键指标：U={harmony_report.get('U'):.3f}, D={harmony_report.get('D'):.3f}, A={harmony_report.get('A'):.3f}
调谐策略：{strategy}
要求：

1. 严格保持原文的法律效力和核心事实不变。

2. 根据指标进行精细化微调，使指标向健康区间(0.6-0.8)移动。

3. 直接返回调谐后的完整文档文本，不要任何解释。

原文：

{text}
"""