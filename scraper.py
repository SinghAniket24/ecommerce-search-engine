import requests
from bs4 import BeautifulSoup
import time
import random
import sys

# Import your existing database functions
try:
    from database import init_db, add_product
except ImportError:
    print("Error: 'database.py' not found.")
    sys.exit(1)

init_db()

#
KEYWORDS = [
    "mobile phones", "laptops", "tablets", "smartwatch", "bluetooth speakers",
    "gaming consoles", "monitors", "cameras", "printers", "external hard drive",
    "power banks", "keyboard and mouse", "dslr camera", "home theater",
    "trimmers", "refrigerators", "washing machines", "microwave oven", "air conditioners"
]

TARGET_TOTAL = 1000 
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

class ProductDTO:
    def __init__(self, title, price, mrp, rating, category):
        self.title = title
        self.description = f"High-quality {title} from the {category} category. Best price and performance."
        self.rating = rating
        self.stock = random.randint(5, 100)
        self.price = price
        self.mrp = mrp
        self.currency = "INR"

def clean_price(price_str):
    if not price_str: return 0
    clean = "".join(filter(str.isdigit, price_str))
    return int(clean) if clean else 0

def run_scraper():
    print(f"--- Running Large Scale Scraper (Goal: {TARGET_TOTAL} products) ---")
    total_added = 0

    for query in KEYWORDS:
        if total_added >= TARGET_TOTAL:
            break
            
        print(f"\n[!] Switching Category: {query.upper()}")
        
        # We scrape up to 5 pages per keyword (approx 100 products per keyword)
        for offset in range(0, 100, 20):
            if total_added >= TARGET_TOTAL: break
            
            search_url = f"https://www.snapdeal.com/search?keyword={query.replace(' ', '%20')}&sn={offset}"
            
            try:
                # Add a slightly longer sleep to avoid IP bans during large runs
                time.sleep(random.uniform(1.5, 3.0))
                
                response = requests.get(search_url, headers=HEADERS, timeout=20)
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.text, "html.parser")
                product_cards = soup.select(".product-tuple-listing")
                
                if not product_cards:
                    break # No more results for this keyword

                for card in product_cards:
                    if total_added >= TARGET_TOTAL: break
                    
                    try:
                        title = card.select_one(".product-title").get_text(strip=True)
                        price_val = clean_price(card.select_one(".product-price").get_text(strip=True))
                        
                        # Basic validation to avoid junk data
                        if price_val < 100 or not title:
                            continue

                        mrp_elem = card.select_one(".product-desc-price")
                        mrp_val = clean_price(mrp_elem.get_text(strip=True)) if mrp_elem else int(price_val * 1.2)
                        
                        # Rating logic
                        rating_stars = card.select_one(".filled-stars")
                        rating_val = 4.0
                        if rating_stars and 'style' in rating_stars.attrs:
                            width = "".join(filter(str.isdigit, rating_stars['style']))
                            if width: rating_val = round((float(width)/100) * 5, 1)

                        product_obj = ProductDTO(title, price_val, mrp_val, rating_val, query)
                        add_product(product_obj)
                        
                        total_added += 1
                        if total_added % 10 == 0:
                            print(f"    Status: {total_added}/{TARGET_TOTAL} items stored...")

                    except Exception:
                        continue

            except Exception as e:
                print(f"    Error fetching {query}: {e}")
                continue

    print(f"\n--- MISSION COMPLETE: {total_added} products in database ---")

if __name__ == "__main__":
    run_scraper()