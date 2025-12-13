import pandas as pd
import re
from pydantic import BaseModel
from fastapi import FastAPI


app = FastAPI()
df = pd.read_csv(r'c:\Users\PC\Downloads\products_small.csv')

@app.get("/products")
def get_products(start: int, end: int):
    return df.iloc[start:end].to_dict(orient="records")

class ProductRequest(BaseModel):
    sku: int

@app.post("/product-by-id")
def get_product_by_id(req: ProductRequest):
    product = df[df["sku"] == req.sku]
    if product.empty:
        return {"error": "Product not found"}
    return product.to_dict(orient="records")[0]

