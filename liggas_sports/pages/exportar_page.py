import streamlit as st
from utils.database import get_campeonato
from utils.exportar import exportar_excel, exportar_pdf

def render(campeonato_id):
    camp = get_campeonato(campeonato_id)
    st.markdown('<div class="xt-page-title">📤 Exportar</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="xt-page-sub">{camp["nome"]}</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div style="background:#0d1a2d;border:1px solid #1e3a5f;border-radius:8px;
             padding:24px;text-align:center;margin-bottom:12px">
            <div style="font-size:2.5rem">📊</div>
            <div style="font-family:Barlow Condensed,sans-serif;font-size:1.1rem;
                 font-weight:800;letter-spacing:2px;text-transform:uppercase;
                 color:#e0e6f0;margin:10px 0 6px">Excel</div>
            <div style="font-family:Rajdhani,sans-serif;font-size:0.85rem;color:#405060">
                Classificação · Jogos · Artilheiros
            </div>
        </div>
        """, unsafe_allow_html=True)
        try:
            buf = exportar_excel(campeonato_id)
            st.download_button("⬇️ BAIXAR EXCEL", data=buf,
                file_name=f"{camp['nome'].replace(' ','_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True, type="primary")
        except Exception as e:
            st.error(f"Erro: {e}")

    with col2:
        st.markdown("""
        <div style="background:#0d1a2d;border:1px solid #1e3a5f;border-radius:8px;
             padding:24px;text-align:center;margin-bottom:12px">
            <div style="font-size:2.5rem">📄</div>
            <div style="font-family:Barlow Condensed,sans-serif;font-size:1.1rem;
                 font-weight:800;letter-spacing:2px;text-transform:uppercase;
                 color:#e0e6f0;margin:10px 0 6px">PDF</div>
            <div style="font-family:Rajdhani,sans-serif;font-size:0.85rem;color:#405060">
                Relatório pronto para impressão
            </div>
        </div>
        """, unsafe_allow_html=True)
        try:
            buf = exportar_pdf(campeonato_id)
            st.download_button("⬇️ BAIXAR PDF", data=buf,
                file_name=f"{camp['nome'].replace(' ','_')}.pdf",
                mime="application/pdf",
                use_container_width=True, type="primary")
        except Exception as e:
            st.error(f"Erro: {e}")
