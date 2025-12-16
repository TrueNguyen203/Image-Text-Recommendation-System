import pandas as pd
import os
from PIL import Image
from sentence_transformers import SentenceTransformer
from vectordb.qdrant_client_handler import QdrantHandler
from qdrant_client.http import models
import ast

class DataIngestion:
    def __init__(self, csv_path: str, images_folder: str):
        print(f"[INFO] Reading CSV from {csv_path}...")
        self.df = pd.read_csv(csv_path)
        self.df['sku'] = self.df['sku'].astype(str)
        self.images_folder = images_folder
        
        # --- CHỈ DÙNG 1 MODEL CLIP ---
        # CLIP embed ra vector 512 chiều cho cả Text và Ảnh
        print("[INFO] Loading CLIP Model (clip-ViT-B-32)...")
        self.model = SentenceTransformer('clip-ViT-B-32')
        
        # Init DB (Cả 2 đều size 512)
        self.text_db = QdrantHandler(collection_name="products_text", vector_size=512)
        self.image_db = QdrantHandler(collection_name="products_image", vector_size=512)

    def extract_clean_description(self, desc_col_data):
        """Parse chuỗi json/list trong description thành text thuần"""
        try:
            if pd.isna(desc_col_data): return ""
            data_list = ast.literal_eval(str(desc_col_data))
            text_parts = []
            if isinstance(data_list, list):
                for item in data_list:
                    if isinstance(item, dict):
                        text_parts.extend(item.values())
            return ". ".join([str(t) for t in text_parts])
        except:
            return str(desc_col_data)

    def process_and_ingest(self, batch_size=50):
        total_rows = len(self.df)
        print(f"[INFO] Start processing {total_rows} products (Local Images)...")

        text_batch = []
        image_batch = []
        success_img_count = 0

        for index, row in self.df.iterrows():
            try:
                # 1. Lấy thông tin cơ bản
                sku = str(row['sku']).replace(".0", "") # Xử lý nếu pandas đọc thành 12345.0
                try:
                    p_id = int(sku)
                except:
                    continue # Bỏ qua nếu SKU không phải số

                brand = str(row['brand']) if not pd.isna(row['brand']) else ""
                color = str(row['color']) if not pd.isna(row['color']) else ""
                
                payload = {
                    "product_id": p_id,
                    "brand": brand,
                    "color": color
                }

                # --- 2. Xử lý TEXT (Dùng CLIP Text Encoder) ---
                name = str(row['name']) if not pd.isna(row['name']) else ""
                clean_desc = self.extract_clean_description(row['description'])
                full_text = f"{name}. {clean_desc}"[:77] # CLIP giới hạn token text, cắt ngắn để tối ưu (hoặc để thư viện tự cắt)
                
                # Encode Text bằng CLIP
                text_vector = self.model.encode(full_text).tolist()
                text_batch.append(models.PointStruct(id=p_id, vector=text_vector, payload=payload))

                # --- 3. Xử lý ẢNH (Đọc từ Local Folder) ---
                # Giả định tên file ảnh là {sku}.jpg. Nếu file ảnh của bạn tên khác, hãy sửa dòng này.
                image_path = os.path.join(self.images_folder, f"{sku}.jpg")
                
                if os.path.exists(image_path):
                    try:
                        img_obj = Image.open(image_path).convert("RGB")
                        # Encode Ảnh bằng CLIP
                        image_vector = self.model.encode(img_obj).tolist()
                        
                        image_batch.append(models.PointStruct(id=p_id, vector=image_vector, payload=payload))
                        success_img_count += 1
                    except Exception as img_err:
                        print(f"[WARN] Corrupt image {image_path}: {img_err}")
                else:
                    # Uncomment dòng dưới nếu muốn debug xem ảnh nào thiếu
                    # print(f"[MISSING] Image not found: {image_path}")
                    pass

                # --- 4. Upload Batch ---
                if len(text_batch) >= batch_size:
                    self.text_db.upsert_points(text_batch)
                    text_batch = []

                if len(image_batch) >= batch_size:
                    self.image_db.upsert_points(image_batch)
                    image_batch = []
                    print(f"--> [Batch {index}] Image Count: {success_img_count}")

            except Exception as e:
                print(f"[ERR] Row {index}: {e}")
                continue

        # Upload phần dư
        if text_batch: self.text_db.upsert_points(text_batch)
        if image_batch: self.image_db.upsert_points(image_batch)

        print(f"[SUCCESS] Ingest Done! Processed Images: {success_img_count}/{total_rows}")

# Bản 2:
# import pandas as pd
# import requests
# from PIL import Image
# from io import BytesIO
# from sentence_transformers import SentenceTransformer
# from vectordb.qdrant_client_handler import QdrantHandler
# from qdrant_client.http import models
# import ast
# import socket # Để set timeout mức socket

