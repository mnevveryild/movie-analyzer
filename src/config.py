import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    TMDB_API_KEY = os.getenv("TMDB_API_KEY")

    GROQ_MODEL = "llama-3.3-70b-versatile"
    ANTHROPIC_MODEL = "claude-3-5-haiku-20241022"
    OPENAI_MODEL = "gpt-4o-mini"

    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    DEFAULT_CATALOG = os.path.join(DATA_DIR, "tmdb_5000_movies.csv")

    @classmethod
    def validate(cls):
        if cls.LLM_PROVIDER == "groq" and not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY eksik")
        if cls.LLM_PROVIDER == "anthropic" and not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY eksik")
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY eksik")
