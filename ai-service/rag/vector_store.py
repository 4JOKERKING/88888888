"""
RAG 向量检索 — 双模支持

模式1: TF-IDF（默认，纯离线，零下载）
模式2: sentence-transformers embedding（需下载中文模型，约400MB）

自动检测: 如果 sentence-transformers 可用 → 用模式2，否则 → 模式1
"""

import os
import re
import json
import pickle
import numpy as np
from pathlib import Path

VECTOR_DIR = Path(__file__).parent.parent / "vector_data"
KNOWLEDGE_DIR = Path(__file__).parent.parent / "data" / "knowledge"

# --- 内部状态 ---
class _RAGState:
    def __init__(self):
        self.vectorizer = None       # TF-IDF
        self.doc_vectors = None      # sparse (TF-IDF) or dense (embedding)
        self.doc_chunks = []
        self.doc_sources = []
        self.embedding_model = None  # sentence-transformers model
        self.mode = "tfidf"

    @property
    def ready(self):
        return (self.vectorizer is not None and self.doc_vectors is not None)

_state = _RAGState()


# --- 分块 ---
def _chunk_text(text: str, chunk_size: int = 500) -> list[str]:
    paragraphs = text.split("\n\n")
    chunks = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(para) <= chunk_size:
            chunks.append(para)
        else:
            sentences = re.split(r'(?<=[。！？；\n])', para)
            current = ""
            for sent in sentences:
                if len(current) + len(sent) <= chunk_size:
                    current += sent
                else:
                    if current.strip():
                        chunks.append(current.strip())
                    current = sent
            if current.strip():
                chunks.append(current.strip())
    return chunks


# --- 构建 ---
def build_index():
    _load_documents()

    if not _state.doc_chunks:
        print("[RAG] No documents found")
        return False

    # 尝试用 embedding 模型
    try:
        return _build_with_embedding()
    except Exception as e:
        print(f"[RAG] Embedding not available ({e}), using TF-IDF")

    return _build_with_tfidf()


def _build_with_tfidf():
    from sklearn.feature_extraction.text import TfidfVectorizer
    vec = TfidfVectorizer(max_features=2000, analyzer='char_wb', ngram_range=(2, 4))
    _state.doc_vectors = vec.fit_transform(_state.doc_chunks)
    _state.vectorizer = vec
    _state.mode = "tfidf"
    _save()
    print(f"[RAG] TF-IDF index built: {len(_state.doc_chunks)} vectors, dim={vec.get_feature_names_out().shape[0]}")
    return True


def _build_with_embedding():
    from sentence_transformers import SentenceTransformer
    import os

    # 优先用本地缓存的模型（ModelScope下载的），否则从HF下载
    local_path = os.path.expanduser(
        r"~\.cache\modelscope\models\iic--nlp_corom_sentence-embedding_chinese-base\snapshots\master"
    )
    model_path = local_path if os.path.exists(local_path) else "shibing624/text2vec-base-chinese"
    print(f"[RAG] Loading embedding model ({model_path})...")
    model = SentenceTransformer(model_path)

    print(f"[RAG] Encoding {len(_state.doc_chunks)} chunks...")
    embeddings = model.encode(_state.doc_chunks, show_progress_bar=True)

    _state.embedding_model = model
    _state.doc_vectors = embeddings  # numpy array [N, 768]
    _state.vectorizer = model  # reuse field
    _state.mode = "embedding"
    _save()
    print(f"[RAG] Embedding index built: {len(_state.doc_chunks)} vectors, dim=768")
    return True


def _load_documents():
    vectors_exist = all(
        (VECTOR_DIR / f).exists()
        for f in ["chunks.json"]
    )

    if vectors_exist:
        # 加载已有分块
        with open(VECTOR_DIR / "chunks.json", "r", encoding="utf-8") as f:
            info = json.load(f)
            _state.doc_chunks = info["chunks"]
            _state.doc_sources = info["sources"]
        return

    # 首次构建: 从知识文档加载
    if not KNOWLEDGE_DIR.exists():
        return

    for filename in sorted(os.listdir(KNOWLEDGE_DIR)):
        if not filename.endswith(".txt"):
            continue
        filepath = KNOWLEDGE_DIR / filename
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        chunks = _chunk_text(text)
        _state.doc_chunks.extend(chunks)
        _state.doc_sources.extend([filename] * len(chunks))
        print(f"[RAG] {filename}: {len(chunks)} chunks")

    print(f"[RAG] Total: {len(_state.doc_chunks)} chunks")


