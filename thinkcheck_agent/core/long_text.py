"""
长文本处理模块
提供分块处理、跨块矛盾追踪等功能
"""
import numpy as np
from typing import List, Dict
import re
from itertools import combinations
from collections import defaultdict


class TextChunker:
    def __init__(self, max_chars_per_chunk: int = 4000):
        self.max_chars_per_chunk = max_chars_per_chunk

    def chunk_sentences(self, sentences: List[str]) -> List[List[int]]:
        chunks = []
        current_chunk = []
        current_length = 0
        for idx, sent in enumerate(sentences):
            sent_len = len(sent)
            if current_length + sent_len > self.max_chars_per_chunk and current_chunk:
                chunks.append(current_chunk)
                current_chunk = [idx]
                current_length = sent_len
            else:
                current_chunk.append(idx)
                current_length += sent_len
        if current_chunk:
            chunks.append(current_chunk)
        return chunks


class InterBlockContradictionTracker:
    def __init__(self, semantic_model, threshold: float = -0.15):
        self.semantic_model = semantic_model
        self.threshold = threshold
        self.concept_registry = defaultdict(list)
        self.cross_edges: List[Dict] = []

    def register_block_concepts(self, block_idx, sentences, sentence_indices, embeddings):
        for i, sent in enumerate(sentences):
            if not sent:
                continue
            words = set(re.findall(r'[\u4e00-\u9fa5a-zA-Z]{2,}', sent))
            for w in words:
                self.concept_registry[w].append({
                    'block': block_idx,
                    'sentence_idx': sentence_indices[i],
                    'vector': embeddings[i]
                })

    def detect_cross_block_contradictions(self):
        self.cross_edges = []
        for concept, occurrences in self.concept_registry.items():
            if len(occurrences) < 2:
                continue
            for (occ_a, occ_b) in combinations(occurrences, 2):
                if occ_a['block'] == occ_b['block']:
                    continue
                sim = np.dot(occ_a['vector'], occ_b['vector']) / (
                    np.linalg.norm(occ_a['vector']) * np.linalg.norm(occ_b['vector']) + 1e-8)
                if sim < self.threshold:
                    weight = min(1.0, -sim)
                    self.cross_edges.append({
                        'i': occ_a['sentence_idx'],
                        'j': occ_b['sentence_idx'],
                        'weight': weight,
                        'type': 'cross_block',
                        'concept': concept
                    })
        return self.cross_edges

    def clear(self):
        self.concept_registry.clear()
        self.cross_edges.clear()
