from pydantic import BaseModel, Field
from typing import List


class RankedItem(BaseModel):
    id: int = Field(..., ge=0)
    score: float = Field(..., ge=0, le=10)


class RankingResponse(BaseModel):
    ranked_articles: List[RankedItem]
