from embedding.ingest import DataIngestion
import os

if __name__ == "__main__":
    # Đường dẫn file CSV
    csv_file = os.path.join("data", "asos_products.csv")
    
    # Đường dẫn thư mục chứa ảnh
    images_dir = os.path.join("data", "images")
    
    print(f"--- Starting Ingest (CSV: {csv_file}, Images: {images_dir}) ---")
    
    # Khởi tạo với đường dẫn folder ảnh
    ingestor = DataIngestion(csv_path=csv_file, images_folder=images_dir)
    
    # Chạy xử lý
    ingestor.process_and_ingest(batch_size=100) # Local nhanh nên tăng batch size lên 100

# Bản 2:
# from embedding.ingest import DataIngestion

# if __name__ == "__main__":
#     csv_file = "data/asos_products.csv"
    
#     print(f"--- Starting Ingest Process for {csv_file} ---")
#     ingestor = DataIngestion(csv_path=csv_file)
    
#     # LƯU Ý: Giảm batch_size xuống 5 để test tốc độ
#     ingestor.process_and_ingest(batch_size=5)

# Bản 1:
# # run_ingest.py
# from embedding.ingest import DataIngestion

# if __name__ == "__main__":
#     # Đảm bảo đường dẫn tới file CSV là đúng
#     ingestor = DataIngestion(csv_path=r"C:\Users\admin\OneDrive - National Economics University\Desktop\Các Folder\Multimodal_RecSys\data\product.csv")
#     ingestor.process_and_ingest()