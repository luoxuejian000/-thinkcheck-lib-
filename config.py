"""
配置管理模块
"""

import os
from typing import Optional
from pathlib import Path
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


# 加载 .env 文件
env_path = Path('.') / '.env'
if env_path.exists():
    load_dotenv(env_path)


class Settings(BaseSettings):
    """
    应用配置
    """
    
    # DeepSeek API 配置
    deepseek_api_key: str = Field(default="", description="DeepSeek API Key")
    deepseek_base_url: str = Field(default="https://api.deepseek.com/v1", description="DeepSeek API Base URL")
    deepseek_model: str = Field(default="deepseek-chat", description="DeepSeek Model Name")
    deepseek_max_tokens: int = Field(default=4000, description="Max tokens per request")
    deepseek_temperature: float = Field(default=0.1, description="Temperature for generation")
    deepseek_max_retries: int = Field(default=3, description="Max retries for API calls")
    deepseek_timeout: int = Field(default=30, description="Timeout in seconds")
    
    # ThinkCheck 配置
    thinkcheck_default_domain: str = Field(default="legal", description="Default domain")
    thinkcheck_harmony_threshold: float = Field(default=0.7, description="Harmony threshold")
    thinkcheck_adversarial_threshold: float = Field(default=0.3, description="Adversarial threshold")
    thinkcheck_enable_suggestions: bool = Field(default=True, description="Enable suggestions")
    
    # OCHR 配置
    ochr_boundary_mode: str = Field(default="adaptive", description="Boundary mode")
    
    # 日志配置
    log_level: str = Field(default="INFO", description="Log level")
    log_file: str = Field(default="logs/agent.log", description="Log file path")
    
    # 性能配置
    max_file_size_mb: int = Field(default=10, description="Max file size in MB")
    batch_size: int = Field(default=5, description="Batch size")
    cache_enabled: bool = Field(default=True, description="Enable cache")
    cache_ttl_seconds: int = Field(default=3600, description="Cache TTL in seconds")
    
    # API 服务配置
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    
    model_config = {
        "env_prefix": "THINKCHECK_",
        "env_file": ".env",
        "extra": "ignore"
    }
    
    @field_validator('deepseek_api_key')
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        if not v or v == "${DEEPSEEK_API_KEY}":
            # 尝试从环境变量获取
            return os.environ.get("DEEPSEEK_API_KEY", "")
        return v


# 全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """
    获取配置实例
    """
    return settings
