from src.schemas import CatalogSummary, GapReport, FinalReport
from src.agents.catalog_agent import run_catalog_agent
from src.agents.gap_agent import run_gap_agent
from src.agents.report_agent import run_report_agent
from src.tools import catalog_tools, analysis_tools


def analyze_catalog(csv_path: str = None) -> tuple[CatalogSummary, GapReport, FinalReport]:
    if csv_path:
        catalog_tools.set_catalog_path(csv_path)
        analysis_tools.set_catalog_path(csv_path)

    catalog_summary = run_catalog_agent()
    gap_report = run_gap_agent(catalog_summary)
    final_report = run_report_agent(catalog_summary, gap_report)

    return catalog_summary, gap_report, final_report
