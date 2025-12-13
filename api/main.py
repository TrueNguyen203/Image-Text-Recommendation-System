from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from vectordb.qdrant_client_handler import QdrantHandler
from PIL import Image
from pydantic import BaseModel
import io

app = FastAPI(title="ASOS Multimodal Recommendation API")

# --- Load Models & DB ---
print("[API] Loading models...")
text_model = SentenceTransformer('all-MiniLM-L6-v2')
# CLIP model dùng cho cả encode ảnh (khi upload) và encode text (nếu muốn text-to-image search)
# Ở đây ta dùng clip-ViT-B-32 cho nhất quán với lúc ingest
clip_model = SentenceTransformer('clip-ViT-B-32') 

text_db = QdrantHandler(collection_name="products_text", vector_size=384)
image_db = QdrantHandler(collection_name="products_image", vector_size=512)

# --- Define Output Model ---
# Theo yêu cầu: Chỉ trả về list product_id
class SearchResponse(BaseModel):
    product_ids: List[int]

@app.get("/")
def health_check():
    return {"status": "ok", "message": "ASOS Recommender System Ready"}

@app.post("/search")
async def search_products(
    file: Optional[UploadFile] = File(None),  # Nhận file ảnh
    query_text: Optional[str] = Form(None),   # Nhận text query
    brand: Optional[str] = Form(None),        # Filter Brand
    color: Optional[str] = Form(None)         # Filter Color
):
    """
    Multimodal Search Endpoint.
    - Ưu tiên: Nếu có 'file' (ảnh) -> Search bằng Image Vector.
    - Nếu không có file, dùng 'query_text' -> Search bằng Text Vector.
    - Hỗ trợ lọc theo 'brand' và 'color'.
    - Trả về: Top 12 Product IDs.
    """
    
    print(f"--> Input: File={file.filename if file else 'None'}, Text='{query_text}', Brand='{brand}', Color='{color}'")

    # 1. Chuẩn bị filter criteria
    filters = {}
    if brand:
        filters["brand"] = brand
    if color:
        filters["color"] = color

    search_results = []
    top_k = 12  # Yêu cầu trả về 12 sản phẩm

    try:
        # CASE A: Tìm kiếm bằng Hình ảnh (Image-to-Image Similarity)
        if file:
            print("[LOG] Processing Image Search...")
            # Đọc file ảnh từ request
            image_data = await file.read()
            image = Image.open(io.BytesIO(image_data)).convert("RGB")
            
            # Embed ảnh query
            query_vector = clip_model.encode(image).tolist()
            
            # Search trong collection ẢNH
            search_results = image_db.search(
                query_vector=query_vector,
                limit=top_k,
                filter_criteria=filters
            )

        # CASE B: Tìm kiếm bằng Text (Text-to-Text Similarity)
        elif query_text:
            print("[LOG] Processing Text Search...")
            # Embed text query
            query_vector = text_model.encode(query_text).tolist()
            
            # Search trong collection TEXT
            search_results = text_db.search(
                query_vector=query_vector,
                limit=top_k,
                filter_criteria=filters
            )
        
        else:
            raise HTTPException(status_code=400, detail="Vui lòng cung cấp ảnh (file) hoặc text (query_text) để tìm kiếm.")

        # 3. Trích xuất Product IDs
        result_ids = [hit.payload['product_id'] for hit in search_results]
        
        print(f"<-- Found {len(result_ids)} items: {result_ids}")
        return {"product_ids": result_ids}

    except Exception as e:
        print(f"[ERR] API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Bản 1
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from typing import List, Optional
# from sentence_transformers import SentenceTransformer
# from vectordb.qdrant_client_handler import QdrantHandler

# app = FastAPI(title="Multimodal Recommendation API")

# # --- Load Models & DB Connection (Load 1 lần khi start app) ---
# # Lưu ý: Trong production nên dùng Singleton pattern hoặc lifespan state
# text_model = SentenceTransformer('all-MiniLM-L6-v2')
# # CLIP Text encoder để tìm ảnh bằng text
# clip_model = SentenceTransformer('clip-ViT-B-32') 

# text_db = QdrantHandler(collection_name="products_text", vector_size=384)
# image_db = QdrantHandler(collection_name="products_image", vector_size=512)

# # --- Define Request/Response Models ---
# class SearchRequest(BaseModel):
#     query: str
#     search_type: str = "text" # "text" hoặc "image" (tìm ảnh bằng text query)
#     top_k: int = 5
#     filter_brand: Optional[str] = None
#     filter_category: Optional[str] = None

# class ProductResponse(BaseModel):
#     product_id: int
#     product_name: str
#     brand: str
#     price: str
#     image_url: str
#     score: float

# @app.get("/")
# def health_check():
#     return {"status": "ok", "message": "Multimodal RecSys API is running"}

# @app.post("/search", response_model=List[ProductResponse])
# def search_products(request: SearchRequest):
#     """
#     API tìm kiếm sản phẩm.
#     - query: Câu truy vấn (vd: "running shoes")
#     - search_type: 
#         - 'text': Tìm dựa trên mô tả sản phẩm (text-to-text).
#         - 'image': Tìm ảnh sản phẩm khớp với mô tả (text-to-image dùng CLIP).
#     - filter_brand: Lọc theo brand chính xác.
#     """
    
#     print(f"--> API Input: {request}")

#     # 1. Chuẩn bị filter
#     filters = {}
#     if request.filter_brand:
#         filters["brand"] = request.filter_brand
#     if request.filter_category:
#         filters["main_category"] = request.filter_category

#     search_results = []

#     # 2. Logic tìm kiếm
#     try:
#         if request.search_type == "text":
#             # Embed query bằng text model
#             query_vector = text_model.encode(request.query).tolist()
#             # Search trong collection text
#             results = text_db.search(
#                 query_vector=query_vector, 
#                 limit=request.top_k, 
#                 filter_criteria=filters
#             )
        
#         elif request.search_type == "image":
#             # Embed query bằng CLIP model (Text encoder của CLIP)
#             query_vector = clip_model.encode(request.query).tolist()
#             # Search trong collection image
#             results = image_db.search(
#                 query_vector=query_vector, 
#                 limit=request.top_k, 
#                 filter_criteria=filters
#             )
#         else:
#             raise HTTPException(status_code=400, detail="Invalid search_type. Use 'text' or 'image'.")

#         # 3. Format kết quả trả về
#         response_list = []
#         for hit in results:
#             payload = hit.payload
#             response_list.append(ProductResponse(
#                 product_id=payload['product_id'],
#                 product_name=payload['product_name'],
#                 brand=payload['brand'],
#                 price=str(payload['price']), # Convert to string to be safe
#                 image_url=payload['image_url'],
#                 score=hit.score
#             ))

#         print(f"<-- API Output Count: {len(response_list)}")
#         return response_list

#     except Exception as e:
#         print(f"Error processing request: {e}")
#         raise HTTPException(status_code=500, detail=str(e))