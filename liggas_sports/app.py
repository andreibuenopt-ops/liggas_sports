import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from utils.database import init_db, listar_campeonatos, deletar_campeonato, atualizar_status_campeonato

st.set_page_config(
    page_title="TorneioX — Gerenciador de Campeonatos",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()

# ── DARK ESPORTS CSS ──────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Barlow+Condensed:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap');

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background: #090b10 !important;
    color: #e0e6f0 !important;
}
[data-testid="stSidebar"] {
    background: #0d1117 !important;
    border-right: 1px solid #1e2a3a !important;
}
[data-testid="stSidebarContent"] { padding-top: 1rem; }

/* ── Remove streamlit default padding ── */
.block-container { padding-top: 1.5rem !important; }

/* ── Inputs & selects ── */
input, textarea, [data-baseweb="select"] > div {
    background: #111827 !important;
    border: 1px solid #1e3a5f !important;
    color: #e0e6f0 !important;
    border-radius: 6px !important;
}
input:focus, textarea:focus { border-color: #00e5ff !important; box-shadow: 0 0 0 2px rgba(0,229,255,0.15) !important; }
[data-baseweb="select"] * { color: #e0e6f0 !important; background: #111827 !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #0066ff, #00e5ff) !important;
    color: #000 !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(0,229,255,0.35) !important;
    filter: brightness(1.1) !important;
}
.stButton > button[kind="secondary"] {
    background: #1a2235 !important;
    color: #e0e6f0 !important;
    border: 1px solid #2a3a50 !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tablist"] {
    background: #0d1117 !important;
    border-bottom: 1px solid #1e2a3a !important;
    gap: 4px;
}
[data-testid="stTabs"] button[role="tab"] {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    color: #607080 !important;
    border-bottom: 2px solid transparent !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.2s !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #00e5ff !important;
    border-bottom: 2px solid #00e5ff !important;
    background: transparent !important;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
    background: #0d1a2d !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 8px !important;
    padding: 1rem !important;
}
[data-testid="metric-container"] label { color: #607080 !important; font-family: 'Barlow Condensed', sans-serif !important; letter-spacing: 1px !important; text-transform: uppercase !important; font-size: 0.75rem !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #00e5ff !important; font-family: 'Barlow Condensed', sans-serif !important; font-size: 2rem !important; font-weight: 800 !important; }

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #0d1117 !important;
    border: 1px solid #1e2a3a !important;
    border-radius: 6px !important;
}
[data-testid="stExpander"] summary { color: #c0d0e0 !important; font-family: 'Barlow Condensed', sans-serif !important; font-size: 0.9rem !important; letter-spacing: 0.5px !important; }

/* ── Selectbox label ── */
[data-testid="stSelectbox"] label, [data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label, [data-testid="stTextArea"] label,
[data-testid="stCheckbox"] label, [data-testid="stRadio"] label,
[data-testid="stDateInput"] label {
    color: #607080 !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 0.78rem !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border: 1px solid #1e2a3a !important; border-radius: 6px !important; }
.dvn-scroller { background: #090b10 !important; }

/* ── Divider ── */
hr { border-color: #1e2a3a !important; }

/* ── Info / warning / success ── */
[data-testid="stAlert"] { border-radius: 6px !important; border-left-width: 4px !important; }

/* ── Form ── */
[data-testid="stForm"] { background: #0d1117 !important; border: 1px solid #1e2a3a !important; border-radius: 8px !important; padding: 1rem !important; }

/* ── Sidebar radio ── */
[data-testid="stRadio"] > div { gap: 4px !important; }
[data-testid="stRadio"] label { color: #a0b0c0 !important; font-family: 'Barlow Condensed', sans-serif !important; font-size: 0.9rem !important; letter-spacing: 1px !important; padding: 6px 10px !important; border-radius: 4px !important; transition: all 0.15s !important; }
[data-testid="stRadio"] label:hover { background: #1a2235 !important; color: #00e5ff !important; }

/* ── Custom classes ── */
.xt-logo {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.8rem; font-weight: 800;
    letter-spacing: 3px; text-transform: uppercase;
    background: linear-gradient(90deg, #0066ff, #00e5ff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    line-height: 1;
}
.xt-logo-sub {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.65rem; letter-spacing: 4px;
    color: #405060; text-transform: uppercase; margin-top: 2px;
}
.xt-page-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 2.4rem; font-weight: 800;
    letter-spacing: 2px; text-transform: uppercase;
    color: #ffffff; line-height: 1;
}
.xt-page-sub {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem; color: #506070; letter-spacing: 1px;
    margin-bottom: 1.5rem;
}
.xt-card {
    background: linear-gradient(135deg, #0d1a2d 0%, #0d1117 100%);
    border: 1px solid #1e3a5f;
    border-left: 3px solid #00e5ff;
    border-radius: 6px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.75rem;
    transition: all 0.2s;
}
.xt-card:hover { border-left-color: #0066ff; box-shadow: 0 4px 20px rgba(0,102,255,0.15); }
.xt-card-name {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.1rem; font-weight: 700;
    letter-spacing: 1px; text-transform: uppercase;
    color: #ffffff;
}
.xt-card-meta {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.82rem; color: #506070;
    margin-top: 3px;
}
.xt-badge {
    display: inline-block; padding: 2px 10px;
    border-radius: 2px; font-size: 0.68rem;
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 700; letter-spacing: 1.5px;
    text-transform: uppercase; margin-right: 5px;
}
.xt-badge-copa    { background: rgba(255,170,0,0.15);  color: #ffaa00; border: 1px solid #ffaa0040; }
.xt-badge-liga    { background: rgba(0,229,100,0.12);  color: #00e564; border: 1px solid #00e56440; }
.xt-badge-generico{ background: rgba(120,80,255,0.12); color: #9060ff; border: 1px solid #9060ff40; }
.xt-badge-interclasses { background: rgba(0,150,255,0.12); color: #0096ff; border: 1px solid #0096ff40; }
.xt-badge-ativo   { background: rgba(0,229,255,0.1);   color: #00e5ff; border: 1px solid #00e5ff30; }
.xt-badge-encerrado{ background: rgba(255,50,50,0.1);  color: #ff5050; border: 1px solid #ff505030; }
.xt-divider {
    border: none; height: 1px;
    background: linear-gradient(90deg, #1e3a5f, transparent);
    margin: 1.5rem 0;
}
.xt-section-label {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.7rem; font-weight: 700;
    letter-spacing: 3px; text-transform: uppercase;
    color: #305070; margin-bottom: 0.75rem;
}
.xt-bracket-card {
    background: #0d1a2d;
    border: 1px solid #1e3a5f;
    border-radius: 4px;
    padding: 8px 12px;
    margin-bottom: 6px;
    border-left: 2px solid #1e3a5f;
    transition: all 0.2s;
}
.xt-bracket-card:hover { border-left-color: #00e5ff; }
.xt-match-team { font-family: 'Rajdhani', sans-serif; font-size: 0.85rem; font-weight: 600; }
.xt-match-score { font-family: 'Barlow Condensed', sans-serif; font-size: 0.75rem; color: #405060; text-align: center; padding: 2px 0; }
.xt-player-row {
    display: flex; align-items: center; gap: 10px;
    padding: 6px 0; border-bottom: 1px solid #111827;
}
.xt-player-num {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.75rem; font-weight: 700;
    color: #0066ff; min-width: 20px;
}
.xt-player-name {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.9rem; color: #c0d0e0;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 0.5rem 0 1.5rem">
        <div class="xt-logo">⚡ TorneioX</div>
        <div class="xt-logo-sub">Gerenciador de Campeonatos</div>
    </div>
    """, unsafe_allow_html=True)

    pagina = st.radio(
        "nav",
        ["🏠  Início", "➕  Novo Campeonato", "📋  Gerenciar"],
        label_visibility="collapsed"
    )
    st.markdown("<hr class='xt-divider'>", unsafe_allow_html=True)
    st.markdown('<div class="xt-logo-sub" style="padding-left:2px">v2.0 · SQLite · Streamlit</div>', unsafe_allow_html=True)

# ── Início ────────────────────────────────────────────────────
if pagina == "🏠  Início":
    st.markdown('<div class="xt-page-title">⚡ Painel</div>', unsafe_allow_html=True)
    st.markdown('<div class="xt-page-sub">Gerencie seus campeonatos em um só lugar</div>', unsafe_allow_html=True)

    campeonatos = listar_campeonatos()
    ativos = [c for c in campeonatos if c["status"] == "ativo"]
    encerrados = [c for c in campeonatos if c["status"] == "encerrado"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total", len(campeonatos))
    col2.metric("Em Andamento", len(ativos))
    col3.metric("Encerrados", len(encerrados))

    st.markdown("<hr class='xt-divider'>", unsafe_allow_html=True)

    if not campeonatos:
        st.info("Nenhum campeonato criado ainda. Use **➕ Novo Campeonato** para começar!")
    else:
        st.markdown('<div class="xt-section-label">Campeonatos Recentes</div>', unsafe_allow_html=True)
        for camp in campeonatos[:8]:
            fmt = camp["formato"].lower()
            mod = camp["modalidade"].lower().split()[0]
            st.markdown(f"""
            <div class="xt-card">
                <div class="xt-card-name">{camp['nome']}</div>
                <div class="xt-card-meta">
                    <span class="xt-badge xt-badge-{fmt}">{camp['formato']}</span>
                    <span class="xt-badge xt-badge-{mod}">{camp['modalidade']}</span>
                    <span class="xt-badge xt-badge-{camp['status']}">{camp['status'].upper()}</span>
                    <span style="margin-left:6px;font-size:0.75rem;color:#304050">
                        {camp['criado_em'][:10]}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

elif pagina == "➕  Novo Campeonato":
    from pages.novo_campeonato import render
    render()

elif pagina == "📋  Gerenciar":
    campeonatos = listar_campeonatos()
    if not campeonatos:
        st.warning("Nenhum campeonato encontrado. Crie um primeiro!")
    else:
        st.markdown('<div class="xt-page-title">📋 Gerenciar</div>', unsafe_allow_html=True)

        opcoes = {f"{c['nome']}  [{c['formato']}]": c["id"] for c in campeonatos}
        escolha = st.selectbox("Campeonato", list(opcoes.keys()))
        camp_id = opcoes[escolha]
        camp = next(c for c in campeonatos if c["id"] == camp_id)

        aba_map = {
            "Copa": ["⚙️ Times", "👥 Jogadores", "🎯 Bracket", "📊 Resultados", "📤 Exportar"],
            "Liga": ["⚙️ Times", "👥 Jogadores", "📅 Rodadas", "🏆 Classificação", "📊 Resultados", "📤 Exportar"],
        }
        abas_lista = aba_map.get(camp["formato"], aba_map["Liga"])
        if camp["modalidade"] == "Interclasses":
            abas_lista = ["⚙️ Times", "👥 Jogadores", "📅 Rodadas", "🏆 Classificação", "🥇 Geral", "📊 Resultados", "📤 Exportar"]

        abas = st.tabs(abas_lista)

        from pages import times_page, copa_page, liga_page, resultados_page, exportar_page, jogadores_page

        if camp["formato"] == "Copa":
            with abas[0]: times_page.render(camp_id)
            with abas[1]: jogadores_page.render(camp_id)
            with abas[2]: copa_page.render(camp_id)
            with abas[3]: resultados_page.render(camp_id)
            with abas[4]: exportar_page.render(camp_id)
        else:
            with abas[0]: times_page.render(camp_id)
            with abas[1]: jogadores_page.render(camp_id)
            with abas[2]: liga_page.render_rodadas(camp_id)
            with abas[3]: liga_page.render_classificacao(camp_id)
            if camp["modalidade"] == "Interclasses":
                with abas[4]: st.info("Pontuação geral de interclasses em breve.")
                with abas[5]: resultados_page.render(camp_id)
                with abas[6]: exportar_page.render(camp_id)
            else:
                with abas[4]: resultados_page.render(camp_id)
                with abas[5]: exportar_page.render(camp_id)

        st.markdown("<hr class='xt-divider'>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if camp["status"] == "ativo":
                if st.button("✅ Encerrar Campeonato", use_container_width=True):
                    atualizar_status_campeonato(camp_id, "encerrado")
                    st.rerun()
            else:
                if st.button("🔄 Reativar", use_container_width=True):
                    atualizar_status_campeonato(camp_id, "ativo")
                    st.rerun()
        with col2:
            if st.button("🗑️ Deletar Campeonato", use_container_width=True, type="secondary"):
                if st.session_state.get("confirmar_delete") == camp_id:
                    deletar_campeonato(camp_id)
                    st.rerun()
                else:
                    st.session_state["confirmar_delete"] = camp_id
                    st.warning("Clique novamente para confirmar.")
