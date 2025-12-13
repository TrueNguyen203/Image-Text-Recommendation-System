import pandas as pd
import requests
from PIL import Image
from io import BytesIO
from sentence_transformers import SentenceTransformer
from vectordb.qdrant_client_handler import QdrantHandler
from qdrant_client.http import models
import ast
import re

class DataIngestion:
    def __init__(self, csv_path: str):
        # Đọc CSV, chuyển sku thành string để tránh lỗi
        print(f"[INFO] Reading CSV from {csv_path}...")
        self.df = pd.read_csv(csv_path)
        self.df['sku'] = self.df['sku'].astype(str)
        
        # Load Models
        print("[INFO] Loading Text Embedding Model (all-MiniLM-L6-v2)...")
        self.text_model = SentenceTransformer('all-MiniLM-L6-v2') # Dim: 384
        
        print("[INFO] Loading Image Embedding Model (clip-ViT-B-32)...")
        self.image_model = SentenceTransformer('clip-ViT-B-32')   # Dim: 512
        
        # Init DB
        self.text_db = QdrantHandler(collection_name="products_text", vector_size=384)
        self.image_db = QdrantHandler(collection_name="products_image", vector_size=512)

    def parse_image_url(self, image_col_data):
        """
        Xử lý cột 'images' phức tạp: "[['Product', ['url1', 'url2']...]]"
        """
        try:
            # Cách 1: Thử parse cấu trúc list
            if isinstance(image_col_data, str):
                data = ast.literal_eval(image_col_data)
                # Cấu trúc mong đợi: [['Product', ['https://...', ...]], ...]
                # Lấy phần tử đầu tiên -> lấy list url -> lấy url đầu tiên
                return data[0][1][0]
        except:
            # Cách 2: Fallback dùng Regex nếu cấu trúc lỗi
            # Tìm chuỗi bắt đầu bằng http và kết thúc bằng jpg/png...
            try:
                match = re.search(r'(https?://[^\s]+\.(?:jpg|jpeg|png|webp))', str(image_col_data))
                if match:
                    return match.group(0)
            except:
                pass
        return None

    def download_image(self, url: str):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'} # Fake user agent để tránh bị block
            response = requests.get(url, headers=headers, timeout=3)
            if response.status_code == 200:
                return Image.open(BytesIO(response.content)).convert("RGB")
        except:
            pass
        return None

    def process_and_ingest(self, batch_size=50):
        total_rows = len(self.df)
        print(f"[INFO] Start processing {total_rows} products with Batch Size: {batch_size}...")

        text_batch = []
        image_batch = []

        for index, row in self.df.iterrows():
            try:
                # 1. Lấy dữ liệu cơ bản
                p_id = int(row['sku']) # Dùng sku làm ID (Qdrant yêu cầu int hoặc uuid)
                brand = str(row['brand']) if not pd.isna(row['brand']) else ""
                color = str(row['color']) if not pd.isna(row['color']) else ""
                
                # Payload metadata dùng để lọc sau này
                payload = {
                    "product_id": p_id,
                    "brand": brand,
                    "color": color
                }

                # 2. Xử lý Text (Chỉ dùng name và description theo yêu cầu)
                # Xử lý description nếu bị null
                desc = str(row['description']) if not pd.isna(row['description']) else ""
                name = str(row['name']) if not pd.isna(row['name']) else ""
                
                full_text = f"{name}. {desc}"
                text_vector = self.text_model.encode(full_text).tolist()
                
                text_batch.append(models.PointStruct(
                    id=p_id,
                    vector=text_vector,
                    payload=payload
                ))

                # 3. Xử lý Image
                raw_img_str = row['images']
                img_url = self.parse_image_url(raw_img_str)
                
                if img_url:
                    img_obj = self.download_image(img_url)
                    if img_obj:
                        image_vector = self.image_model.encode(img_obj).tolist()
                        image_batch.append(models.PointStruct(
                            id=p_id,
                            vector=image_vector,
                            payload=payload
                        ))
                
                # 4. Upload theo Batch (để tránh tràn RAM và nhanh hơn)
                if len(text_batch) >= batch_size:
                    self.text_db.upsert_points(text_batch)
                    text_batch = [] # Reset batch
                    print(f"--> Uploaded batch Text at index {index}")

                if len(image_batch) >= batch_size:
                    self.image_db.upsert_points(image_batch)
                    image_batch = [] # Reset batch
                    print(f"--> Uploaded batch Image at index {index}")

            except Exception as e:
                print(f"[ERR] Error at row {index}: {e}")
                continue

        # Upload nốt những phần tử còn sót lại
        if text_batch:
            self.text_db.upsert_points(text_batch)
        if image_batch:
            self.image_db.upsert_points(image_batch)

        print("[SUCCESS] Ingestion Process Completed!")

