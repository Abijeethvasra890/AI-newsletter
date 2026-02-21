from pydantic import BaseModel, Field
from typing import List


class ExtractedArticle(BaseModel):
    id: int
    summary: str = Field(..., min_length=20)
    why_it_matters: str = Field(..., min_length=20)
    key_points: List[str] = Field(..., min_items=1, max_items=5)


class ExtractionResponse(BaseModel):
    articles: List[ExtractedArticle]
