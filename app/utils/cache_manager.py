import os
import json
import hashlib
from collections import OrderedDict
from sentence_transformers import SentenceTransformer, util

CACHE_FILE = "data/query_cache.json"
MAX_CACHE_SIZE = 50  # Tune based on memory/performance
model = SentenceTransformer("all-MiniLM-L6-v2")  # Used for semantic deduplication

class GlobalCache:
    def __init__(self):
        self.cache = self._load_cache()

    def _load_cache(self):
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r") as f:
                    return json.load(f, object_pairs_hook=OrderedDict)
            except:
                return OrderedDict()
        return OrderedDict()

    def _save_cache(self):
        with open(CACHE_FILE, "w") as f:
            json.dump(self.cache, f)

    def _hash(self, text):
        return hashlib.sha256(text.encode()).hexdigest()

    def _is_similar(self, query, threshold=0.85):
        query_emb = model.encode(query, convert_to_tensor=True)
        for cached_q in self.cache.keys():
            cached_emb = model.encode(cached_q, convert_to_tensor=True)
            sim_score = util.cos_sim(query_emb, cached_emb).item()
            if sim_score >= threshold:
                return cached_q  # Return matching query
        return None

    def get(self, query):
        similar_query = self._is_similar(query)
        if similar_query:
            # Move to end to simulate LRU
            self.cache.move_to_end(similar_query)
            return self.cache[similar_query]
        return None

    def add(self, query, response):
        if self._is_similar(query):
            return  # Don't store duplicates

        if len(self.cache) >= MAX_CACHE_SIZE:
            self.cache.popitem(last=False)  # Remove oldest (LRU)

        self.cache[query] = response
        self._save_cache()