# class DataIngestion:
#     def __init__(self, csv_path: str):
#         print(f"[INFO] Reading CSV from {csv_path}...")
#         self.df = pd.read_csv(csv_path, on_bad_lines='skip')
#         self.df['sku'] = self.df['sku'].astype(str)
        
#         # Set global socket timeout để tránh treo mạng vô tận
#         socket.setdefaulttimeout(5) 
        
#         print("[INFO] Loading Text Model...")
#         self.text_model = SentenceTransformer('all-MiniLM-L6-v2') 
        
#         print("[INFO] Loading Image Model...")
#         self.image_model = SentenceTransformer('clip-ViT-B-32')   
        
#         self.text_db = QdrantHandler(collection_name="products_text", vector_size=384)
#         self.image_db = QdrantHandler(collection_name="products_image", vector_size=512)

#     def extract_image_url(self, image_col_data):
#         try:
#             if pd.isna(image_col_data): return None
#             # Thử parse list
#             urls = ast.literal_eval(str(image_col_data))
#             if isinstance(urls, list) and len(urls) > 0:
#                 return urls[0]
#         except:
#             # Fallback nếu eval lỗi, lấy chuỗi thô (nếu nó là link đơn)
#             s = str(image_col_data)
#             if s.startswith('http'): return s
#         return None

#     def extract_clean_description(self, desc_col_data):
#         try:
#             if pd.isna(desc_col_data): return ""
#             data_list = ast.literal_eval(str(desc_col_data))
#             text_parts = []
#             if isinstance(data_list, list):
#                 for item in data_list:
#                     if isinstance(item, dict):
#                         text_parts.extend(item.values())
#             return ". ".join([str(t) for t in text_parts])
#         except:
#             return str(desc_col_data)

#     def download_image(self, url: str):
#         try:
#             # Fake User-Agent giống trình duyệt thật
#             headers = {
#                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
#             }
#             # Timeout cực ngắn: 2 giây connect, 2 giây đọc
#             response = requests.get(url, headers=headers, timeout=(2, 2))
#             if response.status_code == 200:
#                 return Image.open(BytesIO(response.content)).convert("RGB")
#         except Exception:
#             # print(f"   [Warn] Download failed: {url}") # Bỏ comment nếu muốn xem lỗi chi tiết
#             return None
#         return None

#     def process_and_ingest(self, batch_size=10): # Giảm mặc định xuống 10
#         total_rows = len(self.df)
#         print(f"[INFO] Start processing {total_rows} products...")

#         text_batch = []
#         image_batch = []
#         success_img_count = 0

#         for index, row in self.df.iterrows():
#             # [DEBUG] In ra mỗi dòng để biết code đang chạy tới đâu
#             # print(f"Processing row {index}/{total_rows}...", end='\r') 

#             try:
#                 try:
#                     p_id = int(float(str(row['sku'])))
#                 except:
#                     continue

#                 brand = str(row['brand']) if not pd.isna(row['brand']) else ""
#                 color = str(row['color']) if not pd.isna(row['color']) else ""
                
#                 payload = {"product_id": p_id, "brand": brand, "color": color}

#                 # 1. Text
#                 name = str(row['name']) if not pd.isna(row['name']) else ""
#                 clean_desc = self.extract_clean_description(row['description'])
#                 full_text = f"{name}. {clean_desc}"
                
#                 text_vector = self.text_model.encode(full_text).tolist()
#                 text_batch.append(models.PointStruct(id=p_id, vector=text_vector, payload=payload))

#                 # 2. Image
#                 img_url = self.extract_image_url(row['images'])
#                 if img_url:
#                     # In ra URL đang thử tải để xem có bị treo không
#                     # print(f"   Downloading: {img_url[:50]}...") 
#                     img_obj = self.download_image(img_url)
#                     if img_obj:
#                         image_vector = self.image_model.encode(img_obj).tolist()
#                         image_batch.append(models.PointStruct(id=p_id, vector=image_vector, payload=payload))
#                         success_img_count += 1

#                 # 3. Upload Batch
#                 if len(text_batch) >= batch_size:
#                     self.text_db.upsert_points(text_batch)
#                     text_batch = []

#                 if len(image_batch) >= batch_size:
#                     self.image_db.upsert_points(image_batch)
#                     image_batch = []
#                     # In ra ngay khi upload xong 1 batch
#                     print(f"--> [SAVED] Index {index}: Uploaded batch (Total imgs: {success_img_count})")

#             except Exception as e:
#                 print(f"[ERR] Row {index}: {e}")
#                 continue

#         # Upload phần còn lại
#         if text_batch: self.text_db.upsert_points(text_batch)
#         if image_batch: self.image_db.upsert_points(image_batch)

#         print(f"\n[SUCCESS] Finished! Total Images Ingested: {success_img_count}/{total_rows}")

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