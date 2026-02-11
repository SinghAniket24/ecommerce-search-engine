# E-commerce Search Engine Microservice

## Overview

This project implements a semantic search engine microservice for an electronics e-commerce platform using FastAPI and SentenceTransformer embeddings. It intelligently ranks products based on query meaning, attributes, popularity, and user intent.

The system supports large product catalogs and provides highly relevant results using LLM-based semantic search.

---

## Features

• FastAPI microservice architecture  
• SQLite persistent product catalog  
• 1000+ products scraped and indexed  
• Semantic search using sentence-transformers (LLM embeddings)  
• Handles spelling mistakes and semantic queries  
• Intent detection (cheap, premium, latest)  
• Attribute-based ranking (storage, color, price)  
• Popularity-based ranking (rating, units sold)  
• Explainable ranking with debug score  
• Fast search latency (< 1000 ms)

---

## APIs Implemented

### Store Product  
POST /api/v1/product  

Stores product in catalog.

---

### Update Metadata  
PUT /api/v1/product/meta-data  

Updates product metadata.

---

### Search Products  
GET /api/v1/search/product?query=iphone  

Returns ranked products using semantic similarity.

---

## Ranking Approach

Hybrid semantic ranking using:

• SentenceTransformer embeddings (semantic similarity)  
• Cosine similarity scoring  
• Exact keyword boost  
• Attribute matching (storage, color, price)  
• Popularity scoring (rating, units sold)  
• Intent detection (cheap, premium, latest)

Returns top relevant results based on combined score.

---

## Setup Instructions

Install dependencies:

pip install -r requirements.txt

Run server:

uvicorn main:app --reload

Open API docs:

http://127.0.0.1:8000/docs

---

## Example Queries

/api/v1/search/product?query=iphone  
/api/v1/search/product?query=cheap phone  
/api/v1/search/product?query=iphone 128gb blue  
/api/v1/search/product?query=premium laptop  
/api/v1/search/product?query=latest samsung phone  

---

## Technologies Used

Python  
FastAPI  
SQLite  
SentenceTransformers  
BeautifulSoup  
