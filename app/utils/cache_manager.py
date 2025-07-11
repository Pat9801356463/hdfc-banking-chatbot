# utils/cache_manager.py

import os
import json
import hashlib
from collections import OrderedDict
from sentence_transformers import SentenceTransformer, util

# Persistent file for cross-user public query cache
CACHE_FILE = "data/query_cache.json"
MAX_CACHE_SIZE = 50
SIMILARITY_THRESHOLD = 0.85

# Sentence Transformer for semantic deduplication
model = SentenceTransformer("all-MiniLM-L6-v2")

# --- Public Use Case Tags ---
PUBLIC_USE_CASES = {
    "Documentation & Process Query",
    "KYC & Details Update",
    "Download Statement & Document",
    "Investment (non-sharemarket)",
    "Banking Norms",
    "Loan Prepurchase Query",
    "Mutual Funds & Tax Benefits",
}

def is_public_query(intent, use_case):
    """
    Returns True if the query is classified as public (non-user-specific).
    """
    return use_case in PUBLIC_USE_CASES

# --- Global Cache Class ---
class GlobalCache:
    _cache = OrderedDict()

    @classmethod
    def _load(cls):
        if not cls._cache and os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r") as f:
                    data = json.load(f, object_pairs_hook=OrderedDict)
                    cls._cache = data
            except:
                cls._cache = OrderedDict()

    @classmethod
    def _save(cls):
        with open(CACHE_FILE, "w") as f:
            json.dump(cls._cache, f)

    @classmethod
    def _is_similar(cls, query):
        """
        Return a matching query key from cache if semantically similar.
        """
        query_emb = model.encode(query, convert_to_tensor=True)
        for existing_q in cls._cache.keys():
            cached_emb = model.encode(existing_q, convert_to_tensor=True)
            score = util.cos_sim(query_emb, cached_emb).item()
            if score >= SIMILARITY_THRESHOLD:
                return existing_q
        return None

    @classmethod
    def get(cls, query):
        cls._load()
        match = cls._is_similar(query)
        if match:
            cls._cache.move_to_end(match)
            return cls._cache[match]
        return None

    @classmethod
    def set(cls, query, response):
        cls._load()
        if cls._is_similar(query):  # avoid storing duplicates
            return

        if len(cls._cache) >= MAX_CACHE_SIZE:
            cls._cache.popitem(last=False)

        cls._cache[query] = response
        cls._save()
