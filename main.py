from fastapi import FastAPI, HTTPException

from models import Product, Metadata
from database import (
    init_db,
    add_product,
    update_product_metadata,
    get_all_products
)
from search import search_products_logic


app = FastAPI()

# Initialize database
init_db()


@app.get("/")
def home():
    try:
        return {"message": "Search Engine Running"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Store product API
@app.post("/api/v1/product")
def store_product(product: Product):
    
    try:
        product_id = add_product(product)
        
        return {"productId": product_id}
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to store product: {str(e)}"
        )


# Update metadata API
@app.put("/api/v1/product/meta-data")
def update_metadata(data: Metadata):
    
    try:
        updated_product = update_product_metadata(
            data.productId,
            data.metadata
        )
        
        if updated_product is None:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )
        
        return {
            "productId": data.productId,
            "metadata": updated_product["metadata"]
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update metadata: {str(e)}"
        )


# View all products
@app.get("/products")
def view_products():
    
    try:
        return get_all_products()
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch products: {str(e)}"
        )


# Search API
@app.get("/api/v1/search/product")
def search_products(query: str):
    
    try:
        if not query or query.strip() == "":
            raise HTTPException(
                status_code=400,
                detail="Query cannot be empty"
            )
        
        results = search_products_logic(query)
        
        return {"data": results}
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )
