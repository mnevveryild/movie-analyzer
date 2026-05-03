import requests
from functools import lru_cache
from src.config import Config

TMDB_BASE = "https://api.themoviedb.org/3"


def _params(extra: dict = None) -> dict:
    p = {"api_key": Config.TMDB_API_KEY, "language": "en-US"}
    if extra:
        p.update(extra)
    return p


@lru_cache(maxsize=1)
def fetch_genre_benchmarks() -> dict[str, float]:
    """TMDB'den popüler filmlerin tür dağılımını çekip yüzde olarak döndürür."""
    genre_map = _fetch_genre_map()
    counts: dict[str, int] = {}
    total = 0

    for page in range(1, 6):
        resp = requests.get(
            f"{TMDB_BASE}/movie/popular",
            params=_params({"page": page}),
            timeout=10,
        )
        resp.raise_for_status()
        movies = resp.json().get("results", [])
        for movie in movies:
            for gid in movie.get("genre_ids", []):
                name = genre_map.get(gid)
                if name:
                    counts[name] = counts.get(name, 0) + 1
                    total += 1

    if total == 0:
        return {}

    return {genre: round(count / total * 100, 1) for genre, count in counts.items()}


def _fetch_genre_map() -> dict[int, str]:
    resp = requests.get(
        f"{TMDB_BASE}/genre/movie/list",
        params=_params(),
        timeout=10,
    )
    resp.raise_for_status()
    genres = resp.json().get("genres", [])
    return {g["id"]: g["name"] for g in genres}
