import sqlite3
import json

DB_NAME = "products.db"


# Create table if not exists
def init_db():
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            productId INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            rating REAL,
            stock INTEGER,
            price REAL,
            mrp REAL,
            currency TEXT,
            metadata TEXT
        )
    """)
    
    conn.commit()
    conn.close()


# Add product
def add_product(product):
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO products
        (title, description, rating, stock, price, mrp, currency, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        product.title,
        product.description,
        product.rating,
        product.stock,
        product.price,
        product.mrp,
        product.currency,
        json.dumps({})
    ))
    
    product_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return product_id


# Update metadata
def update_product_metadata(product_id, metadata):
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT metadata FROM products WHERE productId = ?", (product_id,))
    
    row = cursor.fetchone()
    
    if not row:
        return None
    
    current_metadata = json.loads(row[0])
    current_metadata.update(metadata)
    
    cursor.execute("""
        UPDATE products
        SET metadata = ?
        WHERE productId = ?
    """, (
        json.dumps(current_metadata),
        product_id
    ))
    
    conn.commit()
    conn.close()
    
    return {
        "productId": product_id,
        "metadata": current_metadata
    }


# Get all products
def get_all_products():
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM products")
    
    rows = cursor.fetchall()
    
    conn.close()
    
    products = {}
    
    for row in rows:
        
        products[row[0]] = {
            "productId": row[0],
            "title": row[1],
            "description": row[2],
            "rating": row[3],
            "stock": row[4],
            "price": row[5],
            "mrp": row[6],
            "currency": row[7],
            "metadata": json.loads(row[8])
        }
    
    return products


# Get products list
def get_products_list():
    
    return list(get_all_products().values())
