import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from database.database import init_db, autenticar
from utils.style import inject_css

st.set_page_config(
    page_title="LiggasSports — Gerenciador de Campeonatos",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()
inject_css()

# ── LOGIN ─────────────────────────────────────────────────────
if "usuario" not in st.session_state:
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;
         justify-content:center;padding:4rem 0 2rem">
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:3rem;
             font-weight:800;letter-spacing:6px;text-transform:uppercase;
             background:linear-gradient(90deg,#0066ff,#00e5ff);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent;
             margin-bottom:4px">⚡ LiggasSports</div>
        <div style="font-family:Rajdhani,sans-serif;font-size:.8rem;
             letter-spacing:4px;color:#304050;text-transform:uppercase;
             margin-bottom:2rem">Gerenciador Profissional de Campeonatos</div>
    </div>""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,1.4,1])
    with col2:
        st.markdown("""
        <div style="background:#0d1117;border:1px solid #1e3a5f;border-radius:10px;
             padding:28px 32px">
            <div style="font-family:'Barlow Condensed',sans-serif;font-weight:700;
                 font-size:1rem;letter-spacing:2px;color:#607080;text-transform:uppercase;
                 margin-bottom:16px;text-align:center">ENTRAR</div>
        """, unsafe_allow_html=True)

        email = st.text_input("E-mail", placeholder="admin@liggassports.com")
        senha = st.text_input("Senha", type="password", placeholder="••••••••")

        if st.button("⚡ ACESSAR PLATAFORMA", use_container_width=True, type="primary"):
            user = autenticar(email, senha)
            if user:
                st.session_state["usuario"] = user
                st.rerun()
            else:
                st.error("E-mail ou senha incorretos.")

        st.markdown("""
        <div style="margin-top:16px;text-align:center;font-family:Rajdhani,sans-serif;
             font-size:.82rem;color:#304050">
            Padrão: admin@liggassports.com / admin123
        </div></div>""", unsafe_allow_html=True)
    st.stop()

# ── NAVEGAÇÃO ─────────────────────────────────────────────────
usuario = st.session_state["usuario"]

PAGINAS = {
    "🏠  Dashboard":       "dashboard",
    "🏆  Campeonatos":     "campeonatos",
    "👥  Equipes":         "equipes",
    "🧑‍🤝‍🧑  Jogadores":      "jogadores",
    "⚽  Jogos":           "jogos",
    "📊  Classificação":   "classificacao",
    "📈  Estatísticas":    "estatisticas",
    "🎲  Sorteio ao Vivo": "sorteio",
    "📜  Histórico":       "historico",
    "📄  Relatórios":      "relatorios",
    "⚙️  Configurações":   "configuracoes",
}

with st.sidebar:
    st.markdown(f"""
    <div style="padding:.3rem 0 1.2rem">
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.4rem;
             font-weight:800;letter-spacing:4px;text-transform:uppercase;
             background:linear-gradient(90deg,#0066ff,#00e5ff);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent">
             ⚡ LiggasSports</div>
        <div style="font-family:Rajdhani,sans-serif;font-size:.58rem;
             letter-spacing:3px;color:#304050;text-transform:uppercase">
             Gerenciador de Campeonatos</div>
    </div>
    <div style="background:#0d1a2d;border:1px solid #1e3a5f;border-radius:6px;
         padding:8px 12px;margin-bottom:12px">
        <div style="font-family:Rajdhani,sans-serif;font-size:.8rem;color:#607080">
            {usuario['nome']}</div>
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:.65rem;
             letter-spacing:2px;color:#00e5ff;text-transform:uppercase">
             {usuario['perfil']}</div>
    </div>
    """, unsafe_allow_html=True)

    pagina_sel = st.radio("menu", list(PAGINAS.keys()),
                           label_visibility="collapsed")

    st.markdown("<hr style='border-color:#1a2535;margin:12px 0'>", unsafe_allow_html=True)

    if st.button("🚪 Sair", use_container_width=True, type="secondary"):
        del st.session_state["usuario"]
        st.rerun()

    st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:.58rem;'
                'letter-spacing:3px;color:#1e3a5f;text-transform:uppercase;'
                'padding-left:2px">v3.0 · SQLAlchemy · Streamlit</div>',
                unsafe_allow_html=True)

# ── RENDER PÁGINA ─────────────────────────────────────────────
modulo = PAGINAS[pagina_sel]

if modulo == "dashboard":
    from pages.dashboard import render
elif modulo == "campeonatos":
    from pages.campeonatos import render
elif modulo == "equipes":
    from pages.equipes import render
elif modulo == "jogadores":
    from pages.jogadores import render
elif modulo == "jogos":
    from pages.jogos import render
elif modulo == "classificacao":
    from pages.classificacao import render
elif modulo == "estatisticas":
    from pages.estatisticas import render
elif modulo == "sorteio":
    from pages.sorteio import render
elif modulo == "historico":
    from pages.historico import render
elif modulo == "relatorios":
    from pages.relatorios import render
elif modulo == "configuracoes":
    from pages.configuracoes import render

render()
