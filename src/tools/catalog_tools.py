import json
from langchain_core.tools import tool
from src.utils.csv_parser import load_catalog, get_genre_counts, get_language_counts, get_year_counts

_df = None


def _get_df():
    global _df
    if _df is None:
        _df = load_catalog()
    return _df


def set_catalog_path(path: str):
    global _df
    _df = load_catalog(path)


@tool
def get_catalog_stats() -> str:
    """Katalogdaki toplam film sayısı, ortalama popülerlik ve oy ortalamasını döndürür."""
    df = _get_df()
    return json.dumps({
        "total_movies": len(df),
        "avg_popularity": round(df["popularity"].mean(), 2),
        "avg_vote": round(df["vote_average"].mean(), 2),
        "date_range": f"{int(df['release_year'].min())}-{int(df['release_year'].max())}"
    })


@tool
def get_genre_distribution() -> str:
    """Katalogdaki film türlerinin dağılımını ve yüzdelerini döndürür."""
    df = _get_df()
    counts = get_genre_counts(df)
    total = sum(counts.values())
    result = [
        {"genre": g, "count": c, "percentage": round(c / total * 100, 1)}
        for g, c in list(counts.items())[:15]
    ]
    return json.dumps(result)


@tool
def get_language_distribution() -> str:
    """Katalogdaki dil dağılımını döndürür."""
    df = _get_df()
    counts = get_language_counts(df)
    top = dict(list(counts.items())[:10])
    return json.dumps(top)


@tool
def get_year_distribution() -> str:
    """Yıllara göre film sayısı dağılımını döndürür."""
    df = _get_df()
    counts = get_year_counts(df)
    return json.dumps(counts)


@tool
def get_top_movies_by_genre(genre: str) -> str:
    """Belirli bir türdeki en popüler 10 filmi döndürür."""
    df = _get_df()
    filtered = df[df["genres_parsed"].apply(lambda g: genre in g)]
    top = filtered.nlargest(10, "popularity")[["title", "popularity", "vote_average", "release_year"]]
    return top.to_json(orient="records")


@tool
def get_decade_distribution() -> str:
    """On yıllara göre film sayısı dağılımını döndürür."""
    df = _get_df()
    df2 = df.copy()
    df2["decade"] = (df2["release_year"] // 10 * 10).astype("Int64")
    counts = df2["decade"].value_counts().sort_index().to_dict()
    return json.dumps({str(k): v for k, v in counts.items()})


ALL_CATALOG_TOOLS = [
    get_catalog_stats,
    get_genre_distribution,
    get_language_distribution,
    get_year_distribution,
    get_top_movies_by_genre,
    get_decade_distribution,
]
