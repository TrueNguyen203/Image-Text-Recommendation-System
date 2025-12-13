import requests

API_MAIN = "http://127.0.0.1:8000"

# =====================
# 1️⃣ Get product by sku
# =====================
res = requests.get(API_MAIN, params={"sku": 123650194})
print("GET /:", res.json())


# =====================
# 2️⃣ Get products by brand
# =====================
res = requests.post(
    f"{API_MAIN}/products-by-brand",
    json={"brand": "Topshop"}
)
print("POST /products-by-brand:", res.json())


# =====================
# 3️⃣ Search products
# =====================
res = requests.post(
    f"{API_MAIN}/search-products",
    json={
        "query": "black dress",
        "brand": "Asos",
        "color": "BLACK"
    }
)

print("POST /search-products:", res.json())
