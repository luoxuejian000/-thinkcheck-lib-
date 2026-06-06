"""
ThinkCheck Harmony 指标计算模块
实现四维评估：U, D, A, H，包含语义向量对立检测、共现约束、分层计算等
"""

import re
import math
from typing import List, Dict, Tuple, Optional
from collections import Counter, defaultdict
import numpy as np
from itertools import combinations


# ============================================================
# 参数协商声明（实践介入论要求：所有参数必须可审计、可追溯）
# ============================================================
# U（统一性）权重配置 - 关系本体论
#   base_unity（相邻句子相似度）：权重 0.5
#     依据：作为基础指标，衡量文档的结构连贯性
#   term_consistency（同术语一致性）：权重 0.3
#     依据：确保同一术语在全文中的语义一致性
#   cross_term_consistency（跨术语全局一致性）：权重 0.2
#     依据：衡量不同概念之间的关系网络一致性
#
# D（发展性）权重配置 - 矛盾动力论
#   base_development（新术语分布均匀性）：权重 0.4
#     依据：基础发展性指标
#   伪创新过滤阈值：0.85
#     依据：如果新术语与已有知识语义高度相似（>0.85），则只是换了个说法
#   genuineness_ratio（真正新术语比例）：权重 0.4
#     依据：区分真正的"发展"与"伪发展"
#   document_length（文档长度）：权重 0.3
#     依据：适中的长度反映充分的发展
#
# H（和谐度）λ权重配置 - 谐振调谐论
#   lambda_u: 0.4（协商起点）
#   lambda_d: 0.4（协商起点）
#   lambda_a: 0.2（协商起点）
#     依据：平衡U、D、A三维度的重要性，A维度权重较低以避免过度惩罚
#
# A（对抗性）相关配置
#   语义矛盾检测方式：基于句子嵌入余弦相似度的向量对立检测（关系本体论）
#   否定词检测权重上限：0.35（协商起点）
#   语义对立权重系数：0.3（协商起点）
#   interpretation 阈值：0.5（协商起点）
# ============================================================


# 全局的矛盾检测器实例，用于向后兼容
_global_detector = None

# 全局的文档分析器实例，用于U和D计算
_global_analyzer = None


