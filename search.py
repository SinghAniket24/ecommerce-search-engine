import re
import math
from typing import List, Dict
from sentence_transformers import SentenceTransformer, util

from database import get_products_list

# --- Configuration ---


RELEVANCE_THRESHOLD = 0.30

INTENT_CHEAP = ["cheap", "budget", "sasta", "low price", "affordable"]
INTENT_PREMIUM = ["premium", "expensive", "flagship", "pro", "max", "ultra"]
INTENT_LATEST = ["latest", "new", "2024", "2025", "gen", "generation"]


# --- Query Parser ---

class QueryParser:

    def __init__(self, query: str):
        self.raw_query = query.lower()
        self.clean_query = self.raw_query
        
        self.filters = {
            "max_price": None,
            "storage": None,
            "color": None,
            "sort": None
        }
        
        self.boosts = {
            "is_latest": False,
            "is_premium": False
        }

    def parse(self):
        self.extract_price()
        self.extract_storage()
        self.extract_color()
        self.extract_intents()
        return self

    def extract_price(self):
        match = re.search(r'(?:under|below|<)\s?(\d+)', self.clean_query)
        if match:
            self.filters["max_price"] = int(match.group(1))
            self.filters["sort"] = "asc"

    def extract_storage(self):
        match = re.search(r'(\d+)\s?(gb|tb)', self.clean_query)
        if match:
            val = int(match.group(1))
            unit = match.group(2)
            if unit == "tb":
                val *= 1024
            self.filters["storage"] = val

    def extract_color(self):
        colors = ["black", "white", "blue", "red", "green", "gold", "silver"]
        for color in colors:
            if f" {color} " in f" {self.clean_query} ":
                self.filters["color"] = color

    def extract_intents(self):
        if any(w in self.clean_query for w in INTENT_CHEAP):
            self.filters["sort"] = "asc"
        if any(w in self.clean_query for w in INTENT_PREMIUM):
            self.boosts["is_premium"] = True
        if any(w in self.clean_query for w in INTENT_LATEST):
            self.boosts["is_latest"] = True


# --- Ranking Engine (Hybrid Semantic Search) ---

class SemanticSearchRanker:

    _instance = None
    _model = None
    _product_embeddings = None
    _cached_products = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SemanticSearchRanker, cls).__new__(cls)
            print("--- Loading Semantic LLM (all-MiniLM-L6-v2) ---")
            cls._model = SentenceTransformer('all-MiniLM-L6-v2')
            cls._refresh_index()
        return cls._instance

    @classmethod
    def _refresh_index(cls):
        products = get_products_list()
        cls._cached_products = products
        
        corpus = [
            f"{p['title']} {p.get('description', '')}"
            for p in products
        ]
        
        if corpus:
            cls._product_embeddings = cls._model.encode(corpus, convert_to_tensor=True)
        else:
            cls._product_embeddings = None

    def search(self, raw_query: str):
        if not raw_query or not self._cached_products or self._product_embeddings is None:
            return []

        parser = QueryParser(raw_query).parse()
        
        # Convert user query to vector embedding
        query_embedding = self._model.encode(raw_query, convert_to_tensor=True)
        
        # Calculate semantic similarity scores for all products
        cos_scores = util.cos_sim(query_embedding, self._product_embeddings)[0]

        ranked_results = []

        for idx, score_tensor in enumerate(cos_scores):
            
            semantic_score = float(score_tensor)
            product = self._cached_products[idx]

            # 1. HARD FILTERING
            if semantic_score < RELEVANCE_THRESHOLD:
                continue

            # Scale LLM score to a base of 0-100
            score = semantic_score * 100
            metadata = product.get("metadata", {})
            title_lower = product["title"].lower()
            query_lower = raw_query.lower()

            if query_lower in title_lower:
                score += 50  
            else:
                words = query_lower.split()
                for w in words:
                    if len(w) > 2 and w in title_lower:
                        score += 15  # Partial boost for single word match

            # ATTRIBUTE MATCHING
            attr_score = 0
            if parser.filters["storage"]:
                if str(parser.filters["storage"]) in title_lower:
                    attr_score += 15

            if parser.filters["color"]:
                if parser.filters["color"] in title_lower:
                    attr_score += 15

            if parser.filters["max_price"]:
                if product["price"] <= parser.filters["max_price"]:
                    attr_score += 10
                else:
                    attr_score -= 30 

            score += attr_score

            # POPULARITY
            units_sold = metadata.get("units_sold", 0)
            if units_sold > 0:
                score += math.log10(units_sold) * 10

            # Prevents corrupted database numbers (e.g., 4400000000) from breaking the math
            raw_rating = product.get("rating", 0)
            try:
                safe_rating = min(float(raw_rating), 5.0)
            except (ValueError, TypeError):
                safe_rating = 0.0
                
            score += safe_rating * 4

            # INTENT BOOST
            if parser.boosts["is_premium"]:
                if product["price"] > 50000:
                    score += 20

            if parser.boosts["is_latest"]:
                if re.search(r'202[4-5]|gen\s?\d', title_lower):
                    score += 20

            product_copy = product.copy()
            product_copy["_debug"] = {
                "semantic_score": round(semantic_score, 3),
                "safe_rating_used": safe_rating,
                "ranking_score": round(score, 2)
            }

            ranked_results.append((score, product_copy))

        # Sort by final computed score
        ranked_results.sort(key=lambda x: x[0], reverse=True)

        # Return top 20 results to avoid massive payloads
        return [p[1] for p in ranked_results[:20]]


# --- MAIN FUNCTION FOR FASTAPI ---

search_engine = SemanticSearchRanker()

def search_products_logic(query: str):
    return search_engine.search(query)

def refresh_search_index():
    search_engine._refresh_index()