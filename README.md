# E-commerce Search Engine Microservice

## Overview

This project implements a production-level search engine microservice for an electronics e-commerce platform. It supports intelligent search, ranking, and retrieval of products using modern ranking techniques like BM25, fuzzy matching, and intent-aware scoring.

The system is designed to handle large product catalogs efficiently and provide relevant results based on customer intent.

---

## Features

* FastAPI microservice architecture
* SQLite persistent product catalog
* 1000+ products scraped and indexed
* BM25 ranking algorithm (industry standard)
* Fuzzy search (handles spelling mistakes like "ifone")
* Query intent detection:

  * Cheap intent ("sasta iphone")
  * Premium intent ("premium phone")
  * Latest intent ("latest iphone")
* Attribute-based ranking:

  * Storage
  * Color
  * Price
  * Rating
  * Popularity (units sold)
* Explainable ranking with score breakdown
* Exception handling for all APIs
* Fast search latency (< 1000 ms)

---

## APIs Implemented

### Store Product

POST /api/v1/product

Stores product in catalog.

---

### Update Metadata

PUT /api/v1/product/meta-data

Updates product metadata such as storage, RAM, etc.

---

### Search Products

GET /api/v1/search/product?query=iphone

Returns ranked product list based on query.

---

## Ranking Algorithm

Hybrid ranking using:

1. BM25 text relevance scoring
2. RapidFuzz typo tolerance
3. Popularity scoring:

   * Units sold
   * Product rating
4. Attribute matching:

   * Storage
   * Color
   * Price
5. Intent detection:

   * Cheap intent
   * Premium intent
   * Latest intent

Final ranking score combines:

* Text relevance (40%)
* Attribute match (30%)
* Popularity (20%)
* Intent boost (10%)

---

## Setup Instructions

Clone repository:

git clone [https://github.com/SinghAniket24/ecommerce-search-engine.git](https://github.com/SinghAniket24/ecommerce-search-engine.git)

cd ecommerce-search-engine

Install dependencies:

pip install -r requirements.txt

Run server:

uvicorn main:app --reload

Open API documentation:

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Example Search Queries

/api/v1/search/product?query=iphone

/api/v1/search/product?query=ifone

/api/v1/search/product?query=sasta iphone

/api/v1/search/product?query=iphone 128gb blue

/api/v1/search/product?query=latest samsung phone

---

## Technologies Used

Python
FastAPI
SQLite
RapidFuzz
BM25 (rank-bm25)
BeautifulSoup

---


