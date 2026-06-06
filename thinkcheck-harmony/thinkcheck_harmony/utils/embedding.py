'''嵌入模型封装（带缓存）'''
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from ..config import EMBEDDING_MODEL

_model = None

def get_model():
    global _model
    if _model is None:
        # 延迟导入 sentence_transformers，避免在导入阶段不立即失败
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model

def get_embeddings_tfidf(sentences):
    """使用 TF-IDF 生成句子嵌入（轻量级降级方案，无需 torch）"""
    vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(1, 3))
    embeddings = vectorizer.fit_transform(sentences)
    return embeddings.toarray()

def get_embeddings(sentences):
    try:
        model = get_model()
        return model.encode(sentences)
    except Exception as e:
        print(f"[ThinkCheck] 警告：无法加载语义模型，自动降级为轻量级引擎。错误: {e}")
        return get_embeddings_tfidf(sentences)
