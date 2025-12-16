## Set up Terminal: Chỉ lần đầu tiên vào dự án 
#### Bước 1: Tạo môi trường ảo
```
&"C:\Users\admin\AppData\Local\Programs\Python\Python310\python.exe" -m venv venv
(Thay bằng đường dẫn tuyệt đối Python trong máy bạn nhé)
```

#### Bước 2: Tải các thư viện cần thiết
```
pip install -r requirements.txt
```

#### Bước 3: Ghi lại phiên bản được tải bởi pip
```
pip freeze -r requirements.txt
```
---

## Các lần sau quay lại dự án
#### Bước 1: Tái khởi động môi trường: 
```
venv\Scripts\activate
```

#### Bước 2: Reset Database
```
python reset_db.py
```

**Optional: Chạy Unit test cho Text và Image Embedding**
```
python test_logic.py
```

---
## Chạy Luồng chính
#### Bước 1: Chạy Ingest data (Chỉ chạy 1 lần đầu tiên thôi, các lần sau bỏ qua bước này)
```
python run_ingest.py
``` 
**Đảm bảo sau khi chạy đã tạo được các collections**

#### Bước 2: Chạy Backend
```
uvicorn api.main:app --reload
```
---

#### Bước 3: Test API- Truy cập http://127.0.0.1:8000/docs
**Mẫu Input để nhập**
```
{
  "query": "shoes",
  "search_type": "text",
  "top_k": 5,
  "filter_brand": "adidas"
}
```
---

**Output**
```
[
  {
    "product_id": 12,
    "product_name": "adidas Women's Sooraj Sneaker",
    "brand": "adidas",
    "price": "\"44.99\"",
    "image_url": "https://m.media-amazon.com/images/I/81xxvsms7-L._AC_UX575_.jpg",
    "score": 0.5086859
  },
  {
    "product_id": 85,
    "product_name": "adidas Men's Ultraboost Personal Best Running Shoe",
    "brand": "adidas",
    "price": "\"107\"",
    "image_url": "https://m.media-amazon.com/images/I/81huEKmoz1L._AC_UX695_.jpg",
    "score": 0.4832937
  },
  {
    "product_id": 15,
    "product_name": "adidas unisex-child Racer Tr21",
    "brand": "adidas",
    "price": "\"32.45\"",
    "image_url": "https://m.media-amazon.com/images/I/711YXKSxaqL.__AC_SY395_SX395_QL70_FMwebp_.jpg",
    "score": 0.46796548
  },
  {
    "product_id": 89,
    "product_name": "adidas Women's Gamecourt 2 Tennis Shoe",
    "brand": "adidas",
    "price": "\"57.04\"",
    "image_url": "https://m.media-amazon.com/images/I/61H485FBGQL.__AC_SY395_SX395_QL70_FMwebp_.jpg",
    "score": 0.45603645
  },
  {
    "product_id": 51,
    "product_name": "adidas Men's Racer Tr21 Running Shoe",
    "brand": "adidas",
    "price": "\"53\"",
    "image_url": "https://m.media-amazon.com/images/I/71J8YYAb1WL._AC_UX695_.jpg",
    "score": 0.43329236
  }
]
Response head
```
---
![Ảnh1](Swagger_UI1.png)

---
![Ảnh2](Swagger_UI2.png)
