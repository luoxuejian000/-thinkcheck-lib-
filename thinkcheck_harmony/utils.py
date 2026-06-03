"""
ThinkCheck Harmony 工具模块
文本处理、分块等辅助函数
"""

import re
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class TextChunk:
    content: str
    start_index: int
    end_index: int
    metadata: dict = None


def clean_text(text: str) -> str:
    """
    清理文本：去除多余空格、换行等
    """
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text


def split_into_sentences(text: str) -> List[str]:
    """
    将文本分割成句子
    """
    pattern = r'(?<=[.!?。！？])\s+'
    sentences = re.split(pattern, text)
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences


def split_into_paragraphs(text: str) -> List[str]:
    """
    将文本分割成段落
    """
    paragraphs = text.split('\n\n')
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    return paragraphs


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[TextChunk]:
    """
    将文本分块，支持重叠
    """
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        if end > len(text):
            end = len(text)
        
        chunk_content = text[start:end]
        chunks.append(TextChunk(
            content=chunk_content,
            start_index=start,
            end_index=end
        ))
        
        start += chunk_size - overlap
        if start >= len(text):
            break
    
    return chunks


def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """
    简单的关键词提取（基于词频）
    """
    words = re.findall(r'[\w\u4e00-\u9fff]+', text.lower())
    stop_words = {'的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
    
    filtered_words = [word for word in words if word not in stop_words and len(word) > 1]
    
    from collections import Counter
    word_counts = Counter(filtered_words)
    return [word for word, _ in word_counts.most_common(top_n)]


def detect_language(text: str) -> str:
    """
    简单的语言检测（基于字符）
    """
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    english_chars = re.findall(r'[a-zA-Z]', text)
    
    if len(chinese_chars) > len(english_chars):
        return 'zh'
    else:
        return 'en'
