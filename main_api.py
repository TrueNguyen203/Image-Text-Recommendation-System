import pandas as pd
import requests
import ast
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI()

df = pd.read_csv(r"c:\Users\PC\Downloads\products_small.csv")

def clean_stringified_list(val):
    try:
        # Nếu nó là chuỗi và nhìn giống list "['a', 'b']" -> chuyển thành list thật
        if isinstance(val, str) and val.startswith("[") and val.endswith("]"):
            return ast.literal_eval(val)
        return val
    except:
        return val

# Áp dụng cho các cột bị dính lỗi này
for col in ['in_stock_size', 'out_stock_size', 'description', 'images']:
    if col in df.columns:
        df[col] = df[col].apply(clean_stringified_list)

class BrandRequest(BaseModel):
    brand: str


class SearchRequest(BaseModel):
    query: Optional[str] = None
    brand: Optional[str] = None
    color: Optional[str] = None


API_A_URL = "http://127.0.0.1:8001/search"



# GET product by sku
@app.get("/")
def get_product_by_sku(sku: int):
    product = df[df["sku"] == sku]

    if product.empty:
        return {"error": "Product not found"}

    return product.to_dict(orient="records")[0]



# POST products by brand
@app.post("/products-by-brand")
def get_products_by_brand(req: BrandRequest):
    products = df[df["brand"].str.lower() == req.brand.lower()]
    return products.head(4).to_dict(orient="records")


# POST search-products
@app.post("/search-products")
def search_products(req: SearchRequest):

    payload = req.dict()

    # Gửi sang API A
    response = requests.post(API_A_URL, json=payload)
    sku_list: List[int] = response.json()

    # Lọc data
    result = df[df["sku"].isin(sku_list)]

    return result.to_dict(orient="records")
