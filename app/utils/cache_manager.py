# utils/cache_manager.py

import os
import json
import hashlib
from datetime import datetime
from collections import OrderedDict
from sentence_transformers import SentenceTransformer, util

CACHE_FILE = "data/query_cache.json"
MAX_CACHE_SIZE = 50
SIMILARITY_THRESHOLD = 0.85

model = SentenceTransformer("all-MiniLM-L6-v2")

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
    return use_case in PUBLIC_USE_CASES


class GlobalCache:
    _cache = OrderedDict()

    @classmethod
    def _load(cls):
        if not cls._cache and os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r") as f:
                    cls._cache = json.load(f, object_pairs_hook=OrderedDict)
            except Exception:
                cls._cache = OrderedDict()

    @classmethod
    def _save(cls):
        with open(CACHE_FILE, "w") as f:
            json.dump(cls._cache, f, indent=2)

    @classmethod
    def _is_similar(cls, query):
        query_emb = model.encode(query, convert_to_tensor=True)
        for cached_q in cls._cache.keys():
            cached_emb = model.encode(cached_q, convert_to_tensor=True)
            sim_score = util.cos_sim(query_emb, cached_emb).item()
            if sim_score >= SIMILARITY_THRESHOLD:
                return cached_q
        return None

    @classmethod
    def get(cls, query):
        cls._load()
        match = cls._is_similar(query)
        if match:
            cls._cache.move_to_end(match)
            return cls._cache[match]["response"]
        return None

    @classmethod
    def get_metadata(cls, query):
        cls._load()
        match = cls._is_similar(query)
        if match:
            return cls._cache[match]
        return None

    @classmethod
    def set(cls, query, response, source="Unknown", use_case=None, validated=False):
        cls._load()
        if cls._is_similar(query):
            return

        if len(cls._cache) >= MAX_CACHE_SIZE:
            cls._cache.popitem(last=False)

        cls._cache[query] = {
            "query": query,
            "response": response,
            "source": source,
            "use_case": use_case,
            "validated": validated,
            "timestamp": datetime.now().isoformat()
        }
        cls._save()

    @classmethod
    def list_recent(cls, n=5):
        cls._load()
        return list(cls._cache.items())[-n:]

