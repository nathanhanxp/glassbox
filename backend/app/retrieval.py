"""BM25. MiniLM is not loaded. The linker uses this for ambiguous cross-company pairs."""

import re

from rank_bm25 import BM25Okapi

TOKEN = re.compile(r"[a-z0-9]+")
STOP = {
    "the", "and", "for", "that", "with", "from", "this", "were", "was", "are", "its",
    "our", "their", "have", "has", "had", "not", "but", "you", "your", "into", "over",
    "than", "then", "them", "they", "been", "will", "would", "about", "after", "before",
    "quarter", "billion", "million", "percent", "year", "versus", "prior",
}


def tokenize(text: str) -> list[str]:
    return [t for t in TOKEN.findall((text or "").lower()) if t not in STOP and len(t) > 2]


def bm25_pairs(texts: list[str]) -> list[list[float]]:
    docs = [tokenize(t) or ["empty"] for t in texts]
    model = BM25Okapi(docs)
    return [model.get_scores(doc).tolist() for doc in docs]
