import streamlit as st
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))

from utils.database import init_db, listar_campeonatos, deletar_campeonato, atualizar_status_campeonato

st.set_page_config(
    page_title="LiggasSports — Gerenciador de Campeonatos",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Barlow+Condensed:wght@400;600;700;800&display=swap');
html,body,[data-testid="stAppViewContainer"]{background:#090b10!important;color:#e0e6f0!important}
[data-testid="stSidebar"]{background:#0d1117!important;border-right:1px solid #1e2a3a!important}
.block-container{padding-top:1.5rem!important}
input,textarea,[data-baseweb="select"]>div{background:#111827!important;border:1px solid #1e3a5f!important;color:#e0e6f0!important;border-radius:6px!important}
input:focus,textarea:focus{border-color:#00e5ff!important;box-shadow:0 0 0 2px rgba(0,229,255,.15)!important}
[data-baseweb="select"] *{color:#e0e6f0!important;background:#111827!important}
.stButton>button{background:linear-gradient(135deg,#0066ff,#00e5ff)!important;color:#000!important;font-family:'Barlow Condensed',sans-serif!important;font-weight:700!important;font-size:.95rem!important;letter-spacing:1px!important;text-transform:uppercase!important;border:none!important;border-radius:4px!important;transition:all .2s!important}
.stButton>button:hover{transform:translateY(-1px)!important;box-shadow:0 4px 20px rgba(0,229,255,.35)!important}
.stButton>button[kind="secondary"]{background:#1a2235!important;color:#e0e6f0!important;border:1px solid #2a3a50!important}
[data-testid="stTabs"] [role="tablist"]{background:#0d1117!important;border-bottom:1px solid #1e2a3a!important}
[data-testid="stTabs"] button[role="tab"]{font-family:'Barlow Condensed',sans-serif!important;font-weight:700!important;font-size:.82rem!important;letter-spacing:1px!important;text-transform:uppercase!important;color:#607080!important;border-bottom:2px solid transparent!important}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"]{color:#00e5ff!important;border-bottom:2px solid #00e5ff!important;background:transparent!important}
[data-testid="metric-container"]{background:#0d1a2d!important;border:1px solid #1e3a5f!important;border-radius:8px!important;padding:1rem!important}
[data-testid="metric-container"] label{color:#607080!important;font-family:'Barlow Condensed',sans-serif!important;letter-spacing:1px!important;text-transform:uppercase!important;font-size:.75rem!important}
[data-testid="metric-container"] [data-testid="stMetricValue"]{color:#00e5ff!important;font-family:'Barlow Condensed',sans-serif!important;font-size:2rem!important;font-weight:800!important}
[data-testid="stExpander"]{background:#0d1117!important;border:1px solid #1e2a3a!important;border-radius:6px!important}
[data-testid="stExpander"] summary{color:#c0d0e0!important;font-family:'Barlow Condensed',sans-serif!important}
[data-testid="stSelectbox"] label,[data-testid="stTextInput"] label,[data-testid="stNumberInput"] label,[data-testid="stTextArea"] label,[data-testid="stCheckbox"] label,[data-testid="stRadio"] label,[data-testid="stDateInput"] label{color:#607080!important;font-family:'Barlow Condensed',sans-serif!important;font-size:.75rem!important;letter-spacing:1.5px!important;text-transform:uppercase!important}
[data-testid="stForm"]{background:#0d1117!important;border:1px solid #1e2a3a!important;border-radius:8px!important;padding:1rem!important}
[data-testid="stAlert"]{border-radius:6px!important;border-left-width:4px!important}
hr{border-color:#1e2a3a!important}
.xt-logo{font-family:'Barlow Condensed',sans-serif;font-size:1.7rem;font-weight:800;letter-spacing:3px;text-transform:uppercase;background:linear-gradient(90deg,#0066ff,#00e5ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1}
.xt-logo-sub{font-family:Rajdhani,sans-serif;font-size:.62rem;letter-spacing:4px;color:#405060;text-transform:uppercase;margin-top:2px}
.xt-page-title{font-family:'Barlow Condensed',sans-serif;font-size:2.2rem;font-weight:800;letter-spacing:2px;text-transform:uppercase;color:#fff;line-height:1}
.xt-page-sub{font-family:Rajdhani,sans-serif;font-size:1rem;color:#506070;letter-spacing:1px;margin-bottom:1.2rem}
.xt-card{background:linear-gradient(135deg,#0d1a2d,#0d1117);border:1px solid #1e3a5f;border-left:3px solid #00e5ff;border-radius:6px;padding:1rem 1.2rem;margin-bottom:.75rem;transition:all .2s}
.xt-card:hover{border-left-color:#0066ff;box-shadow:0 4px 20px rgba(0,102,255,.15)}
.xt-card-name{font-family:'Barlow Condensed',sans-serif;font-size:1.05rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#fff}
.xt-card-meta{font-family:Rajdhani,sans-serif;font-size:.82rem;color:#506070;margin-top:3px}
.xt-badge{display:inline-block;padding:2px 10px;border-radius:2px;font-size:.68rem;font-family:'Barlow Condensed',sans-serif;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin-right:5px}
.xt-badge-liga{background:rgba(0,229,100,.12);color:#00e564;border:1px solid #00e56440}
.xt-badge-mata-mata{background:rgba(255,50,50,.1);color:#ff5050;border:1px solid #ff505030}
.xt-badge-copa.xt-badge-do.xt-badge-mundo,.xt-badge-copa{background:rgba(255,170,0,.15);color:#ffaa00;border:1px solid #ffaa0040}
.xt-badge-ativo{background:rgba(0,229,255,.1);color:#00e5ff;border:1px solid #00e5ff30}
.xt-badge-encerrado{background:rgba(255,50,50,.1);color:#ff5050;border:1px solid #ff505030}
.xt-divider{border:none;height:1px;background:linear-gradient(90deg,#1e3a5f,transparent);margin:1.2rem 0}
.xt-section-label{font-family:'Barlow Condensed',sans-serif;font-size:.68rem;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#305070;margin-bottom:.6rem}
.xt-bracket-card{background:#0d1a2d;border:1px solid #1e3a5f;border-radius:4px;padding:8px 12px;margin-bottom:6px;border-left:2px solid #1e3a5f}
.xt-match-team{font-family:Rajdhani,sans-serif;font-size:.85rem;font-weight:600}
.xt-match-score{font-family:'Barlow Condensed',sans-serif;font-size:.7rem;color:#405060;text-align:center;padding:2px 0}
.xt-player-row{display:flex;align-items:center;gap:10px;padding:5px 0;border-bottom:1px solid #111827}
.xt-player-num{font-family:'Barlow Condensed',sans-serif;font-size:.75rem;font-weight:700;min-width:20px}
.xt-player-name{font-family:Rajdhani,sans-serif;font-size:.9rem;color:#c0d0e0}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="padding:.5rem 0 1.5rem"><div class="xt-logo">⚡ LiggasSports</div><div class="xt-logo-sub">Gerenciador de Campeonatos</div></div>', unsafe_allow_html=True)
    pagina = st.radio("nav", ["🏠  Início", "➕  Novo Campeonato", "📋  Gerenciar"],
                      label_visibility="collapsed")
    st.markdown("<hr class='xt-divider'>", unsafe_allow_html=True)
    st.markdown('<div class="xt-logo-sub" style="padding-left:2px">v2.1 · SQLite · Streamlit</div>', unsafe_allow_html=True)

# ── Início ────────────────────────────────────────────────────
if pagina == "🏠  Início":
    st.markdown('<div class="xt-page-title">⚡ Painel</div>', unsafe_allow_html=True)
    st.markdown('<div class="xt-page-sub">Gerencie seus campeonatos em um só lugar</div>', unsafe_allow_html=True)

    campeonatos = listar_campeonatos()
    ativos    = [c for c in campeonatos if c["status"] == "ativo"]
    encerrados = [c for c in campeonatos if c["status"] == "encerrado"]

    c1,c2,c3 = st.columns(3)
    c1.metric("Total", len(campeonatos))
    c2.metric("Em Andamento", len(ativos))
    c3.metric("Encerrados", len(encerrados))

    st.markdown("<hr class='xt-divider'>", unsafe_allow_html=True)
    if not campeonatos:
        st.info("Nenhum campeonato criado ainda. Use **➕ Novo Campeonato** para começar!")
    else:
        st.markdown('<div class="xt-section-label">Campeonatos Recentes</div>', unsafe_allow_html=True)
        for camp in campeonatos[:8]:
            fmt  = camp["formato"].lower().replace(" ","_")
            cfg  = json.loads(camp.get("config") or "{}")
            game_tag = f'<span class="xt-badge" style="background:rgba(120,80,255,.12);color:#9060ff;border:1px solid #9060ff40">{cfg["game"]}</span>' if cfg.get("game") else ""
            st.markdown(f"""
            <div class="xt-card">
                <div class="xt-card-name">{camp['nome']}</div>
                <div class="xt-card-meta">
                    <span class="xt-badge xt-badge-{fmt}">{camp['formato']}</span>
                    <span class="xt-badge xt-badge-{camp['status']}">{camp['status'].upper()}</span>
                    {game_tag}
                    <span style="margin-left:6px;font-size:.72rem;color:#304050">{camp['criado_em'][:10]}</span>
                </div>
            </div>""", unsafe_allow_html=True)

elif pagina == "➕  Novo Campeonato":
    from pages.novo_campeonato import render
    render()

elif pagina == "📋  Gerenciar":
    campeonatos = listar_campeonatos()
    if not campeonatos:
        st.warning("Nenhum campeonato encontrado.")
    else:
        st.markdown('<div class="xt-page-title">📋 Gerenciar</div>', unsafe_allow_html=True)
        opcoes = {f"{c['nome']}  [{c['formato']}]": c["id"] for c in campeonatos}
        escolha = st.selectbox("Campeonato", list(opcoes.keys()))
        camp_id = opcoes[escolha]
        camp = next(c for c in campeonatos if c["id"] == camp_id)
        fmt = camp["formato"]
        config = json.loads(camp.get("config") or "{}")

        from pages import times_page, resultados_page, exportar_page, jogadores_page
        from pages import grupos_page, matamata_page, liga_page

        # Monta abas por formato
        if fmt == "Liga":
            abas = st.tabs(["⚙️ Times", "👥 Jogadores", "📅 Rodadas", "🏆 Classificação", "📊 Resultados", "📤 Exportar"])
            with abas[0]: times_page.render(camp_id)
            with abas[1]: jogadores_page.render(camp_id)
            with abas[2]: liga_page.render_rodadas(camp_id)
            with abas[3]: liga_page.render_classificacao(camp_id)
            with abas[4]: resultados_page.render(camp_id)
            with abas[5]: exportar_page.render(camp_id)

        elif fmt == "Mata-Mata":
            abas = st.tabs(["⚙️ Times", "👥 Jogadores", "⚔️ Bracket", "📊 Resultados", "📤 Exportar"])
            with abas[0]: times_page.render(camp_id)
            with abas[1]: jogadores_page.render(camp_id)
            with abas[2]: matamata_page.render(camp_id)
            with abas[3]: resultados_page.render(camp_id)
            with abas[4]: exportar_page.render(camp_id)

        elif fmt == "Copa do Mundo":
            abas = st.tabs(["⚙️ Times", "👥 Jogadores", "🌍 Grupos", "⚔️ Mata-Mata", "📊 Resultados", "📤 Exportar"])
            with abas[0]: times_page.render(camp_id)
            with abas[1]: jogadores_page.render(camp_id)
            with abas[2]: grupos_page.render(camp_id)
            with abas[3]: matamata_page.render(camp_id)
            with abas[4]: resultados_page.render(camp_id)
            with abas[5]: exportar_page.render(camp_id)

        st.markdown("<hr class='xt-divider'>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            label = "✅ Encerrar" if camp["status"] == "ativo" else "🔄 Reativar"
            novo_status = "encerrado" if camp["status"] == "ativo" else "ativo"
            if st.button(label, use_container_width=True):
                atualizar_status_campeonato(camp_id, novo_status)
                st.rerun()
        with col2:
            if st.button("🗑️ Deletar Campeonato", use_container_width=True, type="secondary"):
                if st.session_state.get("confirmar_delete") == camp_id:
                    deletar_campeonato(camp_id)
                    st.rerun()
                else:
                    st.session_state["confirmar_delete"] = camp_id
                    st.warning("Clique novamente para confirmar.")