if __name__ == "__main__":
    # Sửa đường dẫn tới file CSV mới của bạn
    ingestor = DataIngestion(csv_path="data/asos_products.csv")
    ingestor.process_and_ingest(batch_size=50)

# Bản 1:
# import pandas as pd
# import requests
# from PIL import Image
# from io import BytesIO
# from sentence_transformers import SentenceTransformer
# from vectordb.qdrant_client_handler import QdrantHandler
# from qdrant_client.http import models
# import ast

# class DataIngestion:
#     def __init__(self, csv_path: str):
#         self.df = pd.read_csv(csv_path)
        
#         # Load Models
#         print("[INFO] Loading Text Embedding Model...")
#         self.text_model = SentenceTransformer('all-MiniLM-L6-v2') # Output dim: 384
        
#         print("[INFO] Loading Image Embedding Model...")
#         self.image_model = SentenceTransformer('clip-ViT-B-32')   # Output dim: 512
        
#         # Init Vector DB Clients (2 collections riêng biệt)
#         self.text_db = QdrantHandler(collection_name="products_text", vector_size=384)
#         self.image_db = QdrantHandler(collection_name="products_image", vector_size=512)

#     def download_image(self, url: str):
#         """Tải ảnh từ URL và convert sang PIL Image"""
#         try:
#             response = requests.get(url, timeout=5)
#             response.raise_for_status()
#             return Image.open(BytesIO(response.content)).convert("RGB")
#         except Exception as e:
#             print(f"[WARN] Cannot download image {url}: {e}")
#             return None

#     def process_and_ingest(self):
#         text_points = []
#         image_points = []

#         print(f"[INFO] Start processing {len(self.df)} products...")

#         for index, row in self.df.iterrows():
#             p_id = int(row['Product_id'])
            
#             # --- 1. Xử lý Metadata ---
#             # Parse Categories string "['a', 'b']" thành list thực tế nếu cần, hoặc giữ string
#             try:
#                 categories = ast.literal_eval(row['Categories']) if isinstance(row['Categories'], str) else []
#                 # Lấy category chính (phần tử đầu tiên) để lọc cho dễ
#                 main_category = categories[0] if len(categories) > 0 else "Unknown"
#             except:
#                 main_category = "Unknown"

#             payload = {
#                 "product_id": p_id,
#                 "product_name": row['Product_Name'],
#                 "brand": str(row['Brand']),
#                 "price": row['Final_Price'],
#                 "image_url": row['Image_URL'],
#                 "main_category": main_category
#             }

#             # --- 2. Text Embedding ---
#             # Kết hợp các trường text để model hiểu ngữ cảnh tốt hơn
#             full_text = f"{row['Product_Name']}. Brand: {row['Brand']}. {row['Description']}"
#             text_vector = self.text_model.encode(full_text).tolist()
            
#             text_points.append(models.PointStruct(
#                 id=p_id,
#                 vector=text_vector,
#                 payload=payload
#             ))

#             # --- 3. Image Embedding ---
#             img_obj = self.download_image(row['Image_URL'])
#             if img_obj:
#                 image_vector = self.image_model.encode(img_obj).tolist()
#                 image_points.append(models.PointStruct(
#                     id=p_id,
#                     vector=image_vector,
#                     payload=payload
#                 ))
#             else:
#                 print(f"[SKIP] Product {p_id} has no valid image.")

#             # Print Input/Output progress (Mỗi 5 items in 1 lần cho đỡ rối)
#             if index % 5 == 0:
#                 print(f"--> Processed ID: {p_id} | Brand: {payload['brand']} | Text Vec Len: {len(text_vector)}")

#         # --- 4. Upload to DB ---
#         if text_points:
#             print(f"[INFO] Uploading {len(text_points)} text vectors to Qdrant...")
#             self.text_db.upsert_points(text_points)
        
#         if image_points:
#             print(f"[INFO] Uploading {len(image_points)} image vectors to Qdrant...")
#             self.image_db.upsert_points(image_points)
            
#         print("[SUCCESS] Ingestion Finished!")

# # File chạy riêng lẻ để test
# if __name__ == "__main__":
#     ingestor = DataIngestion(csv_path="data/products.csv")
#     ingestor.process_and_ingest()