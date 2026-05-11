import streamlit as st
import sys
import os
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether,
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

sys.path.insert(0, os.path.dirname(__file__))

try:
    from src.orchestrator import analyze_catalog
    from src.config import Config
except ModuleNotFoundError as e:
    st.error(f"Modül içe aktarma hatası: {e}")

st.set_page_config(
    page_title="Tivibu · Katalog Analiz",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded", 
)

def apply_tivibu_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── BASE ── */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, sans-serif;
    }

    .stApp {
        background-color: #08192b;
        color: #ffffff;
    }

    /* Cyan top accent bar */
    .stApp::before {
        content: '';
        display: block;
        position: fixed;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #00deff, #FFD700, #00deff);
        z-index: 9999;
    }

    /* ── SIDEBAR ── */
    [data-testid="stSidebar"] {
        background-color: #051525 !important;
        border-right: 1px solid rgba(0,222,255,0.1) !important;
    }

    [data-testid="stSidebar"] * {
        color: #c0d8ee !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }

    /* ── HEADER ── */
    .tivibu-header {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 28px 0 20px;
        border-bottom: 1px solid rgba(0,222,255,0.12);
        margin-bottom: 28px;
    }

    .tivibu-logo-badge {
        background: #00deff;
        border-radius: 10px;
        padding: 10px 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        flex-shrink: 0;
    }

    .tivibu-title-block h1 {
        margin: 0;
        font-size: 1.6rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.5px;
        line-height: 1.1;
    }

    .tivibu-title-block h1 span {
        color: #00deff;
    }

    .tivibu-title-block p {
        margin: 4px 0 0;
        font-size: 0.82rem;
        color: #5580a0;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        font-weight: 500;
    }

    /* ── METRICS ── */
    [data-testid="stMetric"] {
        background: #0d2237 !important;
        border: 1px solid rgba(0,222,255,0.1) !important;
        border-radius: 14px !important;
        padding: 20px 22px !important;
        transition: border-color 0.25s, box-shadow 0.25s !important;
    }

    [data-testid="stMetric"]:hover {
        border-color: rgba(0,222,255,0.4) !important;
        box-shadow: 0 0 0 1px rgba(0,222,255,0.12), 0 8px 24px rgba(0,0,0,0.4) !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
        color: #5580a0 !important;
    }

    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        line-height: 1.1 !important;
    }

    /* ── TABS ── */
    [data-testid="stTabs"] [role="tablist"] {
        background: #0d2237;
        border-radius: 12px;
        padding: 4px;
        gap: 2px;
        border: 1px solid rgba(0,222,255,0.1);
    }

    [data-testid="stTabs"] [role="tab"] {
        border-radius: 9px !important;
        color: #5580a0 !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        padding: 8px 16px !important;
        transition: all 0.2s !important;
        border: none !important;
    }

    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        background: #ccff00 !important;
        color: #08192b !important;
        font-weight: 700 !important;
    }

    [data-testid="stTabs"] [role="tab"]:hover:not([aria-selected="true"]) {
        color: #00deff !important;
        background: rgba(0,222,255,0.06) !important;
    }

    [data-testid="stTabsContent"] {
        background: transparent !important;
        border: none !important;
        padding-top: 20px !important;
    }

    /* ── BUTTONS ── */
    .stButton > button {
        background: #ccff00 !important;
        color: #08192b !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 800 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.3px !important;
        padding: 12px 28px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 14px #ccff00 !important;
    }

    .stButton > button:hover {
        background: #ccff00 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px #ccff00 !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* ── EXPANDERS ── */
    [data-testid="stExpander"] {
        background: #0d2237 !important;
        border: 1px solid rgba(0,222,255,0.1) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }

    [data-testid="stExpander"]:hover {
        border-color: rgba(0,222,255,0.3) !important;
    }

    [data-testid="stExpander"] summary {
        font-weight: 600 !important;
        color: #0d2237 !important;
        padding: 14px 18px !important;
    }

    [data-testid="stExpander"] summary:hover {
        color: #00deff !important;
    }

    /* ── ALERTS ── */
    [data-testid="stAlert"] {
        border-radius: 12px !important;
        border-left-width: 3px !important;
    }

    [data-testid="stAlert"][data-baseweb="notification"] {
        background: rgba(0,222,255,0.06) !important;
        border-color: #00deff !important;
        color: #ffffff !important;
    }

    div[data-testid="stAlert"].element-container > div[class*="stError"] {
        background: rgba(239,68,68,0.08) !important;
        border-color: #ef4444 !important;
    }

    div[data-testid="stAlert"].element-container > div[class*="stWarning"] {
        background: #ccff00 !important;
        border-color: #FFD700 !important;
    }

    div[data-testid="stAlert"].element-container > div[class*="stSuccess"] {
        background: rgba(0,222,255,0.06) !important;
        border-color: #00deff !important;
    }

    /* ── CHARTS ── */
    [data-testid="stVegaLiteChart"],
    [data-testid="stArrowVegaLiteChart"] {
        background: #0d2237 !important;
        border-radius: 14px !important;
        border: 1px solid rgba(0,222,255,0.1) !important;
        padding: 16px !important;
    }

    /* ── STATUS ── */
    [data-testid="stStatus"] {
        background: #0d2237 !important;
        border: 1px solid rgba(0,222,255,0.2) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
    }

    /* ── DOWNLOAD BUTTON ── */
    [data-testid="stDownloadButton"] > button {
        background: #ccff00 !important;
        border: none !important;
        color: #08192b !important;
        border-radius: 9px !important;
        font-weight: 800 !important;
        box-shadow: 0 4px 14px #ccff00 !important;
    }

    [data-testid="stDownloadButton"] > button:hover {
        background: #ccff00 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px #ccff00 !important;
    }

    /* ── DIVIDER ── */
    hr {
        border-color: rgba(0,222,255,0.1) !important;
    }

    /* ── HEADINGS ── */
    h1, h2, h3, h4, h5 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    p, li, .stMarkdown {
        color: #ffffff !important;
    }

    /* ── INFO BOX ── */
    .stInfo {
        background: rgba(0,222,255,0.06) !important;
        border-left: 3px solid #00deff !important;
        color: #0d2237 !important;
    }

    /* ── SEVERITY BADGE helpers ── */
    .badge-kritik {
        display: inline-block;
        background: rgba(239,68,68,0.15);
        color: #f87171;
        border: 1px solid rgba(239,68,68,0.3);
        border-radius: 6px;
        padding: 2px 10px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-right: 6px;
    }

    .badge-orta {
        display: inline-block;
        background: #ccff00;
        color: #FFD700;
        border: 1px solid #ccff00;
        border-radius: 6px;
        padding: 2px 10px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-right: 6px;
    }

    .badge-dusuk {
        display: inline-block;
        background: rgba(0,222,255,0.1);
        color: #00deff;
        border: 1px solid rgba(0,222,255,0.3);
        border-radius: 6px;
        padding: 2px 10px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-right: 6px;
    }

    /* ── SCROLLBAR ── */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #0d2237; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #00deff; }

    /* ── CAPTION / SMALL TEXT ── */
    .stCaption, small, [data-testid="stCaptionContainer"] {
        color: #5580a0 !important;
    }

    /* ── SIDEBAR STEP LIST ── */
    .step-item {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        padding: 10px 0;
        border-bottom: 1px solid rgba(0,222,255,0.06);
    }

    .step-num {
        background: #FFD700;
        color: #08192b;
        width: 22px;
        height: 22px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.72rem;
        font-weight: 800;
        flex-shrink: 0;
        margin-top: 1px;
    }

    .step-text {
        font-size: 0.85rem;
        color: #c0d8ee;
        line-height: 1.4;
    }

    .step-text strong {
        color: #ffffff;
        display: block;
        margin-bottom: 1px;
    }
    </style>
    """, unsafe_allow_html=True)


ORANGE = colors.HexColor("#ccff00")
DARK_BG = colors.HexColor("#111627")
DARK_TEXT = colors.HexColor("#1a1a2e")
GREY_TEXT = colors.HexColor("#555555")
RED_COLOR = colors.HexColor("#ef4444")
YELLOW_COLOR = colors.HexColor("#def50b")
GREEN_COLOR = colors.HexColor("#22c55e")


def build_pdf_report(catalog_summary, gap_report, final_report) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2 * cm,
        title="Tivibu Katalog Analiz Raporu",
        author="Tivibu Katalog Analiz Asistanı",
    )

    W = A4[0] - 4 * cm  # usable width

    styles = getSampleStyleSheet()

    def style(name, **kw):
        return ParagraphStyle(name, parent=styles["Normal"], **kw)

    s_cover_title = style("CoverTitle", fontSize=28, textColor=colors.white,
                          fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=6)
    s_cover_sub = style("CoverSub", fontSize=11, textColor=colors.HexColor("#cccccc"),
                        alignment=TA_CENTER, spaceAfter=4)
    s_section = style("Section", fontSize=14, textColor=ORANGE,
                      fontName="Helvetica-Bold", spaceBefore=18, spaceAfter=6)
    s_subsection = style("Subsection", fontSize=10, textColor=GREY_TEXT,
                         fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4,
                         textTransform="uppercase", letterSpacing=1)
    s_body = style("Body", fontSize=9.5, textColor=DARK_TEXT,
                   leading=15, spaceAfter=6)
    s_label = style("Label", fontSize=8, textColor=GREY_TEXT,
                    fontName="Helvetica-Bold", textTransform="uppercase",
                    letterSpacing=0.8, spaceAfter=2)
    s_rec = style("Rec", fontSize=9.5, textColor=DARK_TEXT, leading=15, leftIndent=14)
    s_bullet = style("Bullet", fontSize=9.5, textColor=DARK_TEXT,
                     leading=15, leftIndent=14, spaceAfter=3)

    story = []

    # ── COVER ────────────────────────────────────────────────────
    cover_data = [["Tivibu\nKatalog Analiz Raporu"]]
    cover_table = Table(cover_data, colWidths=[W])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0a0d1a")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 26),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 40),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 40),
        ("ROUNDEDCORNERS", (0, 0), (-1, -1), [10, 10, 10, 10]),
    ]))
    story.append(cover_table)
    story.append(Spacer(1, 0.4 * cm))

    # orange accent line
    story.append(HRFlowable(width=W, thickness=3, color=ORANGE, spaceAfter=0.6 * cm))

    sub_data = [["AI Destekli Katalog Analiz Asistanı tarafından hazırlanmıştır"]]
    sub_table = Table(sub_data, colWidths=[W])
    sub_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (-1, -1), GREY_TEXT),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    story.append(sub_table)
    story.append(Spacer(1, 1 * cm))

    # ── SECTION 1: CATALOG SUMMARY ───────────────────────────────
    story.append(Paragraph("1. Katalog Özeti", s_section))
    story.append(HRFlowable(width=W, thickness=0.5, color=colors.HexColor("#e0e0e0"), spaceAfter=8))

    # Metrics row
    total = getattr(catalog_summary, "total_movies", 0)
    avg_pop = getattr(catalog_summary, "avg_popularity", 0)
    avg_vote = getattr(catalog_summary, "avg_vote", 0)

    metrics = [
        ["Toplam Film", "Ort. Popülerlik", "Ort. Oy"],
        [f"{total:,}", f"{avg_pop:.1f}", f"{avg_vote:.2f} / 10"],
    ]
    mt = Table(metrics, colWidths=[W / 3] * 3)
    mt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0a0d1a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#aaaaaa")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 7),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#111627")),
        ("TEXTCOLOR", (0, 1), (-1, 1), colors.white),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 1), (-1, 1), 18),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#2d3555")),
        ("ROUNDEDCORNERS", (0, 0), (-1, -1), [6, 6, 6, 6]),
    ]))
    story.append(mt)
    story.append(Spacer(1, 0.5 * cm))

    # Genre table
    if hasattr(catalog_summary, "top_genres") and catalog_summary.top_genres:
        story.append(Paragraph("Tür Dağılımı", s_subsection))
        genre_rows = [["Tür", "Film Sayısı", "Oran (%)"]]
        for g in catalog_summary.top_genres[:12]:
            genre_rows.append([g.genre, str(g.count), f"{g.percentage:.1f}%"])
        gt = Table(genre_rows, colWidths=[W * 0.5, W * 0.25, W * 0.25])
        gt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), ORANGE),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f7f7")]),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e0e0e0")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(gt)
        story.append(Spacer(1, 0.4 * cm))

    # Analysis text
    analysis = getattr(catalog_summary, "analysis_text", "")
    if analysis:
        story.append(Paragraph("Analiz", s_subsection))
        story.append(Paragraph(analysis, s_body))

    story.append(Spacer(1, 0.6 * cm))

    # ── SECTION 2: GAP REPORT ────────────────────────────────────
    story.append(Paragraph("2. Eksiklik Analizi", s_section))
    story.append(HRFlowable(width=W, thickness=0.5, color=colors.HexColor("#e0e0e0"), spaceAfter=8))

    under = getattr(gap_report, "underrepresented_genres", [])
    over = getattr(gap_report, "overrepresented_genres", [])

    if under or over:
        rep_data = [
            ["Az Temsil Edilen Türler", "Fazla Temsil Edilen Türler"],
            [" · ".join(under) if under else "—", " · ".join(over) if over else "—"],
        ]
        rt = Table(rep_data, colWidths=[W / 2, W / 2])
        rt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#fef2f2")),
            ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#fffbeb")),
            ("TEXTCOLOR", (0, 0), (0, 0), RED_COLOR),
            ("TEXTCOLOR", (1, 0), (1, 0), YELLOW_COLOR),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 7.5),
            ("BACKGROUND", (0, 1), (0, 1), colors.HexColor("#fff5f5")),
            ("BACKGROUND", (1, 1), (1, 1), colors.HexColor("#fffdf0")),
            ("FONTSIZE", (0, 1), (-1, 1), 9),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#e0e0e0")),
        ]))
        story.append(rt)
        story.append(Spacer(1, 0.4 * cm))

    # Gap items
    if hasattr(gap_report, "gaps") and gap_report.gaps:
        story.append(Paragraph("Detaylı Eksiklikler", s_subsection))
        sev_color = {"Kritik": RED_COLOR, "Orta": YELLOW_COLOR, "Düşük": GREEN_COLOR}
        for gap in gap_report.gaps:
            sc = sev_color.get(gap.severity, GREY_TEXT)
            rows = [
                [Paragraph(f"<b>{gap.category}</b>", style("gc", fontSize=9.5, textColor=DARK_TEXT, fontName="Helvetica-Bold")),
                 Paragraph(gap.severity, style("gs", fontSize=8, textColor=sc, fontName="Helvetica-Bold", alignment=TA_RIGHT))],
                [Paragraph(f"<b>Sorun:</b> {gap.description}", s_body), ""],
                [Paragraph(f"<b>Öneri:</b> {gap.recommendation}", style("gr", fontSize=9.5, textColor=colors.HexColor("#444444"), leading=15)), ""],
            ]
            gt = Table(rows, colWidths=[W * 0.75, W * 0.25])
            gt.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
                ("LINEBELOW", (0, 0), (-1, 0), 0.3, colors.HexColor("#e0e0e0")),
                ("SPAN", (0, 1), (-1, 1)),
                ("SPAN", (0, 2), (-1, 2)),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            story.append(KeepTogether([gt, Spacer(1, 0.2 * cm)]))

    gap_analysis = getattr(gap_report, "analysis_text", "")
    if gap_analysis:
        story.append(Paragraph("Analiz", s_subsection))
        story.append(Paragraph(gap_analysis, s_body))

    story.append(Spacer(1, 0.6 * cm))

    # ── SECTION 3: FINAL REPORT ──────────────────────────────────
    story.append(Paragraph("3. Yönetici Raporu ve Öneriler", s_section))
    story.append(HRFlowable(width=W, thickness=0.5, color=colors.HexColor("#e0e0e0"), spaceAfter=8))

    exec_sum = getattr(final_report, "executive_summary", "")
    if exec_sum:
        exec_box = [[Paragraph(exec_sum, style("ex", fontSize=9.5, textColor=DARK_TEXT, leading=16))]]
        et = Table(exec_box, colWidths=[W])
        et.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff8f4")),
            ("LEFTPADDING", (0, 0), (-1, -1), 14),
            ("RIGHTPADDING", (0, 0), (-1, -1), 14),
            ("TOPPADDING", (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ("LINEBEFORE", (0, 0), (0, -1), 3, ORANGE),
            ("BOX", (0, 0), (-1, -1), 0.3, colors.HexColor("#e0e0e0")),
        ]))
        story.append(et)
        story.append(Spacer(1, 0.5 * cm))

    # Highlights & critical gaps side by side
    highlights = getattr(final_report, "catalog_highlights", [])
    critical = getattr(final_report, "critical_gaps", [])
    if highlights or critical:
        h_text = "\n".join(f"✓  {h}" for h in highlights) if highlights else "—"
        c_text = "\n".join(f"✕  {c}" for c in critical) if critical else "—"
        hc_data = [
            [Paragraph("Katalog Güçlü Yönleri", style("hl", fontSize=8, fontName="Helvetica-Bold", textColor=GREEN_COLOR)),
             Paragraph("Kritik Eksiklikler", style("cl", fontSize=8, fontName="Helvetica-Bold", textColor=RED_COLOR))],
            [Paragraph(h_text, style("hb", fontSize=9, textColor=DARK_TEXT, leading=14)),
             Paragraph(c_text, style("cb", fontSize=9, textColor=DARK_TEXT, leading=14))],
        ]
        hct = Table(hc_data, colWidths=[W / 2 - 0.2 * cm, W / 2 - 0.2 * cm], spaceBefore=4)
        hct.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#f0fdf4")),
            ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#fef2f2")),
            ("BACKGROUND", (0, 1), (0, 1), colors.white),
            ("BACKGROUND", (1, 1), (1, 1), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#e0e0e0")),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(hct)
        story.append(Spacer(1, 0.5 * cm))

    # Purchase recommendations
    recs = getattr(final_report, "purchase_recommendations", [])
    if recs:
        story.append(Paragraph("Satın Alma Önerileri", s_subsection))
        for i, rec in enumerate(recs, 1):
            row = [[
                Paragraph(str(i), style("rn", fontSize=10, fontName="Helvetica-Bold",
                                        textColor=colors.white, alignment=TA_CENTER)),
                Paragraph(rec, style("rt", fontSize=9.5, textColor=DARK_TEXT, leading=15)),
            ]]
            rt = Table(row, colWidths=[0.7 * cm, W - 0.7 * cm])
            rt.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (0, -1), ORANGE),
                ("BACKGROUND", (1, 0), (1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.3, colors.HexColor("#e0e0e0")),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (0, -1), 4),
                ("LEFTPADDING", (1, 0), (1, -1), 10),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            story.append(KeepTogether([rt, Spacer(1, 0.15 * cm)]))

    conclusion = getattr(final_report, "conclusion", "")
    if conclusion:
        story.append(Spacer(1, 0.4 * cm))
        story.append(Paragraph("Sonuç", s_subsection))
        story.append(Paragraph(conclusion, s_body))

    # ── FOOTER LINE ──────────────────────────────────────────────
    story.append(Spacer(1, 1 * cm))
    story.append(HRFlowable(width=W, thickness=2, color=ORANGE))
    story.append(Spacer(1, 0.2 * cm))
    footer_data = [["Tivibu Katalog Analiz Asistanı"]]
    ft = Table(footer_data, colWidths=[W])
    ft.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TEXTCOLOR", (0, 0), (-1, -1), GREY_TEXT),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    story.append(ft)

    doc.build(story)
    return buffer.getvalue()


def severity_badge(severity: str) -> str:
    cls = {"Kritik": "badge-kritik", "Orta": "badge-orta", "Düşük": "badge-dusuk"}.get(severity, "badge-dusuk")
    return f'<span class="{cls}">{severity}</span>'


apply_tivibu_theme()


# ── MAIN HEADER ──────────────────────────────────────────────────
st.markdown("""
<div class="tivibu-header">
    <div class="tivibu-logo-badge" style="background:#00deff;color:#000000;border-radius:8px;padding:6px 10px;font-size:1.7rem;font-weight:bold">t</div>
    <div class="tivibu-title-block">
        <h1>Tivibu <span>Katalog Analiz</span> Asistanı</h1>
    </div>
</div>
""", unsafe_allow_html=True)

# ── START BUTTON ──────────────────────────────────────────────────
col_btn, col_info = st.columns([1, 3], vertical_alignment="center")

with col_btn:
    start = st.button("Analizi Başlat", use_container_width=True)

with col_info:
    # Padding'e artık gerek yok, daha temiz bir HTML kullanabilirsiniz
    st.markdown("""
    <div style="color:#5580a0;font-size:0.84rem">
        Ortalama süre <strong style="color:#c0d8ee">30–60 saniye</strong>.
    </div>
    """, unsafe_allow_html=True)
# ── ANALYSIS ─────────────────────────────────────────────────────
if start:
    try:
        with st.status("  Analiz çalışıyor...", expanded=True) as status:
            
            catalog_summary, gap_report, final_report = analyze_catalog(None)
            status.update(label=" Analiz tamamlandı!", state="complete")

        st.success("Analiz başarıyla tamamlandı!")

        tab1, tab2, tab3, tab4 = st.tabs([
            "  Katalog Özeti",
            "  Eksiklik Analizi",
            "  Öneriler & Rapor",
            "  Dosya İndir (PDF)",
        ])

        # ── TAB 1: CATALOG SUMMARY ────────────────────────────────
        with tab1:
            st.subheader("Genel Bakış")

            c1, c2, c3 = st.columns(3)
            c1.metric("Toplam Film", f"{getattr(catalog_summary, 'total_movies', 0):,}")
            c2.metric("Ort. Popülerlik", f"{getattr(catalog_summary, 'avg_popularity', 0):.1f}")
            c3.metric("Ort. Oy", f"{getattr(catalog_summary, 'avg_vote', 0):.2f} / 10")

            st.markdown("#### Tür Dağılımı")
            if hasattr(catalog_summary, "top_genres") and catalog_summary.top_genres:
                genre_data = {g.genre: g.count for g in catalog_summary.top_genres}
                st.bar_chart(genre_data, color="#00deff")

            st.markdown("#### Analiz")
            st.markdown(
                f'<div style="background:#0d2237;border:1px solid rgba(0,222,255,0.1);border-radius:12px;padding:18px 20px;color:#c0d8ee;line-height:1.7">'
                f'{getattr(catalog_summary, "analysis_text", "—")}</div>',
                unsafe_allow_html=True,
            )

        # ── TAB 2: GAP REPORT ─────────────────────────────────────
        with tab2:
            st.subheader("Katalog Eksiklikleri")

            g1, g2 = st.columns(2)
            with g1:
                if hasattr(gap_report, "underrepresented_genres") and gap_report.underrepresented_genres:
                    genres_str = " · ".join(gap_report.underrepresented_genres)
                    st.markdown(f"""
                    <div style="background:rgba(239,68,68,0.07);border:1px solid rgba(239,68,68,0.25);border-radius:12px;padding:16px 18px">
                        <div style="font-size:0.72rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#f87171;margin-bottom:6px">⚠ Az Temsil Edilen Türler</div>
                        <div style="color:#ffffff;font-size:0.9rem">{genres_str}</div>
                    </div>
                    """, unsafe_allow_html=True)

            with g2:
                if hasattr(gap_report, "overrepresented_genres") and gap_report.overrepresented_genres:
                    genres_str = " · ".join(gap_report.overrepresented_genres)
                    st.markdown(f"""
                    <div style="background:#ccff00;border:1px solid #ccff00 ;border-radius:12px;padding:16px 18px">
                        <div style="font-size:0.72rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#FFD700;margin-bottom:6px">◉ Fazla Temsil Edilen Türler</div>
                        <div style="color:#ffffff;font-size:0.9rem">{genres_str}</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("#### Detaylı Eksiklikler")
            if hasattr(gap_report, "gaps") and gap_report.gaps:
                for gap in gap_report.gaps:
                    badge = severity_badge(gap.severity)
                    with st.expander(f"{gap.category}"):
                        st.markdown(
                            f'{badge}<br><br>'
                            f'<strong style="color:#c0d8ee">Sorun:</strong> {gap.description}<br><br>'
                            f'<strong style="color:#00deff">Öneri:</strong> {gap.recommendation}',
                            unsafe_allow_html=True,
                        )

            if getattr(gap_report, "analysis_text", ""):
                st.markdown("#### Analiz")
                st.markdown(
                    f'<div style="background:#0d2237;border:1px solid rgba(0,222,255,0.1);border-radius:12px;padding:18px 20px;color:#c0d8ee;line-height:1.7">'
                    f'{gap_report.analysis_text}</div>',
                    unsafe_allow_html=True,
                )

        # ── TAB 3: FINAL REPORT ───────────────────────────────────
        with tab3:
            st.subheader("Yönetici Raporu")

            exec_sum = getattr(final_report, "executive_summary", "")
            if exec_sum:
                st.markdown(f"""
                <div style="background:rgba(0,222,255,0.06);border-left:3px solid #00deff;border-radius:0 12px 12px 0;padding:16px 20px;margin-bottom:24px;color:#ffffff;line-height:1.7">
                    {exec_sum}
                </div>
                """, unsafe_allow_html=True)

            r1, r2 = st.columns(2)
            with r1:
                st.markdown("""
                <div style="font-size:0.78rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#c;margin-bottom:10px">
                ✓ Katalog Güçlü Yönleri</div>
                """, unsafe_allow_html=True)
                if hasattr(final_report, "catalog_highlights"):
                    for item in final_report.catalog_highlights:
                        st.markdown(f"""
                        <div style="display:flex;gap:8px;align-items:flex-start;padding:6px 0;border-bottom:1px solid rgba(0,222,255,0.07);color:#c0d8ee;font-size:0.88rem">
                            <span style="color:#00deff;margin-top:1px">✓</span>{item}
                        </div>
                        """, unsafe_allow_html=True)

            with r2:
                st.markdown("""
                <div style="font-size:0.78rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#f87171;margin-bottom:10px">
                ✕ Kritik Eksiklikler</div>
                """, unsafe_allow_html=True)
                if hasattr(final_report, "critical_gaps"):
                    for item in final_report.critical_gaps:
                        st.markdown(f"""
                        <div style="display:flex;gap:8px;align-items:flex-start;padding:6px 0;border-bottom:1px solid rgba(0,222,255,0.07);color:#c0d8ee;font-size:0.88rem">
                            <span style="color:#f87171;margin-top:1px">✕</span>{item}
                        </div>
                        """, unsafe_allow_html=True)

            st.markdown("#### Satın Alma Önerileri")
            if hasattr(final_report, "purchase_recommendations"):
                for i, rec in enumerate(final_report.purchase_recommendations, 1):
                    st.markdown(f"""
                    <div style="display:flex;gap:12px;align-items:flex-start;background:#0d2237;border:1px solid rgba(0,222,255,0.1);border-radius:10px;padding:14px 16px;margin-bottom:8px">
                        <div style="background:#FFD700;color:#08192b;width:26px;height:26px;border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:0.78rem;font-weight:800;flex-shrink:0">{i}</div>
                        <div style="color:#c0d8ee;font-size:0.9rem;line-height:1.55;padding-top:3px">{rec}</div>
                    </div>
                    """, unsafe_allow_html=True)

            if getattr(final_report, "conclusion", ""):
                st.markdown("#### Sonuç")
                st.markdown(
                    f'<div style="background:#0d2237;border:1px solid rgba(0,222,255,0.1);border-radius:12px;padding:18px 20px;color:#c0d8ee;line-height:1.7">'
                    f'{final_report.conclusion}</div>',
                    unsafe_allow_html=True,
                )

        # ── TAB 4: PDF REPORT ─────────────────────────────────────
        with tab4:
            st.subheader("PDF Raporu")
            st.markdown("""
            <div style="background:#ccff00;border:1px solid rgba(0,222,255,0.2);border-radius:12px;padding:16px 20px;margin-bottom:20px">
                <div style="font-size:0.78rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#00deff;margin-bottom:6px">📄 PDF Rapor</div>
                <div style="color:#c0d8ee;font-size:0.88rem;line-height:1.6">
                    Katalog özeti, eksiklik analizi ve satın alma önerilerini içeren tam raporu PDF olarak indirebilirsiniz.
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.spinner("PDF oluşturuluyor..."):
                pdf_bytes = build_pdf_report(catalog_summary, gap_report, final_report)

            st.download_button(
                label="⬇  PDF Olarak İndir",
                data=pdf_bytes,
                file_name="tivibu_katalog_analizi.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

            # Preview summary
            st.markdown("---")
            st.markdown("**Rapor İçeriği:**")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                <div style="background:#0d2237;border:1px solid rgba(0,222,255,0.1);border-radius:10px;padding:12px 16px">
                    <div style="color:#00deff;font-size:0.75rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px">İçindekiler</div>
                    <div style="color:#c0d8ee;font-size:0.85rem;line-height:2">
                        1. Katalog Özeti<br>
                        2. Eksiklik Analizi<br>
                        3. Yönetici Raporu & Öneriler
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                rec_count = len(getattr(final_report, "purchase_recommendations", []))
                gap_count = len(getattr(gap_report, "gaps", []))
                genre_count = len(getattr(catalog_summary, "top_genres", []))
                st.markdown(f"""
                <div style="background:#0d2237;border:1px solid rgba(0,222,255,0.1);border-radius:10px;padding:12px 16px">
                    <div style="color:#00deff;font-size:0.75rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px">Rapor Özeti</div>
                    <div style="color:#c0d8ee;font-size:0.85rem;line-height:2">
                         {getattr(catalog_summary, 'total_movies', 0):,} film analiz edildi<br>
                         {genre_count} tür kategorisi<br>
                         {gap_count} eksiklik tespit edildi<br>
                         {rec_count} satın alma önerisi
                    </div>
                </div>
                """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Hata oluştu: {e}")
        st.exception(e)
