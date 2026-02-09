import re
import math
from typing import List, Dict
from rapidfuzz import fuzz
from rank_bm25 import BM25Okapi

from database import get_products_list


# --- Configuration ---

SYNONYMS = {
    "mobile": "smartphone",
    "cell": "smartphone",
    "phone": "smartphone",
    "tv": "television",
    "laptop": "notebook",
    "earbuds": "headphones",
    "earphone": "headphones"
}

STOPWORDS = {"a", "an", "the", "in", "on", "for", "of", "with", "buy", "best", "online"}

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
        self.clean_text()
        
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
            if color in self.clean_query:
                self.filters["color"] = color


    def extract_intents(self):
        
        if any(w in self.clean_query for w in INTENT_CHEAP):
            self.filters["sort"] = "asc"
            
        if any(w in self.clean_query for w in INTENT_PREMIUM):
            self.boosts["is_premium"] = True
            
        if any(w in self.clean_query for w in INTENT_LATEST):
            self.boosts["is_latest"] = True


    def clean_text(self):
        
        text = re.sub(r'[^a-z0-9\s]', '', self.clean_query)
        
        words = text.split()
        
        words = [
            SYNONYMS.get(w, w)
            for w in words
            if w not in STOPWORDS
        ]
        
        self.clean_query = " ".join(words)


# --- Ranking Engine ---

class SearchRanker:

    def __init__(self, products: List[Dict]):
        
        self.products = products
        
        self.corpus = [
            self.tokenize(p["title"] + " " + p.get("description", ""))
            for p in products
        ]
        
        if len(self.corpus) > 0:
            self.bm25 = BM25Okapi(self.corpus)
        else:
            self.bm25 = None


    def tokenize(self, text: str):
        return text.lower().split()


    def search(self, raw_query: str):

        if not raw_query or len(self.products) == 0:
            return []

        parser = QueryParser(raw_query).parse()
        
        query_tokens = self.tokenize(parser.clean_query)

        if len(query_tokens) == 0:
            return []

        if self.bm25:
            bm25_scores = self.bm25.get_scores(query_tokens)
        else:
            bm25_scores = [0] * len(self.products)


        ranked_results = []


        for idx, product in enumerate(self.products):

            score = 0

            metadata = product.get("metadata", {})


            # TEXT RELEVANCE

            bm25_score = bm25_scores[idx]

            fuzzy_score = fuzz.partial_ratio(
                parser.clean_query,
                product["title"].lower()
            ) / 100

            text_score = bm25_score * 0.7 + fuzzy_score * 0.3

            score += text_score * 40


            # ATTRIBUTE MATCHING

            attr_score = 0

            if parser.filters["storage"]:
                if str(parser.filters["storage"]) in product["title"]:
                    attr_score += 1

            if parser.filters["color"]:
                if parser.filters["color"] in product["title"].lower():
                    attr_score += 1

            if parser.filters["max_price"]:
                if product["price"] <= parser.filters["max_price"]:
                    attr_score += 1
                else:
                    attr_score -= 2

            score += attr_score * 30


            # POPULARITY

            units_sold = metadata.get("units_sold", 0)

            if units_sold > 0:
                score += math.log10(units_sold) * 10

            score += product.get("rating", 0) * 4


            # INTENT BOOST

            if parser.boosts["is_premium"]:
                if product["price"] > 50000:
                    score += 20

            if parser.boosts["is_latest"]:
                if re.search(r'202[4-5]|gen\s?\d', product["title"].lower()):
                    score += 20


            product_copy = product.copy()

            product_copy["_debug"] = {
                "ranking_score": round(score, 2)
            }

            ranked_results.append((score, product_copy))


        ranked_results.sort(key=lambda x: x[0], reverse=True)

        return [p[1] for p in ranked_results]


# --- MAIN FUNCTION FOR FASTAPI ---

def search_products_logic(query: str):

    products = get_products_list()

    engine = SearchRanker(products)

    return engine.search(query)
