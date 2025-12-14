from embedding.ingest import DataIngestion

if __name__ == "__main__":
    # Đảm bảo bạn đã tải file CSV mới vào thư mục data và đổi tên thành asos_products.csv
    # Hoặc sửa tên file ở dòng dưới đây cho khớp
    csv_file = "data/asos_products.csv"
    
    print(f"--- Starting Ingest Process for {csv_file} ---")
    ingestor = DataIngestion(csv_path=csv_file)
    
    # Batch size 50 để cân bằng giữa tốc độ và ổn định
    ingestor.process_and_ingest(batch_size=50)

# Bản 1:
# # run_ingest.py
# from embedding.ingest import DataIngestion

# if __name__ == "__main__":
#     # Đảm bảo đường dẫn tới file CSV là đúng
#     ingestor = DataIngestion(csv_path=r"C:\Users\admin\OneDrive - National Economics University\Desktop\Các Folder\Multimodal_RecSys\data\product.csv")
#     ingestor.process_and_ingest()