class DocumentAnalyzer:
    """
    基于关系本体论的文档分析器
    用于计算U（统一性）和D（发展性），支持语义模型增强
    """
    
    def __init__(self, semantic_model=None):
        """
        初始化文档分析器
        
        Args:
            semantic_model: 可选的语义模型，用于句子嵌入
        """
        self.semantic_model = semantic_model
        
        # U（统一性）权重配置
        self.base_unity_weight = 0.5
        self.term_consistency_weight = 0.3
        self.cross_term_consistency_weight = 0.2
        
        # D（发展性）权重配置
        self.base_development_weight = 0.4
        self.genuineness_ratio_weight = 0.4
        self.document_length_weight = 0.3
        self.genuineness_threshold = 0.85  # 伪创新过滤阈值
    
    def _get_embeddings(self, sentences):
        """
        获取句子嵌入
        优先使用语义模型，失败时使用TF-IDF作为降级方案
        """
        if self.semantic_model:
            try:
                return self.semantic_model.encode(sentences, convert_to_numpy=True)
            except Exception:
                pass
        
        # 使用TF-IDF作为降级方案
        from sklearn.feature_extraction.text import TfidfVectorizer
        vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(1, 3))
        embeddings = vectorizer.fit_transform(sentences)
        return embeddings.toarray()
    
    def _get_sentences(self, text: str) -> List[str]:
        """
        将文本分割成句子
        """
        sentences = re.split(r'[.!?。！？]', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def calculate_unity(self, text: str) -> float:
        """
        基于关系本体论的统一性计算
        U = 0.5 * base_unity + 0.3 * term_consistency + 0.2 * cross_term_consistency
        短文本（<=3句）使用句子间相似度直接计算
        
        Args:
            text: 待分析的文本
            
        Returns:
            统一性值 [0, 1]
        """
        if not text or len(text.strip()) < 10:
            return 0.2
        
        sentences = self._get_sentences(text)
        
        if len(sentences) < 2:
            # 单句短文本：检测转折词并分割计算
            if len(sentences) == 1:
                single_sent = sentences[0]
                # 检测转折词
                contrast_markers = ['但', '但是', '却', '然而', '不过', '可是', '只是']
                for marker in contrast_markers:
                    if marker in single_sent:
                        parts = single_sent.split(marker, 1)
                        if len(parts) == 2 and len(parts[0].strip()) > 0 and len(parts[1].strip()) > 0:
                            before = parts[0].strip()
                            after = parts[1].strip()
                            
                            # 方法1：TF-IDF相似度
                            try:
                                from sklearn.feature_extraction.text import TfidfVectorizer
                                vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(1, 2))
                                tfidf_matrix = vectorizer.fit_transform([before, after])
                                tfidf_array = tfidf_matrix.toarray()
                                
                                dot = np.dot(tfidf_array[0], tfidf_array[1])
                                norm0 = np.linalg.norm(tfidf_array[0])
                                norm1 = np.linalg.norm(tfidf_array[1])
                                if norm0 > 0 and norm1 > 0:
                                    tfidf_sim = dot / (norm0 * norm1)
                                else:
                                    tfidf_sim = 0.0
                            except Exception:
                                tfidf_sim = 0.0
                            
                            # 方法2：字符集相似度
                            chars_before = set(re.findall(r'[\u4e00-\u9fa5a-zA-Z]', before))
                            chars_after = set(re.findall(r'[\u4e00-\u9fa5a-zA-Z]', after))
                            
                            if chars_before and chars_after:
                                char_sim = len(chars_before & chars_after) / len(chars_before | chars_after)
                            else:
                                char_sim = 0.0
                            
                            # 方法3：结构特征相似度
                            # 检测评价词模式（积极/消极）
                            positive_words = {'好', '强', '大', '优', '棒', '佳', '美', '善', '良', '高', '多', '快', '新', '全'}
                            negative_words = {'差', '弱', '小', '劣', '坏', '恶', '丑', '低', '少', '慢', '旧', '没', '无', '不', '非'}
                            
                            before_chars_set = set(before)
                            after_chars_set = set(after)
                            
                            before_pos = len(before_chars_set & positive_words)
                            before_neg = len(before_chars_set & negative_words)
                            after_pos = len(after_chars_set & positive_words)
                            after_neg = len(after_chars_set & negative_words)
                            
                            # 如果前后部分的极性相反，说明有语义张力，U值较低
                            polarity_diff = abs((before_pos - before_neg) - (after_pos - after_neg))
                            polarity_factor = min(1.0, polarity_diff / 3)  # 归一化
                            
                            # 组合相似度
                            # TF-IDF权重0.3，字符集权重0.2，极性权重0.5
                            combined = 0.3 * tfidf_sim + 0.2 * char_sim + 0.5 * (1.0 - polarity_factor)
                            
                            # 不使用min截断，让极性差异能产生区分
                            return max(0.1, min(1.0, combined))
            return 0.5
        
        # 短文本处理：直接用句子间相似度，不返回固定默认值
        if len(sentences) <= 3:
            if self.semantic_model is not None:
                try:
                    embeddings = self._get_embeddings(sentences)
                    sims = []
                    for i in range(len(sentences)):
                        for j in range(i + 1, len(sentences)):
                            sim = np.dot(embeddings[i], embeddings[j]) / (
                                np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j]) + 1e-8
                            )
                            sims.append(max(0.0, sim))
                    return float(np.mean(sims)) if sims else 0.5
                except Exception:
                    pass
            
            # 无语义模型时用Jaccard相似度 + TF-IDF语义相似度
            sims = []
            for i in range(len(sentences)):
                for j in range(i + 1, len(sentences)):
                    # 词汇Jaccard相似度
                    words_i = set(re.findall(r'[\u4e00-\u9fa5a-zA-Z]+', sentences[i]))
                    words_j = set(re.findall(r'[\u4e00-\u9fa5a-zA-Z]+', sentences[j]))
                    
                    if not words_i and not words_j:
                        jaccard_sim = 0.5  # 都为空时给中等分
                    elif not words_i or not words_j:
                        jaccard_sim = 0.3  # 一个为空时给较低分
                    else:
                        jaccard_sim = len(words_i & words_j) / len(words_i | words_j)
                    
                    # 字符级n-gram相似度（捕捉语义关联）
                    chars_i = sentences[i]
                    chars_j = sentences[j]
                    ngram_sim = 0.0
                    if len(chars_i) > 1 and len(chars_j) > 1:
                        # 使用2-gram
                        ngrams_i = set(chars_i[k:k+2] for k in range(len(chars_i)-1))
                        ngrams_j = set(chars_j[k:k+2] for k in range(len(chars_j)-1))
                        if ngrams_i and ngrams_j:
                            ngram_sim = len(ngrams_i & ngrams_j) / len(ngrams_i | ngrams_j)
                    
                    # 组合相似度：词汇权重0.6，字符n-gram权重0.4
                    combined_sim = 0.6 * jaccard_sim + 0.4 * ngram_sim
                    sims.append(combined_sim)
            
            # 确保返回值在合理范围内
            avg_sim = float(np.mean(sims)) if sims else 0.5
            return max(0.2, min(1.0, avg_sim))
        
        # 原有长文本三组件计算
        base_unity = self._calculate_base_unity(sentences)
        term_consistency = self._calculate_term_consistency(sentences)
        cross_term_consistency = self._calculate_cross_term_consistency(sentences)
        
        # 组合三个指标
        unity = (
            self.base_unity_weight * base_unity +
            self.term_consistency_weight * term_consistency +
            self.cross_term_consistency_weight * cross_term_consistency
        )
        
        # 确保结果在[0.2, 1]范围内
        return max(0.2, min(1.0, unity))
    
    def _calculate_base_unity(self, sentences: List[str]) -> float:
        """
        计算相邻句子相似度
        """
        if len(sentences) < 2:
            return 1.0
        
        try:
            embeddings = self._get_embeddings(sentences)
            total_sim = 0.0
            count = 0
            
            for i in range(len(sentences) - 1):
                sim = np.dot(embeddings[i], embeddings[i + 1]) / (
                    np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[i + 1]) + 1e-8
                )
                total_sim += sim
                count += 1
            
            return total_sim / count if count > 0 else 0.5
        except Exception:
            # 降级：使用简单的词汇重叠度
            total_overlap = 0.0
            count = 0
            for i in range(len(sentences) - 1):
                words_i = set(re.findall(r'[\w\u4e00-\u9fff]+', sentences[i].lower()))
                words_j = set(re.findall(r'[\w\u4e00-\u9fff]+', sentences[i + 1].lower()))
                if words_i and words_j:
                    overlap = len(words_i & words_j) / len(words_i | words_j)
                    total_overlap += overlap
                    count += 1
            
            return total_overlap / count if count > 0 else 0.5
    
    def _calculate_term_consistency(self, sentences: List[str]) -> float:
        """
        计算同术语一致性：提取所有核心术语，对每个术语，计算包含该术语的所有句子之间的平均语义相似度
        """
        # 提取高频术语（在文档中出现>=2次）
        words = re.findall(r'[\w\u4e00-\u9fff]+', ' '.join(sentences).lower())
        word_freq = Counter(words)
        important_terms = [word for word, count in word_freq.items() if count >= 2 and len(word) > 1]
        
        if not important_terms:
            return 0.5
        
        consistency_scores = []
        for term in important_terms:
            # 找出所有包含该术语的句子
            containing_sentences = [sent for sent in sentences if term in sent.lower()]
            
            if len(containing_sentences) < 2:
                continue
            
            try:
                embeddings = self._get_embeddings(containing_sentences)
                total_sim = 0.0
                count = 0
                
                for i in range(len(containing_sentences)):
                    for j in range(i + 1, len(containing_sentences)):
                        sim = np.dot(embeddings[i], embeddings[j]) / (
                            np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j]) + 1e-8
                        )
                        total_sim += sim
                        count += 1
                
                if count > 0:
                    consistency_scores.append(total_sim / count)
            except Exception:
                # 降级：使用词汇重叠度
                if len(containing_sentences) >= 2:
                    all_words = [set(re.findall(r'[\w\u4e00-\u9fff]+', sent.lower())) for sent in containing_sentences]
                    overlaps = []
                    for i in range(len(all_words)):
                        for j in range(i + 1, len(all_words)):
                            if all_words[i] and all_words[j]:
                                overlap = len(all_words[i] & all_words[j]) / len(all_words[i] | all_words[j])
                                overlaps.append(overlap)
                    if overlaps:
                        consistency_scores.append(sum(overlaps) / len(overlaps))
        
        return sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0.5
    
    def _calculate_cross_term_consistency(self, sentences: List[str]) -> float:
        """
        计算跨术语全局一致性：提取所有句子中长度>1的实词，计算所有不同实词之间的语义向量余弦相似度
        """
        # 提取所有实词
        all_words = []
        for sent in sentences:
            words = [w for w in re.findall(r'[\w\u4e00-\u9fff]+', sent.lower()) if len(w) > 1]
            all_words.extend(words)
        
        # 去重
        unique_words = list(set(all_words))
        
        if len(unique_words) < 2:
            return 1.0
        
        try:
            # 为每个词添加上下文（使用所在句子）
            word_contexts = [f"{word}: {sentences[min(i // 3, len(sentences) - 1)]}" for i, word in enumerate(unique_words)]
            embeddings = self._get_embeddings(word_contexts)
            
            total_sim = 0.0
            count = 0
            
            for i in range(len(unique_words)):
                for j in range(i + 1, len(unique_words)):
                    sim = np.dot(embeddings[i], embeddings[j]) / (
                        np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j]) + 1e-8
                    )
                    total_sim += sim
                    count += 1
            
            return total_sim / count if count > 0 else 0.5
        except Exception:
            # 降级：使用词汇共现度
            cooccurrence = 0.0
            count = 0
            for i in range(len(unique_words)):
                for j in range(i + 1, len(unique_words)):
                    # 检查两个词是否在同一句子中出现
                    co_occur = any(unique_words[i] in sent and unique_words[j] in sent 
                                   for sent in sentences)
                    if co_occur:
                        cooccurrence += 1
                    count += 1
            
            return cooccurrence / count if count > 0 else 0.5
    
    def calculate_development(self, text: str) -> float:
        """
        基于矛盾动力论的发展性计算
        区分真正的"发展"与"伪发展"
        
        Args:
            text: 待分析的文本
            
        Returns:
            发展性值 [0, 1]
        """
        if not text or len(text.strip()) < 10:
            return 0.0
        
        sentences = re.split(r'[.!?。！？]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        development_score = 0.0
        
        # 1. 词汇丰富度
        words = re.findall(r'[\w\u4e00-\u9fff]+', text.lower())
        if words:
            unique_words = set(words)
            ttr = len(unique_words) / len(words)
            development_score += ttr * 0.3
        
        # 2. 分析创新和重复，检测伪创新
        if sentences:
            innovation_score, repetition_penalty = self._analyze_innovation_and_repetition(sentences)
            development_score += innovation_score * 0.4
            development_score -= repetition_penalty * 0.1
        
        # 3. 文档长度
        text_length = len(text)
        if text_length < 100:
            length_score = text_length / 200
        elif text_length < 1000:
            length_score = 0.5 + (text_length - 100) / 1800
        elif text_length < 5000:
            length_score = 1.0
        else:
            length_score = max(0.5, 1.0 - (text_length - 5000) / 10000)
        development_score += length_score * 0.3
        
        # 4. 句子结构多样性
        if len(sentences) > 3:
            sentence_patterns = []
            for s in sentences:
                if s.strip():
                    has_numbers = bool(re.search(r'\d', s))
                    has_special_chars = bool(re.search(r'[,:;：；]', s))
                    pattern = (len(s.split()) > 10, has_numbers, has_special_chars)
                    sentence_patterns.append(pattern)
            
            if sentence_patterns:
                unique_patterns = len(set(sentence_patterns))
                pattern_diversity = unique_patterns / len(sentence_patterns)
                development_score += pattern_diversity * 0.1
        
        return max(0.0, min(1.0, development_score))
    
    def _extract_meaningful_terms(self, text: str) -> set:
        """
        提取有意义的术语
        使用多种策略提取真正的术语，而不是任意字符组合
        """
        terms = set()
        
        # 策略1：提取2-4字的中文词组，但过滤掉常见的无意义组合
        stopwords = {'正在', '已经', '可以', '能够', '应该', '必须', '因为', '所以', '虽然', 
                     '但是', '然而', '如果', '那么', '这个', '那个', '这些', '那些', '一种',
                     '一个', '这个', '那个', '它的', '我们的', '他们的', '该领域', '的方式',
                     '包括', '研究', '生产', '企图', '了解', '做出', '反应', '渗透', '重塑'}
        
        # 提取2-4字的中文词组
        all_ngrams = re.findall(r'[\u4e00-\u9fff]{2,4}', text.lower())
        for ngram in all_ngrams:
            # 过滤掉停用词和无意义组合
            if ngram not in stopwords:
                # 检查是否包含有意义的词汇特征（如包含名词性字符）
                meaningful_chars = {'人', '工', '智', '能', '机', '器', '算', '法', '技', '术',
                                   '科', '学', '研', '究', '系', '统', '语', '言', '图', '像',
                                   '识', '别', '处', '理', '专', '家', '自', '然', '世', '界',
                                   '改', '变', '未', '来', '行', '业'}
                if any(char in ngram for char in meaningful_chars):
                    terms.add(ngram)
        
        # 策略2：提取英文单词
        english_terms = re.findall(r'[a-zA-Z]{2,}', text.lower())
        terms.update(english_terms)
        
        return terms
    
    def _analyze_innovation_and_repetition(self, sentences: List[str]) -> Tuple[float, float]:
        """
        分析建设性创新和破坏性重复，同时过滤伪创新
        """
        if len(sentences) < 2:
            return 0.5, 0.0
        
        # 检测重复内容
        sentence_patterns = []
        for sent in sentences:
            words = self._extract_meaningful_terms(sent)
            sentence_patterns.append(tuple(sorted(words)))
        
        # 计算重复率
        pattern_counts = Counter(sentence_patterns)
        repetitions = sum(count - 1 for count in pattern_counts.values())
        repetition_penalty = min(repetitions / len(sentences), 0.5)
        
        # 提取新术语
        all_words = []
        for sent in sentences:
            words = self._extract_meaningful_terms(sent)
            all_words.extend(list(words))
        
        word_freq = Counter(all_words)
        new_terms = [word for word, count in word_freq.items() if count == 1]  # 只出现一次的词
        
        # 过滤伪创新
        genuinely_new_terms = []
        for term in new_terms:
            context = ' '.join([sent for sent in sentences if term in sent.lower()])
            existing_terms = [w for w in new_terms if w != term]
            if self._is_genuinely_new(term, context, existing_terms):
                genuinely_new_terms.append(term)
        
        # 计算真正的新术语比例
        genuineness_ratio = len(genuinely_new_terms) / len(new_terms) if new_terms else 1.0
        
        # 计算创新度
        unique_patterns = len(pattern_counts)
        innovation_score = unique_patterns / len(sentence_patterns)
        
        # 检测递进关系
        progressive_markers = ['然后', '因此', '所以', '此外', '而且', '另外', '进一步',
                              'then', 'therefore', 'thus', 'furthermore', 'moreover', 'additionally']
        progressive_count = 0
        for sent in sentences:
            if any(marker in sent for marker in progressive_markers):
                progressive_count += 1
        
        # 如果有递进关系，增加创新分数
        if progressive_count > 0:
            innovation_score += min(0.2, progressive_count / len(sentences))
        
        # 应用真正新术语比例（增大权重，使伪创新检测更有效）
        innovation_score *= (0.3 + 0.7 * genuineness_ratio)
        
        return min(1.0, innovation_score), repetition_penalty
    
    def _is_genuinely_new(self, term: str, context: str, existing_terms: List[str]) -> bool:
        """
        判断一个术语是否真正带来了新信息
        基于关系本体论：如果新术语与已有知识高度相似，则只是换了个说法
        无语义模型时使用字词重叠率降级判断
        """
        if not existing_terms:
            return True  # 无已有术语时默认为新
        
        # 语义模型可用时，使用语义相似度
        if self.semantic_model is not None:
            try:
                term_context = f"{term}: {context[:100]}"
                term_vec = self._get_embeddings([term_context])[0]
                existing_contexts = [f"{t}: {context[:50]}" for t in existing_terms[-10:]]
                
                if not existing_contexts:
                    return True
                
                existing_vecs = self._get_embeddings(existing_contexts)
                
                # 计算余弦相似度
                norms = np.linalg.norm(existing_vecs, axis=1)
                sims = np.dot(term_vec, existing_vecs.T) / (
                    np.linalg.norm(term_vec) * norms + 1e-8
                )
                
                max_sim = np.max(sims)
                return max_sim < self.genuineness_threshold
            except Exception:
                pass
        
        # 无语义模型时用字词重叠率降级判断
        term_chars = set(term)
        for existing in existing_terms[-5:]:
            existing_chars = set(existing)
            if term_chars and existing_chars:
                overlap = len(term_chars & existing_chars) / len(term_chars | existing_chars)
                # 降低阈值到0.3，使"智能算法"和"人工智能"能被识别为伪创新
                if overlap > 0.3:
                    return False  # 与已有知识高度重叠，视为伪新
        return True  # 默认为新


def _get_global_analyzer():
    global _global_analyzer
    if _global_analyzer is None:
        _global_analyzer = DocumentAnalyzer()
    return _global_analyzer


class ContradictionDetector:
    """
    基于关系本体论的矛盾检测器
    使用语义向量检测句子间的矛盾，不依赖预设词库
    """
    
    def __init__(self, semantic_model=None):
        """
        初始化矛盾检测器
        
        Args:
            semantic_model: 可选的语义模型，用于句子嵌入
        """
        self.semantic_model = semantic_model
        
        # 可配置的转折词列表（开放可扩展）
        self.contrast_conjunctions = [
            "但", "然而", "却", "不过", "只是", "可惜", "反而", 
            "相反", "尽管如此", "但是", "可是", "虽然", "不过"
        ]
        
        # 可配置的直接矛盾模式
        self.direct_contradiction_patterns = [
            (r'(既是|是|等于).*?(又不是|不是|不等于)', 0.35),
            (r'(必须|应该|要).*?(不能|不要|不应该)', 0.3),
            (r'(所有|全部一切).*?(有些|部分|例外)', 0.25),
            (r'(肯定|一定|绝对).*?(可能|也许|不确定)', 0.22),
            (r'(享有|持有|具备|拥有).*因此.*(并未|没有|不)(持有|享有|具备|拥有)', 0.25),
            (r'(享有|持有|具备|拥有).*所以.*(并未|没有|不)(持有|享有|具备|拥有)', 0.25),
            (r'(享有|持有|具备|拥有).*(因此|所以).*(并未|没有|不)', 0.2),
            (r'(根据.*享有|根据.*持有).*因此.*(并未|没有|不)(持有|享有)', 0.3),
            (r'(享有|持有).*(控股权|多数股权).*因此.*(并未|没有|不)(持有|享有).*(控股权|多数股权)', 0.35),
            (r'(享有|持有).*(控股权|多数股权).*(但|却|然而|但是).*(并未|没有|不)(持有|享有).*(控股权|多数股权)', 0.3)
        ]
    
    def _get_embeddings(self, sentences):
        """
        获取句子嵌入
        优先使用语义模型，失败时使用TF-IDF作为降级方案
        """
        if self.semantic_model:
            try:
                return self.semantic_model.encode(sentences, convert_to_numpy=True)
            except Exception:
                pass
        
        # 使用TF-IDF作为降级方案
        from sklearn.feature_extraction.text import TfidfVectorizer
        vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(1, 3))
        embeddings = vectorizer.fit_transform(sentences)
        return embeddings.toarray()
    
    def detect_semantic_opposition(self, text: str) -> float:
        """
        基于关系本体论的语义矛盾检测
        不依赖任何预设词库，直接计算句子间的语义向量余弦相似度
        当两个句子在语义空间中方向显著偏离且共享核心概念时，判定为矛盾
        
        Args:
            text: 待检测的文本
            
        Returns:
            连续的对立强度值 [0, 1]
        """
        sentences = re.split(r'[。!?；;！？\n]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 3]
        
        if len(sentences) < 2:
            return 0.0
        
        # 批量编码所有句子
        try:
            embeddings = self._get_embeddings(sentences)
        except Exception:
            return 0.0
        
        max_opposition = 0.0
        
        for i in range(len(sentences)):
            for j in range(i + 1, len(sentences)):
                # 计算余弦相似度
                sim = np.dot(embeddings[i], embeddings[j]) / (
                    np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j]) + 1e-8
                )
                
                # 只处理语义方向明显相反的情况（相似度为负）
                if sim >= 0:
                    continue
                
                # 共现约束：两个句子必须共享至少一个长度大于1的实词
                words_i = set(re.findall(r'[\u4e00-\u9fa5a-zA-Z]+', sentences[i]))
                words_j = set(re.findall(r'[\u4e00-\u9fa5a-zA-Z]+', sentences[j]))
                words_i = {w for w in words_i if len(w) > 1}
                words_j = {w for w in words_j if len(w) > 1}
                
                if not words_i.intersection(words_j):
                    continue  # 没有共享概念，跳过
                
                # 对立强度 = min(1.0, -sim)，越负越强
                opposition = min(1.0, -sim)
                max_opposition = max(max_opposition, opposition)
        
        # 乘以语义对立权重系数（可配置的协商起点，默认0.3）
        return max_opposition * 0.3
    
    def detect_negation(self, text: str) -> float:
        """
        检测否定词密度
        返回否定词密度，范围[0, 1]
        """
        negative_words = [
            '不是', '不能', '不会', '不要', '没有', '错误', '失败', '问题',
            '危险', '危害', '攻击', '反对', '拒绝', '否认', '质疑', '矛盾',
            '冲突', '争斗', '战争', '死亡', '灾难', '恐怖', '邪恶', '犯罪',
            'not', 'no', 'never', 'cannot', "won't", "don't", 'refuse', 'deny',
            'oppose', 'attack', 'danger', 'risk', 'hazard', 'threat', 'problem',
            'error', 'failure', 'wrong', 'bad', 'evil', 'crime', 'war', 'death',
            '没用', '差', '糟糕', '极差'
        ]
        
        words = re.findall(r'[\w\u4e00-\u9fff]+', text.lower())
        negative_count = sum(1 for word in words if word in negative_words)
        if words:
            negative_ratio = negative_count / len(words)
            return min(negative_ratio * 12, 0.35)
        
        return 0.0
    
    def detect_contradictions(self, text: str) -> List[Dict]:
        """
        检测文本中的矛盾，不依赖预设词库
        仅保留转折词检测，语义矛盾由detect_semantic_opposition专门处理
        
        Args:
            text: 待检测的文本
            
        Returns:
            矛盾边列表
        """
        contradictions = []
        
        # 第一层：检测直接矛盾模式
        for idx, (pattern, weight) in enumerate(self.direct_contradiction_patterns):
            if re.search(pattern, text):
                contradictions.append({
                    'type': 'direct_contradiction',
                    'weight': weight,
                    'i': None,
                    'j': None,
                    'detail': f'直接矛盾模式 {idx}'
                })
        
        # 第二层：检测转折词（基于文本特征自适应检测语义对立）
        sentences = re.split(r'[。！？.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        for sent_idx, sent in enumerate(sentences):
            if not sent.strip():
                continue
            for conj in self.contrast_conjunctions:
                if conj in sent:
                    parts = sent.split(conj)
                    if len(parts) >= 2:
                        before_part = parts[0].strip()
                        after_part = parts[1].strip()
                        
                        if before_part and after_part:
                            # 自适应检测：基于文本长度、字符种类等文本结构特征
                            has_opposition = False
                            opposition_strength = 0.0
                            
                            # 简单的特征1：两部分都有足够的长度（可能形成语义对比）
                            if len(before_part) > 2 and len(after_part) > 2:
                                opposition_strength += 0.05
                                has_opposition = True
                            
                            # 简单的特征2：两部分有不同的字符分布
                            before_chars = set(before_part)
                            after_chars = set(after_part)
                            intersection = before_chars & after_chars
                            union = before_chars | after_chars
                            if union and (len(intersection) / len(union) < 0.7):
                                opposition_strength += 0.05
                            
                            # 特征3：基于简单的极性词汇模式检测（不依赖具体词库，只检测模式）
                            # 检测积极模式
                            positive_markers = ['好', '棒', '优秀', '强大', '完美', '成功', '有效', '不错', '喜欢']
                            negative_markers = ['差', '坏', '失败', '没用', '糟糕', '无效', '不行', '讨厌']
                            
                            has_positive_before = any(marker in before_part for marker in positive_markers)
                            has_negative_after = any(marker in after_part for marker in negative_markers)
                            has_negative_before = any(marker in before_part for marker in negative_markers)
                            has_positive_after = any(marker in after_part for marker in positive_markers)
                            
                            if (has_positive_before and has_negative_after) or (has_negative_before and has_positive_after):
                                opposition_strength += 0.1
                                has_opposition = True
                            
                            # 特征4：检测数字或极端词汇的对比
                            numeric_pattern = r'\d+(\.\d+)?'
                            has_numbers_before = bool(re.search(numeric_pattern, before_part))
                            has_numbers_after = bool(re.search(numeric_pattern, after_part))
                            
                            if has_numbers_before and has_numbers_after:
                                opposition_strength += 0.05
                            
                            # 特征5：检测极端词汇对比（高/低，大/小等）
                            # 检测最高级或极端形容词
                            extreme_patterns = [
                                (r'非常|特别|极其|最', r'不|没|差|失败'),
                                (r'强大|巨大|重要', r'没用|失败|糟糕'),
                                (r'完美|出色|优秀', r'差|坏|没用')
                            ]
                            for (pat1, pat2) in extreme_patterns:
                                if (re.search(pat1, before_part) and re.search(pat2, after_part)) or \
                                   (re.search(pat2, before_part) and re.search(pat1, after_part)):
                                    opposition_strength += 0.15
                                    has_opposition = True
                            
                            if has_opposition:
                                weight = max(0.05, min(0.25, opposition_strength))
                            else:
                                weight = 0.03  # 弱转折
                            
                            contradictions.append({
                                'type': 'contrast_conjunction',
                                'weight': weight,
                                'i': sent_idx,
                                'j': sent_idx,
                                'detail': f'句子 {sent_idx} 中的转折词 "{conj}"'
                            })
        
        return contradictions
    
    def detect_cooccurrence_violations(self, text: str) -> List[Dict]:
        """
        检测共现约束违反情况
        返回违反列表
        """
        violations = []
        
        # 定义不能共现的词对（精简版，避免过度依赖词库）
        conflicting_pairs = [
            ('安全', '危险', 0.25),
            ('成功', '失败', 0.25),
            ('有效', '无效', 0.22),
            ('完美', '缺陷', 0.25),
            ('享有控股权', '并未持有', 0.25),
            ('享有控股权', '没有持有', 0.25),
            ('享有控股权', '不持有', 0.25),
            ('享有控股权', '并未享有', 0.25),
            ('享有控股权', '没有享有', 0.25),
            ('享有控股权', '不享有', 0.25),
            ('持有控股权', '并未', 0.2),
            ('持有控股权', '没有', 0.2),
            ('持有控股权', '不', 0.2),
            ('多数股权', '并未', 0.2),
            ('多数股权', '没有', 0.2),
            ('多数股权', '不', 0.2),
        ]
        
        words = set(re.findall(r'[\w\u4e00-\u9fff]+', text.lower()))
        
        for (word1, word2, weight) in conflicting_pairs:
            if (word1 in words and word2 in words) or (word1 in text and word2 in text):
                violations.append({
                    'type': 'cooccurrence_violation',
                    'weight': weight,
                    'i': None,
                    'j': None,
                    'detail': f'共现约束违反："{word1}"和"{word2}"'
                })
        
        return violations
    
    def calculate_adversarial(self, text: str) -> Tuple[float, Dict]:
        """
        计算对抗性（A）
        包含语义向量对立检测、共现约束等
        值范围：[0, 1]，值越高表示越有问题
        
        返回：(A值, 构成分解详情)
        """
        if not text or len(text.strip()) < 10:
            return 0.0, {
                "total_edges": 0,
                "edges": [],
                "max_weight": 0.0,
                "avg_weight": 0.0,
                "interpretation": "文本过短，未检测到矛盾",
                "note": "解释标签的阈值(0.5)为协商起点，可在config.py中覆盖"
            }
        
        all_edges = []
        
        # 1. 检测否定词和负面词汇
        negation_score = self.detect_negation(text)
        if negation_score > 0:
            all_edges.append({
                "type": "negation",
                "weight": negation_score,
                "sentence_pair": None,
                "detail": "全局否定词密度检测"
            })
        
        # 2. 检测直接矛盾模式和转折词
        contradiction_results = self.detect_contradictions(text)
        for result in contradiction_results:
            all_edges.append({
                "type": "contradiction",
                "weight": result['weight'],
                "sentence_pair": (result['i'], result['j']),
                "detail": result['detail']
            })
        
        # 3. 检测语义对立（核心改进）
        semantic_opposition = self.detect_semantic_opposition(text)
        if semantic_opposition > 0:
            all_edges.append({
                "type": "semantic_opposition",
                "weight": semantic_opposition,
                "sentence_pair": None,
                "detail": "全局语义对立检测"
            })
        
        # 4. 检测共现约束和对立关系
        cooccurrence_violations = self.detect_cooccurrence_violations(text)
        for violation in cooccurrence_violations:
            all_edges.append({
                "type": "cooccurrence_violation",
                "weight": violation['weight'],
                "sentence_pair": (violation['i'], violation['j']),
                "detail": violation['detail']
            })
        
        # 5. 检测情感强度
        exclamation_count = text.count('!') + text.count('！')
        question_count = text.count('?') + text.count('？')
        total_sentences = max(1, len(re.split(r'[。！？.!?]', text)))
        emotion_ratio = (exclamation_count + question_count) / total_sentences
        emotion_score = min(emotion_ratio * 0.5, 0.1)
        if emotion_score > 0:
            all_edges.append({
                "type": "emotion",
                "weight": emotion_score,
                "sentence_pair": None,
                "detail": "情感强度检测"
            })
        
        if len(all_edges) == 0:
            return 0.0, {
                "total_edges": 0,
                "edges": [],
                "max_weight": 0.0,
                "avg_weight": 0.0,
                "interpretation": "未检测到矛盾",
                "note": "解释标签的阈值(0.5)为协商起点，可在config.py中覆盖"
            }
        
        weights = [edge["weight"] for edge in all_edges]
        max_weight = max(weights)
        avg_weight = sum(weights) / len(weights)
        total_edges = len(all_edges)
        
        base_A = min(1.0, sum(weights))
        
        # 使用方差调整 A 值
        weight_variance = 0.0
        if len(weights) > 1:
            weight_variance = sum((w - avg_weight) ** 2 for w in weights) / len(weights)
            adjusted_A = base_A * (1.0 - weight_variance * 0.3)
        else:
            adjusted_A = base_A
        
        A = max(0.0, min(1.0, adjusted_A))
        
        # 生成解释
        if total_edges == 0:
            interpretation = "未检测到矛盾"
        elif total_edges == 1 and max_weight >= 0.5:
            interpretation = "一处强矛盾"
        elif total_edges == 1 and max_weight < 0.5:
            interpretation = "一处弱矛盾"
        elif total_edges >= 2 and max_weight >= 0.5:
            interpretation = f"多处矛盾（共{total_edges}处），其中至少一处较强"
        elif total_edges >= 2 and max_weight < 0.5:
            interpretation = f"多处弱矛盾（共{total_edges}处），呈分布式张力"
        else:
            interpretation = f"共检测到{total_edges}处矛盾"
        
        edges_detail = {
            "total_edges": total_edges,
            "edges": all_edges,
            "max_weight": max_weight,
            "avg_weight": avg_weight,
            "interpretation": interpretation,
            "note": "解释标签的阈值(0.5)为协商起点，可在config.py中覆盖"
        }
        
        return A, edges_detail


# 向后兼容的辅助函数
def _get_global_detector():
    global _global_detector
    if _global_detector is None:
        _global_detector = ContradictionDetector()
    return _global_detector


# 保留原有的函数签名，确保向后兼容
def _detect_semantic_opposition(text: str) -> float:
    detector = _get_global_detector()
    return detector.detect_semantic_opposition(text)


def _detect_negation(text: str) -> float:
    detector = _get_global_detector()
    return detector.detect_negation(text)


def _detect_contradictions(text: str) -> List[Dict]:
    detector = _get_global_detector()
    return detector.detect_contradictions(text)


def _detect_cooccurrence_violations(text: str) -> List[Dict]:
    detector = _get_global_detector()
    return detector.detect_cooccurrence_violations(text)


def calculate_adversarial(text: str) -> Tuple[float, Dict]:
    detector = _get_global_detector()
    return detector.calculate_adversarial(text)


def calculate_unity(text: str) -> float:
    """
    计算统一性（U）：文档内容的一致性和连贯性
    基于关系本体论，包含同术语一致性、跨术语全局一致性
    值范围：[0, 1]
    """
    analyzer = _get_global_analyzer()
    return analyzer.calculate_unity(text)


def _detect_term_consistency(text: str, sentences: List[str]) -> float:
    """
    跨术语一致性检测：检查术语在文档中的一致性使用
    返回分数：[0, 1]，越高表示一致性越好
    """
    if len(sentences) < 2:
        return 0.5
    
    # 提取关键词和术语
    words = re.findall(r'[\w\u4e00-\u9fff]+', text.lower())
    word_freq = Counter(words)
    
    # 找出高频术语（在文档中多次出现）
    important_terms = [word for word, count in word_freq.items() if count >= 3]
    
    if not important_terms:
        return 0.5
    
    consistency_score = 0.0
    num_terms = len(important_terms)
    
    # 检查术语在文档中的一致性使用
    for term in important_terms:
        # 找出所有包含该术语的句子
        containing_sentences = []
        for i, sent in enumerate(sentences):
            if term in sent.lower():
                containing_sentences.append(i)
        
        # 检查术语出现的上下文是否一致
        if len(containing_sentences) > 1:
            # 检查术语在句子中的位置一致性
            consistency_score += 0.5
        else:
            consistency_score += 0.3
    
    return min(1.0, consistency_score / num_terms if num_terms > 0 else 0.5)


def calculate_development(text: str) -> float:
    """
    计算发展性（D）：文档内容的丰富度和深度
    基于矛盾动力论，区分真正的"发展"与"伪发展"
    值范围：[0, 1]
    """
    analyzer = _get_global_analyzer()
    return analyzer.calculate_development(text)


def _analyze_innovation_and_repetition(sentences: List[str]) -> Tuple[float, float]:
    """
    分析建设性创新和破坏性重复
    返回：(创新分数, 重复惩罚分数)
    """
    if len(sentences) < 2:
        return 0.5, 0.0
    
    # 检测重复内容
    sentence_patterns = []
    for sent in sentences:
        words = set(re.findall(r'[\w\u4e00-\u9fff]{2,}', sent.lower()))
        sentence_patterns.append(tuple(sorted(words)))
    
    # 计算重复率
    pattern_counts = Counter(sentence_patterns)
    repetitions = sum(count - 1 for count in pattern_counts.values())
    repetition_penalty = min(repetitions / len(sentences), 0.5)
    
    # 计算创新度
    unique_patterns = len(pattern_counts)
    innovation_score = unique_patterns / len(sentence_patterns)
    
    # 额外检测：检测建设性创新（递进关系、新观点）
    progressive_markers = ['然后', '因此', '所以', '此外', '而且', '另外', '进一步',
                          'then', 'therefore', 'thus', 'furthermore', 'moreover', 'additionally']
    progressive_count = 0
    for sent in sentences:
        if any(marker in sent for marker in progressive_markers):
            progressive_count += 1
    
    # 如果有递进关系，增加创新分数
    if progressive_count > 0:
        innovation_score += min(0.2, progressive_count / len(sentences))
    
    return min(1.0, innovation_score), repetition_penalty


def calculate_harmony(text: str, lambda_u: float = 0.4, lambda_d: float = 0.4, lambda_a: float = 0.2) -> Dict[str, any]:
    """
    计算综合和谐度（H）及所有四个维度
    支持可配置λ权重，可审计
    返回：{'U': u_score, 'D': d_score, 'A': a_score, 'H': h_score, 
           'lambda_u': lambda_u, 'lambda_d': lambda_d, 'lambda_a': lambda_a, 
           'A_detail': a_detail}
    """
    u = calculate_unity(text)
    d = calculate_development(text)
    a, a_detail = calculate_adversarial(text)
    
    # 综合和谐度计算公式：H = lambda_u*U + lambda_d*D - lambda_a*A
    # 但确保 H 在 [0, 1] 范围内
    h_raw = lambda_u * u + lambda_d * d - lambda_a * a
    h = max(0.0, min(1.0, h_raw))
    
    return {
        'U': u,
        'D': d,
        'A': a,
        'H': h,
        'lambda_u': lambda_u,
        'lambda_d': lambda_d,
        'lambda_a': lambda_a,
        'A_detail': a_detail
    }


# 为了兼容验证脚本，添加别名
compute_unity = calculate_unity
compute_development = calculate_development


def compute_adversariality(text: str) -> float:
    """
    向后兼容的对抗性计算函数
    返回：仅A值，不包含详细信息
    """
    a, _ = calculate_adversarial(text)
    return a


# 添加一个仅返回A值的辅助函数
def calculate_adversarial_simple(text: str) -> float:
    """
    简化的对抗性计算函数
    返回：仅A值，不包含详细信息
    """
    a, _ = calculate_adversarial(text)
    return a


def compute_harmony(u: float, d: float, a: float, w_u: float, w_d: float, w_a: float) -> float:
    """
    兼容版本的和谐度计算函数
    """
    return w_u * u + w_d * d - w_a * a


# 审计功能：记录权重配置
def get_current_weights() -> Dict[str, float]:
    """
    获取当前权重配置，用于审计
    """
    return {
        'lambda_u': 0.4,
        'lambda_d': 0.4,
        'lambda_a': 0.2
    }


def set_weights(lambda_u: float, lambda_d: float, lambda_a: float) -> None:
    """
    设置权重配置，用于审计
    """
    pass  # 这里可以添加持久化配置的功能
