from pydantic import BaseModel
from typing import Optional


class GenreStats(BaseModel):
    genre: str
    count: int
    percentage: float


class CatalogSummary(BaseModel):
    total_movies: int
    top_genres: list[GenreStats]
    language_distribution: dict[str, int]
    year_distribution: dict[str, int]
    avg_popularity: float
    avg_vote: float
    analysis_text: str


class GapItem(BaseModel):
    category: str
    description: str
    severity: str  # "Kritik" | "Orta" | "Düşük"
    recommendation: str


class GapReport(BaseModel):
    underrepresented_genres: list[str]
    overrepresented_genres: list[str]
    gaps: list[GapItem]
    analysis_text: str


class FinalReport(BaseModel):
    executive_summary: str
    catalog_highlights: list[str]
    critical_gaps: list[str]
    purchase_recommendations: list[str]
    conclusion: str
