from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from src.config import Config
from src.prompts import GAP_AGENT_PROMPT
from src.schemas import CatalogSummary, GapReport
from src.tools.analysis_tools import ALL_ANALYSIS_TOOLS


def _get_llm():
    if Config.LLM_PROVIDER == "groq":
        return ChatGroq(api_key=Config.GROQ_API_KEY, model=Config.GROQ_MODEL)
    elif Config.LLM_PROVIDER == "anthropic":
        return ChatAnthropic(api_key=Config.ANTHROPIC_API_KEY, model=Config.ANTHROPIC_MODEL)
    else:
        return ChatOpenAI(api_key=Config.OPENAI_API_KEY, model=Config.OPENAI_MODEL)


def run_gap_agent(catalog_summary: CatalogSummary) -> GapReport:
    Config.validate()
    llm = _get_llm()
    agent = create_react_agent(llm, ALL_ANALYSIS_TOOLS, prompt=GAP_AGENT_PROMPT)

    human_msg = (
        f"Katalog analizi tamamlandı. Özet:\n"
        f"- Toplam film: {catalog_summary.total_movies}\n"
        f"- Ortalama popülerlik: {catalog_summary.avg_popularity}\n"
        f"- Analiz: {catalog_summary.analysis_text[:300]}\n\n"
        f"Şimdi boşluk analizini yap."
    )

    result = agent.invoke({"messages": [("human", human_msg)]})
    raw_output = result["messages"][-1].content

    structured_llm = llm.with_structured_output(GapReport)
    gap_report = structured_llm.invoke(
        f"Aşağıdaki boşluk analizini GapReport formatına dönüştür. "
        f"gaps listesinde her boşluk için category, description, severity (Kritik/Orta/Düşük) "
        f"ve recommendation alanlarını doldur.\n\n{raw_output}"
    )
    return gap_report
