from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()


class SearchPayload(BaseModel):
    query: Optional[str] = None
    brand: Optional[str] = None
    color: Optional[str] = None


@app.post("/search")
def search_products(req: SearchPayload) -> List[int]:
    """
    Giả lập AI search / image search
    Trả về list sku
    """

    # Mock logic
    if req.brand and req.brand.lower() == "Asos":
        return [126704571, 123650194]

    if req.color and req.color.lower() == "BLACK":
        return [1005, 1006, 1007]

    return [125806824]
