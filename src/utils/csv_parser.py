import json
import pandas as pd
from src.config import Config


def load_catalog(csv_path: str = None) -> pd.DataFrame:
    path = csv_path or Config.DEFAULT_CATALOG
    df = pd.read_csv(path)
    df["genres_parsed"] = df["genres"].apply(_parse_genres)
    df["release_year"] = pd.to_datetime(df["release_date"], errors="coerce").dt.year
    return df


def _parse_genres(genres_str: str) -> list[str]:
    try:
        items = json.loads(genres_str)
        return [item["name"] for item in items]
    except Exception:
        return []


def get_genre_counts(df: pd.DataFrame) -> dict[str, int]:
    counts: dict[str, int] = {}
    for genres in df["genres_parsed"]:
        for g in genres:
            counts[g] = counts.get(g, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))


def get_language_counts(df: pd.DataFrame) -> dict[str, int]:
    return df["original_language"].value_counts().to_dict()


def get_year_counts(df: pd.DataFrame) -> dict[str, int]:
    return (
        df["release_year"]
        .dropna()
        .astype(int)
        .value_counts()
        .sort_index()
        .to_dict()
    )
