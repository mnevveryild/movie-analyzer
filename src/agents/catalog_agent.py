from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from pydantic import ValidationError

from src.config import Config
from src.prompts import CATALOG_AGENT_PROMPT
from src.schemas import CatalogSummary, GenreStats
from src.tools.catalog_tools import ALL_CATALOG_TOOLS
import json


def _get_llm():
    if Config.LLM_PROVIDER == "groq":
        return ChatGroq(api_key=Config.GROQ_API_KEY, model=Config.GROQ_MODEL)
    elif Config.LLM_PROVIDER == "anthropic":
        return ChatAnthropic(api_key=Config.ANTHROPIC_API_KEY, model=Config.ANTHROPIC_MODEL)
    else:
        return ChatOpenAI(api_key=Config.OPENAI_API_KEY, model=Config.OPENAI_MODEL)


def run_catalog_agent() -> CatalogSummary:
    Config.validate()
    llm = _get_llm()
    agent = create_react_agent(llm, ALL_CATALOG_TOOLS, prompt=CATALOG_AGENT_PROMPT)
    result = agent.invoke({"messages": [("human", "Katalog analizini başlat ve kapsamlı bir analiz metni yaz.")]})
    raw_output = result["messages"][-1].content

    structured_llm = llm.with_structured_output(CatalogSummary)
    catalog_summary = structured_llm.invoke(
        f"Aşağıdaki analizi CatalogSummary formatına dönüştür. "
        f"top_genres için gerçek tür isimlerini ve yüzdelerini kullan. "
        f"Tüm alanları doldur.\n\n{raw_output}"
    )
    return catalog_summary
