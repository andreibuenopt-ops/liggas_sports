import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from core import engine, style

st.set_page_config(
    page_title="Basic IFC — Gerenciador de Campeonatos",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

style.inject(st)

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:.4rem 0 1.2rem">
        <div class="ifc-logo">⚽ Basic IFC</div>
        <div class="ifc-logo-sub">Gerenciador de Campeonatos</div>
    </div>
    """, unsafe_allow_html=True)

    cfg = engine.get_config()
    if cfg:
        fmt = cfg.get("formato","")
        fmt_cor = {"Liga":"#00e564","Pontos Corridos":"#00e564",
                   "Grupos":"#ffaa00","Chaves Cruzadas":"#ffaa00",
                   "Pontos Corridos + Mata-Mata":"#9060ff",
                   "Eliminatórias":"#ff5050"}.get(fmt,"#00e5ff")
        st.markdown(f"""
        <div style="background:#0d1a2d;border:1px solid #1e3a5f;border-radius:6px;
             padding:8px 12px;margin-bottom:10px">
            <div style="font-family:Rajdhani,sans-serif;font-weight:700;
                 font-size:.9rem;color:#e0e6f0">{cfg.get('nome','—')}</div>
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:.62rem;
                 letter-spacing:1.5px;color:{fmt_cor};text-transform:uppercase">
                {fmt}</div>
        </div>""", unsafe_allow_html=True)

    pagina = st.radio("nav", [
        "🏠  Dashboard",
        "⚙️  Configurar",
        "⚽  Jogos",
        "📊  Classificação",
        "⚔️  Mata-Mata",
        "📈  Estatísticas",
        "🎲  Sorteio ao Vivo",
        "📄  Relatórios",
    ], label_visibility="collapsed")

    st.markdown("<hr style='border-color:#1a2535;margin:10px 0'>", unsafe_allow_html=True)
    st.markdown('<div class="ifc-logo-sub" style="padding-left:2px">v1.0 · Basic IFC 2013 → Python</div>',
                unsafe_allow_html=True)

# ── Roteamento ────────────────────────────────────────────────
p = pagina.strip().split("  ")[-1]

if p == "Dashboard":
    from pages import dashboard; dashboard.render()
elif p == "Configurar":
    from pages import configurar; configurar.render()
elif p == "Jogos":
    from pages import jogos; jogos.render()
elif p == "Classificação":
    from pages import classificacao; classificacao.render()
elif p == "Mata-Mata":
    from pages import matamata; matamata.render()
elif p == "Estatísticas":
    from pages import estatisticas; estatisticas.render()
elif p == "Sorteio ao Vivo":
    from pages import sorteio; sorteio.render()
elif p == "Relatórios":
    from pages import relatorios; relatorios.render()
