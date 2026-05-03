import streamlit as st
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from src.orchestrator import analyze_catalog
from src.config import Config

st.set_page_config(
    page_title="Tivibu Katalog Analiz Asistanı",
    page_icon="🎬",
    layout="wide",
)

st.title("🎬 Tivibu Katalog Analiz Asistanı")
st.caption("Multi-agent sistem ile katalog boşluk analizi ve satın alma önerileri")

with st.sidebar:
    st.header("⚙️ Ayarlar")
    st.info(f"LLM: **{Config.LLM_PROVIDER.upper()}**")

    st.markdown("---")
    st.header("📂 Katalog Seçimi")
    use_default = st.radio(
        "Veri kaynağı:",
        ["Varsayılan katalog (TMDB 5000)", "CSV dosyası yükle"],
    )

    uploaded_file = None
    if use_default == "CSV dosyası yükle":
        uploaded_file = st.file_uploader("CSV dosyası seç", type=["csv"])

    st.markdown("---")
    st.markdown("**Nasıl çalışır?**")
    st.markdown("""
1. 🔍 **Katalog Agent** → İstatistik toplar
2. 📊 **Gap Agent** → Boşlukları tespit eder
3. 📝 **Rapor Agent** → Yönetici raporu üretir
""")

if st.button("🚀 Analizi Başlat", type="primary", use_container_width=True):
    csv_path = None

    if uploaded_file is not None:
        tmp_path = os.path.join(os.path.dirname(__file__), "data", "uploaded_catalog.csv")
        with open(tmp_path, "wb") as f:
            f.write(uploaded_file.read())
        csv_path = tmp_path

    try:
        with st.status("Analiz çalışıyor...", expanded=True) as status:
            st.write("🔍 Katalog Agent başlatılıyor...")
            catalog_summary, gap_report, final_report = analyze_catalog(csv_path)
            status.update(label="Analiz tamamlandı!", state="complete")

        st.success("✅ Analiz başarıyla tamamlandı!")

        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Katalog Özeti",
            "🔍 Boşluk Analizi",
            "💡 Öneriler & Rapor",
            "📄 Ham Veri (JSON)",
        ])

        with tab1:
            st.subheader("Katalog Genel Görünümü")
            col1, col2, col3 = st.columns(3)
            col1.metric("Toplam Film", catalog_summary.total_movies)
            col2.metric("Ort. Popülerlik", catalog_summary.avg_popularity)
            col3.metric("Ort. Oy", catalog_summary.avg_vote)

            st.markdown("#### Tür Dağılımı")
            genre_data = {g.genre: g.count for g in catalog_summary.top_genres}
            st.bar_chart(genre_data)

            st.markdown("#### Analiz")
            st.write(catalog_summary.analysis_text)

        with tab2:
            st.subheader("Katalog Boşlukları")

            if gap_report.underrepresented_genres:
                st.error(f"**Az temsil edilen türler:** {', '.join(gap_report.underrepresented_genres)}")
            if gap_report.overrepresented_genres:
                st.warning(f"**Fazla temsil edilen türler:** {', '.join(gap_report.overrepresented_genres)}")

            st.markdown("#### Detaylı Boşluklar")
            for gap in gap_report.gaps:
                color = "🔴" if gap.severity == "Kritik" else "🟡" if gap.severity == "Orta" else "🟢"
                with st.expander(f"{color} [{gap.severity}] {gap.category}"):
                    st.write(f"**Sorun:** {gap.description}")
                    st.write(f"**Öneri:** {gap.recommendation}")

            st.markdown("#### Boşluk Analizi")
            st.write(gap_report.analysis_text)

        with tab3:
            st.subheader("Yönetici Raporu")
            st.info(final_report.executive_summary)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### ✅ Katalog Güçlü Yönleri")
                for item in final_report.catalog_highlights:
                    st.markdown(f"- {item}")

            with col2:
                st.markdown("#### ⚠️ Kritik Boşluklar")
                for item in final_report.critical_gaps:
                    st.markdown(f"- {item}")

            st.markdown("#### 🛒 Satın Alma Önerileri")
            for i, rec in enumerate(final_report.purchase_recommendations, 1):
                st.markdown(f"**{i}.** {rec}")

            st.markdown("#### Sonuç")
            st.write(final_report.conclusion)

        with tab4:
            st.subheader("Ham JSON Çıktısı")
            full_data = {
                "catalog_summary": catalog_summary.model_dump(),
                "gap_report": gap_report.model_dump(),
                "final_report": final_report.model_dump(),
            }
            st.download_button(
                "📥 JSON Olarak İndir",
                data=json.dumps(full_data, ensure_ascii=False, indent=2),
                file_name="tivibu_katalog_analizi.json",
                mime="application/json",
            )
            st.json(full_data)

    except Exception as e:
        st.error(f"Hata oluştu: {e}")
        st.exception(e)
