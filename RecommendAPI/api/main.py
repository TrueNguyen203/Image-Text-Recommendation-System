from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from vectordb.qdrant_client_handler import QdrantHandler
from PIL import Image
from fastapi.middleware.cors import CORSMiddleware
import ast
import pandas as pd
import io
import uvicorn
import traceback

app = FastAPI(title="ASOS Multimodal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

df = pd.read_csv(r"./data/asos_products.csv")
def clean_stringified_list(val):
    try:
        # Nếu nó là chuỗi và nhìn giống list "['a', 'b']" -> chuyển thành list thật
        if isinstance(val, str) and val.startswith("[") and val.endswith("]"):
            return ast.literal_eval(val)
        return val
    except:
        return val

def take_product_by_skus(dataframe, skus):
    df_filtered = df[df["sku"].isin(skus)]
    return df_filtered.to_dict(orient="records")


# Áp dụng cho các cột bị dính lỗi này
for col in ['in_stock_size', 'out_stock_size', 'description', 'images']:
    if col in df.columns:
        df[col] = df[col].apply(clean_stringified_list)



# --- Load Models & DB ---
print("[API] Loading CLIP Model...")
# Dùng chung 1 model cho cả Text và Image
clip_model = SentenceTransformer('clip-ViT-B-32') 

# Cả 2 DB bây giờ đều dùng vector size 512
text_db = QdrantHandler(collection_name="products_text", vector_size=512)
image_db = QdrantHandler(collection_name="products_image", vector_size=512)

# --- Output Model ---
class SearchResponse(BaseModel):
    product_ids: List[int]

class BrandRequest(BaseModel):
    brand: str

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

# POST Recommend products by image/text
@app.post("/search")
async def search_products(
    file: Optional[UploadFile] = File(None),
    query_text: Optional[str] = Form(None),
    brand: Optional[str] = Form(None),
    color: Optional[str] = Form(None)
):
    """
    Tìm kiếm sử dụng CLIP Model.
    - Nếu gửi Ảnh (file) -> Embed ảnh -> Tìm trong products_image.
    - Nếu gửi Text (query_text) -> Embed text -> Tìm trong products_text (hoặc products_image tùy bài toán, ở đây ta tìm trong products_text cho đúng ngữ nghĩa mô tả).
    """
    
    print(f"--> Input: Text='{query_text}', File={file.filename if file else 'None'}, Brand='{brand}', Color='{color}'")

    filters = {}
    if brand: filters["brand"] = brand
    if color: filters["color"] = color

    search_results = []
    top_k = 12

    try:
        # CASE 1: Tìm bằng Ảnh
        if file:
            print("[LOG] Processing Image Search...")
            image_data = await file.read()
            try:
                image = Image.open(io.BytesIO(image_data)).convert("RGB")
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid image file. Please upload a valid image.")
            
            # Embed ảnh query bằng CLIP
            query_vector = clip_model.encode(image).tolist()
            
            # Tìm sản phẩm có ẢNH giống ẢNH query
            search_results = image_db.search(
                query_vector=query_vector, limit=top_k, filter_criteria=filters
            )

        # CASE 2: Tìm bằng Text
        elif query_text:
            print("[LOG] Processing Text Search...")
            # Embed text query bằng CLIP
            query_vector = clip_model.encode(query_text).tolist()
            
            # Có 2 chiến lược ở đây:
            # a) Tìm sản phẩm có MÔ TẢ (Text) khớp với Text Query -> Search vào products_text
            # b) Tìm sản phẩm có ẢNH khớp với Text Query (Text-to-Image) -> Search vào products_image
            # Theo yêu cầu là tách biệt, ta sẽ search vào products_text
            search_results = text_db.search(
                query_vector=query_vector, limit=top_k, filter_criteria=filters
            )
        
        else:
            raise HTTPException(status_code=400, detail="Please provide 'file' or 'query_text'.")

        # Trích xuất ID an toàn hơn, bỏ qua nếu không có payload hoặc thiếu product_id
        result_ids = []
        for hit in search_results:
            if hit.payload and 'product_id' in hit.payload:
                result_ids.append(hit.payload['product_id'])
        
        print(f"<-- Found: {len(result_ids)} items.")
        return take_product_by_skus(df, list(result_ids))

    except Exception as e:
        # In ra traceback đầy đủ để debug
        print(take_product_by_skus(df, result_ids))
        traceback.print_exc()
        print(f"[ERR] API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/preference")
async def get_preference(sku: int):
    top_k = 12

    # Suggest 1: thông qua Ảnh
    print("[LOG] Processing Image Search...")
    try:
        # Mở trực tiếp file từ đường dẫn (không dùng BytesIO cho file local)
        # Đường dẫn dựa trên thư mục chạy (root) giống như cách đọc file CSV
        image = Image.open(f"./data/images/{sku}.jpg").convert("RGB")
    except Exception:
        traceback.print_exc() # In lỗi chi tiết ra terminal (ví dụ: FileNotFoundError)
        raise HTTPException(status_code=400, detail="Invalid image file. Please upload a valid image.")
    
    # Embed ảnh query bằng CLIP
    query_vector = clip_model.encode(image).tolist()
    
    # Tìm sản phẩm có ẢNH giống ẢNH query
    image_search_results = image_db.search(
        query_vector=query_vector, limit=top_k
    )
    image_result_ids = []
    for hit in image_search_results:
            if hit.payload and 'product_id' in hit.payload:
                image_result_ids.append(hit.payload['product_id'])

    
    print("[LOG] Processing Text Search...")
    query_text = f"{df[df['sku'] == sku]['name']}. {df[df['sku'] == sku]['description']}"
    # Embed text query bằng CLIP
    query_vector = clip_model.encode(query_text).tolist()
        
    # Có 2 chiến lược ở đây:
    # a) Tìm sản phẩm có MÔ TẢ (Text) khớp với Text Query -> Search vào products_text
    # b) Tìm sản phẩm có ẢNH khớp với Text Query (Text-to-Image) -> Search vào products_image
    # Theo yêu cầu là tách biệt, ta sẽ search vào products_text
    text_search_results = text_db.search(
        query_vector=query_vector, limit=top_k
    )
    text_result_ids = []
    for hit in text_search_results:
            if hit.payload and 'product_id' in hit.payload:
                text_result_ids.append(hit.payload['product_id'])

    return {'image' : take_product_by_skus(df, image_result_ids), 'text' : take_product_by_skus(df, text_result_ids)}


    
if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
