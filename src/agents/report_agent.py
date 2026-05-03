from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

from src.config import Config
from src.prompts import REPORT_AGENT_PROMPT
from src.schemas import CatalogSummary, GapReport, FinalReport


def _get_llm():
    if Config.LLM_PROVIDER == "groq":
        return ChatGroq(api_key=Config.GROQ_API_KEY, model=Config.GROQ_MODEL)
    elif Config.LLM_PROVIDER == "anthropic":
        return ChatAnthropic(api_key=Config.ANTHROPIC_API_KEY, model=Config.ANTHROPIC_MODEL)
    else:
        return ChatOpenAI(api_key=Config.OPENAI_API_KEY, model=Config.OPENAI_MODEL)


def run_report_agent(catalog_summary: CatalogSummary, gap_report: GapReport) -> FinalReport:
    Config.validate()
    llm = _get_llm()

    context = f"""
KATALOG ANALİZİ:
- Toplam film: {catalog_summary.total_movies}
- Ortalama popülerlik: {catalog_summary.avg_popularity}
- Ortalama oy: {catalog_summary.avg_vote}
- En çok türler: {', '.join([g.genre for g in catalog_summary.top_genres[:5]])}
- Analiz: {catalog_summary.analysis_text}

BOŞLUK RAPORU:
- Az temsil edilen türler: {', '.join(gap_report.underrepresented_genres)}
- Fazla temsil edilen türler: {', '.join(gap_report.overrepresented_genres)}
- Boşluklar:
{chr(10).join([f"  [{g.severity}] {g.category}: {g.description} → {g.recommendation}" for g in gap_report.gaps])}
- Analiz: {gap_report.analysis_text}
"""

    structured_llm = llm.with_structured_output(FinalReport)
    final_report = structured_llm.invoke(
        f"{REPORT_AGENT_PROMPT}\n\nVERİLER:\n{context}\n\n"
        f"Bu verilere dayanarak FinalReport formatında profesyonel bir rapor üret."
    )
    return final_report
