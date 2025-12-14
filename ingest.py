import pandas as pd
import requests
from PIL import Image
from io import BytesIO
from sentence_transformers import SentenceTransformer
from vectordb.qdrant_client_handler import QdrantHandler
from qdrant_client.http import models
import ast # Thư viện quan trọng để parse cấu trúc List/Dict trong string

class DataIngestion:
    def __init__(self, csv_path: str):
        print(f"[INFO] Reading CSV from {csv_path}...")
        # Đọc CSV
        self.df = pd.read_csv(csv_path)
        # Chuyển sku thành string để làm ID: có thể sau này output sẽ trả về 2 ID
        self.df['sku'] = self.df['sku'].astype(str)
        
        # Load Models
        print("[INFO] Loading Text Model (all-MiniLM-L6-v2)...")
        self.text_model = SentenceTransformer('all-MiniLM-L6-v2') 
        
        print("[INFO] Loading Image Model (clip-ViT-B-32)...")
        self.image_model = SentenceTransformer('clip-ViT-B-32')   
        
        # Init DB
        self.text_db = QdrantHandler(collection_name="products_text", vector_size=384)
        self.image_db = QdrantHandler(collection_name="products_image", vector_size=512)

    def extract_image_url(self, image_col_data):
        """
        Input: "['url1', 'url2', ...]" (String)
        Output: 'url1' (String) hoặc None
        """
        try:
            if pd.isna(image_col_data):
                return None
            
            # Chuyển chuỗi string thành List Python thực sự
            # Ví dụ: "['http://a.com', 'http://b.com']" -> ['http://a.com', 'http://b.com']
            urls = ast.literal_eval(str(image_col_data))
            
            if isinstance(urls, list) and len(urls) > 0:
                return urls[0] # Lấy ảnh đầu tiên
        except Exception:
            return None
        return None

    def extract_clean_description(self, desc_col_data):
        """
        Input: "[{'Product Details': '...'}, {'Brand': '...'}]"
        Output: "Coats & Jackets by Nike... Key players in..." (String gộp)
        """
        try:
            if pd.isna(desc_col_data):
                return ""
            
            # Chuyển chuỗi thành List các Dict
            data_list = ast.literal_eval(str(desc_col_data))
            
            text_parts = []
            if isinstance(data_list, list):
                for item in data_list:
                    if isinstance(item, dict):
                        # Lấy tất cả các value trong dict (bỏ qua key)
                        # Ví dụ: {'Brand': 'Nike...'} -> lấy 'Nike...'
                        text_parts.extend(item.values())
            
            return ". ".join([str(t) for t in text_parts])
        except Exception:
            # Nếu lỗi parse (do data bẩn), trả về chuỗi gốc hoặc rỗng
            return str(desc_col_data)

    def download_image(self, url: str):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            # Timeout ngắn để tránh treo lâu
            response = requests.get(url, headers=headers, timeout=3)
            if response.status_code == 200:
                return Image.open(BytesIO(response.content)).convert("RGB")
        except Exception:
            return None
        return None

    def process_and_ingest(self, batch_size=50):
        total_rows = len(self.df)
        print(f"[INFO] Start processing {total_rows} products...")

        text_batch = []
        image_batch = []
        success_img_count = 0

        for index, row in self.df.iterrows():
            try:
                # --- 1. Lấy dữ liệu cơ bản ---
                # Xử lý sku: ép về int để chắc chắn (nếu file excel bị lỗi 123.0)
                try:
                    p_id = int(float(str(row['sku'])))
                except:
                    continue # Bỏ qua dòng ko có sku hợp lệ

                brand = str(row['brand']) if not pd.isna(row['brand']) else ""
                # Cột trong file Excel tên là 'color', nên ở đây code phải là row['color']
                color = str(row['color']) if not pd.isna(row['color']) else ""
                
                payload = {
                    "product_id": p_id,
                    "brand": brand, # Metadata để lọc
                    "color": color  # Metadata để lọc
                }

                # --- 2. Xử lý Text (Name + Description cleaned) ---
                name = str(row['name']) if not pd.isna(row['name']) else ""
                clean_desc = self.extract_clean_description(row['description'])
                
                full_text = f"{name}. {clean_desc}"
                
                # Embedding Text
                text_vector = self.text_model.encode(full_text).tolist()
                text_batch.append(models.PointStruct(id=p_id, vector=text_vector, payload=payload))

                # --- 3. Xử lý Image ---
                # Lấy link ảnh đầu tiên từ list
                img_url = self.extract_image_url(row['images'])
                
                if img_url:
                    img_obj = self.download_image(img_url)
                    if img_obj:
                        image_vector = self.image_model.encode(img_obj).tolist()
                        image_batch.append(models.PointStruct(id=p_id, vector=image_vector, payload=payload))
                        success_img_count += 1

                # --- 4. Upload Batch ---
                if len(text_batch) >= batch_size:
                    self.text_db.upsert_points(text_batch)
                    text_batch = []

                if len(image_batch) >= batch_size:
                    self.image_db.upsert_points(image_batch)
                    image_batch = []
                    print(f"--> Uploaded batch Image at index {index} (Total images: {success_img_count})")

            except Exception as e:
                # print(f"[ERR] Row {index}: {e}")
                continue

        # Upload nốt phần dư
        if text_batch: self.text_db.upsert_points(text_batch)
        if image_batch: self.image_db.upsert_points(image_batch)

        print(f"[SUCCESS] Finished! Total Images Ingested: {success_img_count}/{total_rows}")

if __name__ == "__main__":
    # Lưu ý: Thay đổi đường dẫn file csv cho đúng vị trí trên máy bạn
    ingestor = DataIngestion(csv_path="data/asos_products.csv")
    
    # Chạy full (để batch_size=50 hoặc 100 cho ổn định)
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