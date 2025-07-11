# utils/cache_manager.py

import os
import json
import hashlib
from collections import OrderedDict
from sentence_transformers import SentenceTransformer, util

# File path for persistent cache
CACHE_FILE = "data/query_cache.json"
MAX_CACHE_SIZE = 50
SIMILARITY_THRESHOLD = 0.85

# Load semantic similarity model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Public use cases that qualify for global caching

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
    Determines whether a query is public and eligible for global caching.
    """
    return use_case in PUBLIC_USE_CASES
class GlobalCache:
    _cache = OrderedDict()

    @classmethod
    def _load(cls):
        if not cls._cache and os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r") as f:
                    cls._cache = json.load(f, object_pairs_hook=OrderedDict)
            except:
                cls._cache = OrderedDict()

    @classmethod
    def _save(cls):
        with open(CACHE_FILE, "w") as f:
            json.dump(cls._cache, f)

    @classmethod
    def _is_similar(cls, query):
        """
        Checks if a semantically similar query exists in cache.
        Returns matching query key if found.
        """
        query_emb = model.encode(query, convert_to_tensor=True)
        for cached_q in cls._cache.keys():
            cached_emb = model.encode(cached_q, convert_to_tensor=True)
            sim_score = util.cos_sim(query_emb, cached_emb).item()
            if sim_score >= SIMILARITY_THRESHOLD:
                return cached_q
        return None

    @classmethod
    def get(cls, query):
        """
        Returns cached response for a semantically similar query.
        """
        cls._load()
        match = cls._is_similar(query)
        if match:
            cls._cache.move_to_end(match)  # simulate LRU
            return cls._cache[match]
        return None

    @classmethod
    def set(cls, query, response):
        """
        Stores new query-response if not semantically similar to existing entries.
        """
        cls._load()
        if cls._is_similar(query):
            return  # avoid duplicates

        if len(cls._cache) >= MAX_CACHE_SIZE:
            cls._cache.popitem(last=False)  # remove least-recently used

        cls._cache[query] = response
        cls._save()
