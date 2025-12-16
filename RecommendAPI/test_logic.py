import ast
import numpy as np
from PIL import Image
from sentence_transformers import SentenceTransformer
import os

# ==========================================
# 1. HÀM XỬ LÝ TEXT (Logic trích xuất từ ingest.py)
# ==========================================
def extract_clean_description(desc_col_data):
    print("\n[LOGIC] Đang xử lý chuỗi Description thô...")
    try:
        # Chuyển chuỗi string thành List các Dict
        data_list = ast.literal_eval(str(desc_col_data))
        
        text_parts = []
        if isinstance(data_list, list):
            for item in data_list:
                if isinstance(item, dict):
                    # Lấy tất cả các value trong dict (bỏ qua key)
                    text_parts.extend(item.values())
        
        # Gộp lại thành 1 chuỗi, ngăn cách bằng dấu chấm
        return ". ".join([str(t) for t in text_parts])
    except Exception as e:
        return f"Error: {str(e)}"

# ==========================================
# 2. DỮ LIỆU INPUT MẪU (Lấy từ ví dụ của bạn)
# ==========================================
raw_description_input = "[{'Product Details': 'Coats & Jackets by Nike RunningHit that new PBToggle hoodZip fasteningNike logo print to chestZip side pocketsReflective details for increased visibility in low lightingElasticated cuffsRegular fitProduct Code: 121963507'}, {'Brand': 'Key players in everything activewear-related, it doesn t get more iconic than Nike. Sporting some of the most wanted trainers in the game, browse Air Max 90s and Air Force 1s, as well as Cortez and Joyride styles. Get off-duty looks down with tracksuits, T-shirts and accessories in our Nike at ASOS edit, or scroll performance leggings and sports bras from Nike Training and Nike Running for an extra dose of motivation.'}, {'Size & Fit': 'Model\\'s height: 174cm/5\\'8.5\"Model is wearing: UK S/ EU S/ US XS'}, {'Look After Me': 'Machine wash according to instructions on care label'}, {'About Me': 'Water-repellent fabricMain: 100% Polyester.'}]"

# ==========================================
# 3. CHẠY TEST
# ==========================================
def run_test():
    print("=== BẮT ĐẦU KIỂM TRA LOGIC MODEL & DỮ LIỆU ===")

    # --- PHẦN 1: KIỂM TRA XỬ LÝ TEXT ---
    print(f"\n1. INPUT Description (Raw string):")
    print(f"   {raw_description_input[:100]}... (đã cắt bớt cho gọn)")
    
    cleaned_text = extract_clean_description(raw_description_input)
    
    print(f"\n2. OUTPUT Description (Cleaned text):")
    print(f"   {cleaned_text}")
    print(f"   -> Độ dài chuỗi: {len(cleaned_text)} ký tự")

    # --- PHẦN 2: KIỂM TRA MODEL EMBEDDING ---
    print("\n" + "="*30)
    print("\n[MODEL] Đang tải model clip-ViT-B-32 (Vui lòng đợi)...")
    try:
        model = SentenceTransformer('clip-ViT-B-32')
        print("-> Model tải thành công!")
    except Exception as e:
        print(f"-> Lỗi tải model: {e}")
        return

    # --- Embedding Text ---
    print(f"\n3. TEST EMBEDDING TEXT:")
    # Mô phỏng việc cắt ngắn text để fit vào CLIP (thường CLIP nhận tối đa 77 tokens)
    input_text_for_model = cleaned_text[:300] 
    vector_text = model.encode(input_text_for_model)
    
    print(f"   -> Input cho model: '{input_text_for_model[:50]}...'")
    print(f"   -> Kích thước Vector (Dimension): {vector_text.shape}")
    print(f"   -> 5 giá trị đầu tiên: {vector_text[:5]}")

    if vector_text.shape[0] == 512:
        print("   -> [OK] Vector Text chuẩn size 512.")
    else:
        print("   -> [WARN] Vector Text sai kích thước!")

    # --- Embedding Ảnh ---
    print(f"\n4. TEST EMBEDDING IMAGE:")
    
    # Tạo một ảnh giả lập (Dummy Image) màu đỏ để test logic encode
    # Bạn không cần file ảnh thật để chạy script này
    dummy_image = Image.new('RGB', (224, 224), color='red')
    print("   -> Đã tạo một ảnh giả lập (Màu đỏ, size 224x224) trong RAM.")
    
    vector_image = model.encode(dummy_image)
    
    print(f"   -> Kích thước Vector Ảnh (Dimension): {vector_image.shape}")
    print(f"   -> 5 giá trị đầu tiên: {vector_image[:5]}")

    if vector_image.shape[0] == 512:
        print("   -> [OK] Vector Ảnh chuẩn size 512.")
    else:
        print("   -> [WARN] Vector Ảnh sai kích thước!")

    print("\n=== KẾT THÚC BÀI TEST ===")

if __name__ == "__main__":
    run_test()