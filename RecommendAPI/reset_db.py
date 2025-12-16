from qdrant_client import QdrantClient

def reset_database():
    # Kết nối tới Qdrant đang chạy trên Docker
    print("[INFO] Connecting to Qdrant at http://localhost:6333...")
    client = QdrantClient(url="http://localhost:6333")

    collections_to_delete = ["products_text", "products_image"]

    for col_name in collections_to_delete:
        try:
            # Kiểm tra xem collection có tồn tại không
            client.get_collection(col_name)
            
            # Nếu có thì xóa
            client.delete_collection(collection_name=col_name)
            print(f"[SUCCESS] Deleted collection: {col_name}")
        except Exception as e:
            # Nếu collection không tồn tại (lỗi 404) hoặc lỗi khác
            if "Not found" in str(e) or "404" in str(e):
                print(f"[INFO] Collection '{col_name}' not found (already deleted).")
            else:
                print(f"[ERR] Error deleting '{col_name}': {e}")

if __name__ == "__main__":
    reset_database()