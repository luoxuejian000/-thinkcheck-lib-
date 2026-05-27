"""
ThinkCheck-lib 安装配置文件
版本: 2.0.1
描述: 谐振理论LLM推理监控框架
"""

from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="thinkcheck",
    version="2.0.1",
    author="ThinkCheck Team",
    author_email="thinkcheck@example.com",
    description="谐振理论LLM推理监控框架 - 自动检测AI推理质量下降并触发回溯",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/luoxuejian000/thinkcheck-lib",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.7",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    keywords="llm reasoning monitoring ai harmonic quality",
    project_urls={
        "Bug Reports": "https://github.com/luoxuejian000/thinkcheck-lib/issues",
        "Source": "https://github.com/luoxuejian000/thinkcheck-lib",
    },
)
