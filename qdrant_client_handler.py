from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Any, Optional

class QdrantHandler:
    def __init__(self, collection_name: str, vector_size: int):
        self.client = QdrantClient(url="http://localhost:6333")
        self.collection_name = collection_name
        self.vector_size = vector_size
        self._create_collection_if_not_exists()

    def _create_collection_if_not_exists(self):
        collections = self.client.get_collections()
        exists = any(c.name == self.collection_name for c in collections.collections)
        
        if not exists:
            print(f"[INFO] Creating collection: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.vector_size,
                    distance=models.Distance.COSINE
                )
            )

    def upsert_points(self, points: List[models.PointStruct]):
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def search(self, query_vector: List[float], limit: int = 12, filter_criteria: Optional[Dict] = None):
        """
        filter_criteria: Dict {'brand': 'Nike', 'color': 'Pink'}
        """
        # 1. Tạo bộ lọc (Filter)
        query_filter = None
        if filter_criteria:
            must_conditions = []
            for key, value in filter_criteria.items():
                if value and str(value).strip() != "":
                    # MatchValue (Exact match) cho chuỗi
                    must_conditions.append(
                        models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=value)
                        )
                    )
            if must_conditions:
                query_filter = models.Filter(must=must_conditions)

        # 2. Thực hiện Search (Fallback version)
        try:
            return self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=limit
            )
        except (AttributeError, TypeError):
            response = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                query_filter=query_filter,
                limit=limit
            )
            return response.points

# Bản 1:
# from qdrant_client import QdrantClient
# from qdrant_client.http import models
# from typing import List, Dict, Any, Optional

# class QdrantHandler:
#     def __init__(self, collection_name: str, vector_size: int):
#         # Khởi tạo client local
#         self.client = QdrantClient(url="http://localhost:6333")
#         self.collection_name = collection_name
#         self.vector_size = vector_size
#         self._create_collection_if_not_exists()

#     def _create_collection_if_not_exists(self):
#         collections = self.client.get_collections()
#         exists = any(c.name == self.collection_name for c in collections.collections)
        
#         if not exists:
#             print(f"[INFO] Creating collection: {self.collection_name}")
#             self.client.create_collection(
#                 collection_name=self.collection_name,
#                 vectors_config=models.VectorParams(
#                     size=self.vector_size,
#                     distance=models.Distance.COSINE
#                 )
#             )
#         else:
#             print(f"[INFO] Collection {self.collection_name} already exists.")

#     def upsert_points(self, points: List[models.PointStruct]):
#         self.client.upsert(
#             collection_name=self.collection_name,
#             points=points
#         )

#     def search(self, query_vector: List[float], limit: int = 5, filter_criteria: Optional[Dict] = None):
#         """Tìm kiếm vector tương đồng, hỗ trợ đa phiên bản Qdrant."""
        
#         # 1. Tạo bộ lọc (Filter)
#         query_filter = None
#         if filter_criteria:
#             must_conditions = []
#             for key, value in filter_criteria.items():
#                 if value:
#                     must_conditions.append(
#                         models.FieldCondition(
#                             key=key,
#                             match=models.MatchValue(value=value)
#                         )
#                     )
#             if must_conditions:
#                 query_filter = models.Filter(must=must_conditions)

#         # 2. Thực hiện Search (Xử lý lỗi version)
#         try:
#             # Cách 1: Dùng .search() (API chuẩn cũ)
#             return self.client.search(
#                 collection_name=self.collection_name,
#                 query_vector=query_vector,
#                 query_filter=query_filter,
#                 limit=limit
#             )
#         except (AttributeError, TypeError):
#             # Cách 2: Dùng .query_points() (API mới/local)
#             # Lưu ý: Sửa 'filter' thành 'query_filter' ở đây
#             response = self.client.query_points(
#                 collection_name=self.collection_name,
#                 query=query_vector,
#                 query_filter=query_filter,  # <--- Đã sửa tên tham số này
#                 limit=limit
#             )
#             return response.points