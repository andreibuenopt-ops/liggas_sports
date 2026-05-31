import streamlit as st
import json
from utils.database import criar_campeonato

GAMES = ["Nenhum (campeonato normal)", "EA FC / FIFA", "eFootball", "PES"]

def render():
    st.markdown('<div class="xt-page-title">➕ Novo Campeonato</div>', unsafe_allow_html=True)
    st.markdown('<div class="xt-page-sub">Configure cada detalhe do seu campeonato</div>', unsafe_allow_html=True)

    with st.form("form_novo"):
        nome = st.text_input("Nome do Campeonato *", placeholder="Ex: Copa da Firma 2025, Liga do Bairro...")

        st.markdown("<hr class='xt-divider'>", unsafe_allow_html=True)
        st.markdown('<div class="xt-section-label">Formato</div>', unsafe_allow_html=True)

        formato = st.radio("Formato", [
            "🏆 Liga (pontos corridos)",
            "⚔️ Mata-Mata (eliminatória)",
            "🌍 Copa do Mundo (grupos + mata-mata)",
        ], horizontal=False, label_visibility="collapsed")

        st.markdown("<hr class='xt-divider'>", unsafe_allow_html=True)
        st.markdown('<div class="xt-section-label">Configurações do Formato</div>', unsafe_allow_html=True)

        config = {}

        if "Liga" in formato:
            config["formato"] = "Liga"
            config["ida_volta"] = st.checkbox("Ida e volta", value=True)

        elif "Mata-Mata" in formato:
            config["formato"] = "Mata-Mata"
            config["ida_volta_mata"] = st.checkbox("2 jogos por fase (ida e volta)", value=False,
                help="Cada confronto tem jogo de ida e volta, avança quem tiver maior agregado")

        elif "Copa do Mundo" in formato:
            config["formato"] = "Copa do Mundo"
            col1, col2, col3 = st.columns(3)
            with col1:
                config["n_grupos"] = st.number_input("Nº de Grupos", 2, 16, 4, step=2)
            with col2:
                config["classificados_por_grupo"] = st.number_input("Classificados por grupo", 1, 4, 2)
            with col3:
                config["ida_volta_grupos"] = st.checkbox("Ida e volta nos grupos", value=False)

            config["tipo_sorteio"] = st.radio(
                "Tipo de Sorteio dos Grupos",
                ["🎯 Por potes (rating — melhores separados)", "🎲 Aleatório puro"],
                horizontal=True, label_visibility="visible"
            )
            config["ida_volta_mata"] = st.checkbox("Ida e volta no mata-mata", value=False)

        st.markdown("<hr class='xt-divider'>", unsafe_allow_html=True)
        st.markdown('<div class="xt-section-label">Game / Modalidade</div>', unsafe_allow_html=True)

        col_g, col_m = st.columns(2)
        with col_g:
            game = st.selectbox("Game (opcional)", GAMES,
                help="Se for videogame, selecione para habilitar rating dos times no sorteio")
        with col_m:
            modalidade = st.selectbox("Modalidade", ["Futebol", "Videogame", "Interclasses", "Genérico"])

        config["game"] = game if game != "Nenhum (campeonato normal)" else None
        config["modalidade"] = modalidade

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("⚡ CRIAR CAMPEONATO", use_container_width=True, type="primary")

    if submitted:
        if not nome.strip():
            st.error("Informe o nome!")
            return
        fmt = config.pop("formato")
        mod = config.pop("modalidade")
        game_val = config.get("game")
        cid = criar_campeonato(nome.strip(), mod, fmt, game_val, config)
        st.success(f"✅ **{nome}** criado! Agora vá em **📋 Gerenciar** → adicione os times.")
