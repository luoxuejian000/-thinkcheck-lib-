from setuptools import setup, find_packages

setup(
    name="thinkcheck-legal",
    version="2.0.0",
    packages=find_packages(include=["thinkcheck_legal", "thinkcheck_legal.*"]),
    install_requires=[
        "sentence-transformers>=2.2.0",
        "scikit-learn>=1.0.0",
        "numpy>=1.20.0",
    ],
    author="李广好",
    description="法律推理谐振评估工具 - 基于晶脉哲学",
    url="https://github.com/luoxuejian000/-thinkcheck-lib-",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
