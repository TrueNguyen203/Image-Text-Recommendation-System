from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from vectordb.qdrant_client_handler import QdrantHandler

app = FastAPI(title="Multimodal Recommendation API")

# --- Load Models & DB Connection (Load 1 lần khi start app) ---
# Lưu ý: Trong production nên dùng Singleton pattern hoặc lifespan state
text_model = SentenceTransformer('all-MiniLM-L6-v2')
# CLIP Text encoder để tìm ảnh bằng text
clip_model = SentenceTransformer('clip-ViT-B-32') 

text_db = QdrantHandler(collection_name="products_text", vector_size=384)
image_db = QdrantHandler(collection_name="products_image", vector_size=512)

# --- Define Request/Response Models ---
class SearchRequest(BaseModel):
    query: str
    search_type: str = "text" # "text" hoặc "image" (tìm ảnh bằng text query)
    top_k: int = 5
    filter_brand: Optional[str] = None
    filter_category: Optional[str] = None

class ProductResponse(BaseModel):
    product_id: int
    product_name: str
    brand: str
    price: str
    image_url: str
    score: float

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Multimodal RecSys API is running"}

@app.post("/search", response_model=List[ProductResponse])
def search_products(request: SearchRequest):
    """
    API tìm kiếm sản phẩm.
    - query: Câu truy vấn (vd: "running shoes")
    - search_type: 
        - 'text': Tìm dựa trên mô tả sản phẩm (text-to-text).
        - 'image': Tìm ảnh sản phẩm khớp với mô tả (text-to-image dùng CLIP).
    - filter_brand: Lọc theo brand chính xác.
    """
    
    print(f"--> API Input: {request}")

    # 1. Chuẩn bị filter
    filters = {}
    if request.filter_brand:
        filters["brand"] = request.filter_brand
    if request.filter_category:
        filters["main_category"] = request.filter_category

    search_results = []

    # 2. Logic tìm kiếm
    try:
        if request.search_type == "text":
            # Embed query bằng text model
            query_vector = text_model.encode(request.query).tolist()
            # Search trong collection text
            results = text_db.search(
                query_vector=query_vector, 
                limit=request.top_k, 
                filter_criteria=filters
            )
        
        elif request.search_type == "image":
            # Embed query bằng CLIP model (Text encoder của CLIP)
            query_vector = clip_model.encode(request.query).tolist()
            # Search trong collection image
            results = image_db.search(
                query_vector=query_vector, 
                limit=request.top_k, 
                filter_criteria=filters
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid search_type. Use 'text' or 'image'.")

        # 3. Format kết quả trả về
        response_list = []
        for hit in results:
            payload = hit.payload
            response_list.append(ProductResponse(
                product_id=payload['product_id'],
                product_name=payload['product_name'],
                brand=payload['brand'],
                price=str(payload['price']), # Convert to string to be safe
                image_url=payload['image_url'],
                score=hit.score
            ))

        print(f"<-- API Output Count: {len(response_list)}")
        return response_list

    except Exception as e:
        print(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))