from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Article(BaseModel):
    title: str
    url: str
    source: str
    published_at: str
    score: Optional[float] = None
    summary: Optional[str] = None
    why_it_matters: Optional[str] = None
    key_points: Optional[List[str]] = None

class NewsletterState(BaseModel):
    run_id: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    region: str = "India"

    raw_articles: List[Article] = []
    ranked_articles: List[Article] = []
    processed_articles: List[Article] = []

    drafted_markdown: Optional[str] = None
    final_markdown: Optional[str] = None
    final_html: Optional[str] = None

    quality_score: Optional[float] = None
    errors: List[str] = []

    final_newsletter: str = ""
