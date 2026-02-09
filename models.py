from pydantic import BaseModel
from typing import Dict


class Product(BaseModel):
    title: str
    description: str
    rating: float
    stock: int
    price: float
    mrp: float
    currency: str


class Metadata(BaseModel):
    productId: int
    metadata: Dict[str, str]
