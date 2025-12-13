import pandas as pd
import requests
from PIL import Image
from io import BytesIO
from sentence_transformers import SentenceTransformer
from vectordb.qdrant_client_handler import QdrantHandler
from qdrant_client.http import models
import ast

class DataIngestion:
    def __init__(self, csv_path: str):
        self.df = pd.read_csv(csv_path)
        
        # Load Models
        print("[INFO] Loading Text Embedding Model...")
        self.text_model = SentenceTransformer('all-MiniLM-L6-v2') # Output dim: 384
        
        print("[INFO] Loading Image Embedding Model...")
        self.image_model = SentenceTransformer('clip-ViT-B-32')   # Output dim: 512
        
        # Init Vector DB Clients (2 collections riêng biệt)
        self.text_db = QdrantHandler(collection_name="products_text", vector_size=384)
        self.image_db = QdrantHandler(collection_name="products_image", vector_size=512)

    def download_image(self, url: str):
        """Tải ảnh từ URL và convert sang PIL Image"""
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return Image.open(BytesIO(response.content)).convert("RGB")
        except Exception as e:
            print(f"[WARN] Cannot download image {url}: {e}")
            return None

    def process_and_ingest(self):
        text_points = []
        image_points = []

        print(f"[INFO] Start processing {len(self.df)} products...")

        for index, row in self.df.iterrows():
            p_id = int(row['Product_id'])
            
            # --- 1. Xử lý Metadata ---
            # Parse Categories string "['a', 'b']" thành list thực tế nếu cần, hoặc giữ string
            try:
                categories = ast.literal_eval(row['Categories']) if isinstance(row['Categories'], str) else []
                # Lấy category chính (phần tử đầu tiên) để lọc cho dễ
                main_category = categories[0] if len(categories) > 0 else "Unknown"
            except:
                main_category = "Unknown"

            payload = {
                "product_id": p_id,
                "product_name": row['Product_Name'],
                "brand": str(row['Brand']),
                "price": row['Final_Price'],
                "image_url": row['Image_URL'],
                "main_category": main_category
            }

            # --- 2. Text Embedding ---
            # Kết hợp các trường text để model hiểu ngữ cảnh tốt hơn
            full_text = f"{row['Product_Name']}. Brand: {row['Brand']}. {row['Description']}"
            text_vector = self.text_model.encode(full_text).tolist()
            
            text_points.append(models.PointStruct(
                id=p_id,
                vector=text_vector,
                payload=payload
            ))

            # --- 3. Image Embedding ---
            img_obj = self.download_image(row['Image_URL'])
            if img_obj:
                image_vector = self.image_model.encode(img_obj).tolist()
                image_points.append(models.PointStruct(
                    id=p_id,
                    vector=image_vector,
                    payload=payload
                ))
            else:
                print(f"[SKIP] Product {p_id} has no valid image.")

            # Print Input/Output progress (Mỗi 5 items in 1 lần cho đỡ rối)
            if index % 5 == 0:
                print(f"--> Processed ID: {p_id} | Brand: {payload['brand']} | Text Vec Len: {len(text_vector)}")

        # --- 4. Upload to DB ---
        if text_points:
            print(f"[INFO] Uploading {len(text_points)} text vectors to Qdrant...")
            self.text_db.upsert_points(text_points)
        
        if image_points:
            print(f"[INFO] Uploading {len(image_points)} image vectors to Qdrant...")
            self.image_db.upsert_points(image_points)
            
        print("[SUCCESS] Ingestion Finished!")

# File chạy riêng lẻ để test
if __name__ == "__main__":
    ingestor = DataIngestion(csv_path="data/products.csv")
    ingestor.process_and_ingest()