def _save():
    VECTOR_DIR.mkdir(exist_ok=True)
    with open(VECTOR_DIR / "chunks.json", "w", encoding="utf-8") as f:
        json.dump({"chunks": _state.doc_chunks, "sources": _state.doc_sources}, f, ensure_ascii=False)

    if _state.mode == "tfidf":
        with open(VECTOR_DIR / "vectorizer.pkl", "wb") as f:
            pickle.dump(_state.vectorizer, f)
        from scipy.sparse import issparse
        if issparse(_state.doc_vectors):
            np.savez(VECTOR_DIR / "doc_vectors.npz", data=_state.doc_vectors.toarray())
    else:
        np.save(VECTOR_DIR / "embeddings.npy", _state.doc_vectors)


# --- 加载 ---
def load_index():
    try:
        # 尝试加载 embedding 版本
        emb_file = VECTOR_DIR / "embeddings.npy"
        chunks_file = VECTOR_DIR / "chunks.json"
        if emb_file.exists() and chunks_file.exists():
            from sentence_transformers import SentenceTransformer
            _state.embedding_model = SentenceTransformer("shibing624/text2vec-base-chinese")
            _state.doc_vectors = np.load(emb_file)
            _state.vectorizer = _state.embedding_model
            _state.mode = "embedding"
            with open(chunks_file, "r", encoding="utf-8") as f:
                info = json.load(f)
                _state.doc_chunks = info["chunks"]
                _state.doc_sources = info["sources"]
            print(f"[RAG] Embedding index loaded: {len(_state.doc_chunks)} vectors")
            return True
    except Exception as e:
        print(f"[RAG] Embedding load failed ({e}), trying TF-IDF")

    try:
        # 加载 TF-IDF 版本
        from scipy.sparse import csr_matrix
        with open(VECTOR_DIR / "vectorizer.pkl", "rb") as f:
            _state.vectorizer = pickle.load(f)
        data = np.load(VECTOR_DIR / "doc_vectors.npz")
        _state.doc_vectors = csr_matrix(data["data"])
        with open(VECTOR_DIR / "chunks.json", "r", encoding="utf-8") as f:
            info = json.load(f)
            _state.doc_chunks = info["chunks"]
            _state.doc_sources = info["sources"]
        _state.mode = "tfidf"
        print(f"[RAG] TF-IDF index loaded: {len(_state.doc_chunks)} vectors")
        return True
    except Exception as e:
        print(f"[RAG] TF-IDF load failed ({e}), rebuilding...")
        return build_index()


# --- 检索 ---
def search(query: str, k: int = 3) -> list[dict]:
    if not _state.ready:
        if not load_index():
            return []

    if _state.mode == "embedding":
        return _search_embedding(query, k)
    else:
        return _search_tfidf(query, k)


def _search_embedding(query: str, k: int) -> list[dict]:
    from sklearn.metrics.pairwise import cosine_similarity
    q_vec = _state.embedding_model.encode([query])  # [1, 768]
    scores = cosine_similarity(q_vec, _state.doc_vectors)[0]
    top_indices = scores.argsort()[-k:][::-1]

    results = []
    for idx in top_indices:
        s = float(scores[idx])
        if s > 0.1:
            results.append({
                "content": _state.doc_chunks[idx],
                "source": _state.doc_sources[idx] if idx < len(_state.doc_sources) else "",
                "score": round(s, 4),
            })
    return results


def _search_tfidf(query: str, k: int) -> list[dict]:
    from sklearn.metrics.pairwise import cosine_similarity
    q_vec = _state.vectorizer.transform([query])
    scores = cosine_similarity(q_vec, _state.doc_vectors)[0]
    top_indices = scores.argsort()[-k:][::-1]

    results = []
    for idx in top_indices:
        s = float(scores[idx])
        if s > 0.001:
            results.append({
                "content": _state.doc_chunks[idx],
                "source": _state.doc_sources[idx] if idx < len(_state.doc_sources) else "",
                "score": round(s, 4),
            })
    return results


def is_available() -> bool:
    return _state.ready
