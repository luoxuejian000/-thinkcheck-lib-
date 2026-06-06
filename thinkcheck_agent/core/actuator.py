"""
DeepSeek 调谐执行器
根据评估诊断结果，调用 DeepSeek 大模型对文档进行谐振调谐。
"""

import os
import time
import random
from typing import Dict, Any, Optional
from openai import OpenAI
from loguru import logger
from config import settings


class DeepSeekError(Exception):
    """DeepSeek API 错误"""
    pass


class TokenLimitError(DeepSeekError):
    """Token 限制错误"""
    pass


class HarmonyActuator:
    """基于 DeepSeek 的文档调谐引擎"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # 从配置或环境变量获取
        self.api_key = settings.deepseek_api_key
        self.base_url = settings.deepseek_base_url
        self.model = settings.deepseek_model
        self.max_tokens = settings.deepseek_max_tokens
        self.temperature = settings.deepseek_temperature
        self.max_retries = settings.deepseek_max_retries
        self.timeout = settings.deepseek_timeout
        
        # 初始化客户端
        self.client = None
        if self.api_key and self.api_key != "${DEEPSEEK_API_KEY}":
            try:
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url,
                    timeout=self.timeout
                )
                logger.info("DeepSeek 客户端初始化成功")
            except Exception as e:
                logger.error(f"DeepSeek 客户端初始化失败: {e}")
        else:
            logger.warning("DeepSeek API Key 未设置，将无法进行调谐")
        
        # 简单缓存
        self._cache = {}
        self._cache_enabled = settings.cache_enabled
    
    def call_deepseek(self, prompt: str) -> tuple[str, Dict[str, Any]]:
        """
        调用 DeepSeek API，带重试机制
        
        Returns:
            (response_text, usage_info)
        """
        if not self.client:
            raise DeepSeekError("DeepSeek 客户端未初始化")
        
        # 检查缓存
        cache_key = hash(prompt)
        if self._cache_enabled and cache_key in self._cache:
            logger.debug("使用缓存的响应")
            return self._cache[cache_key]
        
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"调用 DeepSeek API (尝试 {attempt + 1}/{self.max_retries})")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "你是一个专业的文档调谐专家，基于晶脉哲学与谐振理论。请严格按照要求修改文档，保持原文的核心意思和法律效力。"
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                )
                
                # 验证响应
                if not response.choices:
                    raise DeepSeekError("API 返回了空的响应")
                
                response_text = response.choices[0].message.content
                
                if not response_text or not response_text.strip():
                    raise DeepSeekError("API 返回了空的内容")
                
                # 获取使用信息
                usage_info = {}
                if hasattr(response, 'usage'):
                    usage_info = {
                        'prompt_tokens': response.usage.prompt_tokens,
                        'completion_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens
                    }
                
                # 缓存结果
                if self._cache_enabled:
                    self._cache[cache_key] = (response_text, usage_info)
                
                logger.debug(f"DeepSeek 调用成功: {usage_info}")
                return response_text, usage_info
            
            except Exception as e:
                last_exception = e
                logger.warning(f"DeepSeek 调用失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                
                if attempt < self.max_retries - 1:
                    # 指数退避
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    logger.debug(f"等待 {wait_time:.2f} 秒后重试...")
                    time.sleep(wait_time)
        
        # 所有重试都失败
        raise DeepSeekError(f"所有 {self.max_retries} 次调用都失败: {last_exception}")
    
    def tune(self, original_text: str, diagnosis: Dict) -> Dict[str, Any]:
        """
        执行文档调谐
        
        Args:
            original_text: 原始文档
            diagnosis: 诊断结果，来自 evaluator
        
        Returns:
            {
                'tuned_text': 调谐后的文本,
                'strategy': 策略名称,
                'success': 是否成功,
                'usage': token 使用信息,
                'error': 错误信息（如果有）
            }
        """
        result = {
            'tuned_text': original_text,
            'strategy': 'none',
            'success': True,
            'usage': {},
            'error': None
        }
        
        if not self.client:
            result['success'] = False
            result['strategy'] = 'failed'
            result['error'] = "DeepSeek 客户端不可用"
            logger.error("DeepSeek 客户端不可用，无法执行调谐")
            return result
        
        if not diagnosis.get('needs_tuning', False):
            result['strategy'] = 'none'
            logger.info("文档不需要调谐")
            return result
        
        # 选择策略
        pathology = diagnosis.get('pathology', '需调谐')
        strategy = self._select_strategy(pathology, diagnosis)
        result['strategy'] = strategy
        
        # 构建提示词
        prompt = self._build_tuning_prompt(original_text, diagnosis, strategy, pathology)
        
        try:
            # 调用 API
            tuned_text, usage = self.call_deepseek(prompt)
            result['tuned_text'] = tuned_text
            result['usage'] = usage
            
            logger.info(f"调谐完成: strategy={strategy}, usage={usage}")
            
        except Exception as e:
            result['success'] = False
            result['strategy'] = 'failed'
            result['error'] = str(e)
            logger.exception(f"调谐失败: {e}")
        
        return result
    
    def harmonize_document(self, original_text: str, diagnosis: Optional[Dict] = None) -> Dict[str, Any]:
        """
        文档和谐化（兼容接口）
        """
        return self.tune(original_text, diagnosis or {'needs_tuning': True})
    
    def _select_strategy(self, pathology: str, diagnosis: Dict) -> str:
        """
        根据病理选择调谐策略
        """
        strategies = {
            "逻辑自杀": "重构逻辑链，消除显性矛盾",
            "逻辑空洞": "引入新论据，增强发展性",
            "度假合格": "补充对立论点，增加健康的对抗性",
        }
        
        if pathology in strategies:
            return strategies[pathology]
        
        # 基于建议选择
        suggestions = diagnosis.get('suggestions', [])
        if suggestions:
            return suggestions[0][:80]
        
        return "优化术语一致性和论证流畅度"
    
    def _build_tuning_prompt(self, text: str, diagnosis: Dict, strategy: str, pathology: str) -> str:
        """
        构建调谐提示词
        """
        harmony_report = diagnosis.get('harmony_report', {})
        
        h_before = harmony_report.get('H', 0)
        u_score = harmony_report.get('U', 0)
        d_score = harmony_report.get('D', 0)
        a_score = harmony_report.get('A', 0)
        
        prompt = f"""你是一个基于"晶脉哲学与谐振理论"的文档调谐专家。

当前文档病理诊断: {pathology}
调谐目标: 将和谐度 H 从 {h_before:.3f} 提升至 0.7 以上

关键指标:
- 统一性 U: {u_score:.3f}
- 发展性 D: {d_score:.3f}
- 对抗性 A: {a_score:.3f}

调谐策略: {strategy}

要求:
1. 严格保持原文的法律效力、核心事实和整体结构不变
2. 根据指标进行精细化微调，使指标向健康区间移动 (U>0.6, D>0.6, A<0.4)
3. 不要添加不必要的新内容，只优化现有表达
4. 直接返回调谐后的完整文档文本，不要任何解释或额外标记

原文:
{text}
"""
        return prompt
    
    def clear_cache(self):
        """
        清空缓存
        """
        self._cache.clear()
        logger.info("缓存已清空")
