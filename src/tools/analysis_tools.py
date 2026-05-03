import json
from langchain_core.tools import tool
from src.utils.csv_parser import load_catalog, get_genre_counts
from src.utils.tmdb_client import fetch_genre_benchmarks

_df = None


def _get_df():
    global _df
    if _df is None:
        _df = load_catalog()
    return _df


def set_catalog_path(path: str):
    global _df
    from src.utils.csv_parser import load_catalog as lc
    _df = lc(path)


def _get_benchmarks() -> dict[str, float]:
    """TMDB API'den gerçek benchmark'ları çeker."""
    return fetch_genre_benchmarks()


@tool
def find_underrepresented_genres() -> str:
    """TMDB global popülerlik verisine kıyasla katalogda az temsil edilen türleri bulur."""
    df = _get_df()
    counts = get_genre_counts(df)
    total = sum(counts.values())
    benchmarks = _get_benchmarks()
    result = []
    for genre, benchmark_pct in benchmarks.items():
        catalog_pct = round(counts.get(genre, 0) / total * 100, 1)
        if catalog_pct < benchmark_pct * 0.7:
            result.append({
                "genre": genre,
                "catalog_pct": catalog_pct,
                "tmdb_benchmark_pct": benchmark_pct,
                "gap": round(benchmark_pct - catalog_pct, 1),
                "source": "TMDB Popular Movies (500 film)"
            })
    return json.dumps(sorted(result, key=lambda x: x["gap"], reverse=True))


@tool
def find_overrepresented_genres() -> str:
    """TMDB global popülerlik verisine kıyasla katalogda fazla temsil edilen türleri bulur."""
    df = _get_df()
    counts = get_genre_counts(df)
    total = sum(counts.values())
    benchmarks = _get_benchmarks()
    result = []
    for genre, benchmark_pct in benchmarks.items():
        catalog_pct = round(counts.get(genre, 0) / total * 100, 1)
        if catalog_pct > benchmark_pct * 1.5:
            result.append({
                "genre": genre,
                "catalog_pct": catalog_pct,
                "tmdb_benchmark_pct": benchmark_pct,
                "surplus": round(catalog_pct - benchmark_pct, 1),
                "source": "TMDB Popular Movies (500 film)"
            })
    return json.dumps(sorted(result, key=lambda x: x["surplus"], reverse=True))


@tool
def get_tmdb_genre_benchmarks() -> str:
    """TMDB API'den çekilen gerçek dünya tür dağılım benchmark'larını döndürür."""
    benchmarks = _get_benchmarks()
    return json.dumps({
        "source": "TMDB Popular Movies API (500 film, 5 sayfa)",
        "benchmarks": benchmarks
    })


@tool
def analyze_recent_content_ratio() -> str:
    """Son 5 yılın (2019-2024) içerik oranını hesaplar."""
    df = _get_df()
    total = len(df)
    recent = len(df[df["release_year"] >= 2019])
    older = total - recent
    return json.dumps({
        "total": total,
        "recent_2019_plus": recent,
        "recent_pct": round(recent / total * 100, 1),
        "older": older,
        "older_pct": round(older / total * 100, 1),
    })


@tool
def analyze_language_diversity() -> str:
    """İngilizce dışı içeriklerin oranını ve dil çeşitliliğini analiz eder."""
    df = _get_df()
    total = len(df)
    lang_counts = df["original_language"].value_counts().to_dict()
    en_count = lang_counts.get("en", 0)
    non_en = total - en_count
    return json.dumps({
        "total": total,
        "english": en_count,
        "english_pct": round(en_count / total * 100, 1),
        "non_english": non_en,
        "non_english_pct": round(non_en / total * 100, 1),
        "unique_languages": len(lang_counts),
        "top_non_english": {k: v for k, v in list(lang_counts.items())[1:6]},
    })


ALL_ANALYSIS_TOOLS = [
    find_underrepresented_genres,
    find_overrepresented_genres,
    get_tmdb_genre_benchmarks,
    analyze_recent_content_ratio,
    analyze_language_diversity,
]
