import streamlit as st
from utils.database import criar_campeonato

MODALIDADES = ["Futebol", "Videogame", "Interclasses", "Genérico"]
FORMATOS    = ["Copa", "Liga"]
ESPORTES    = ["Futebol", "Futsal", "Vôlei", "Basquete", "Handebol", "Tênis de Mesa", "Xadrez", "Corrida", "Outro"]

def render():
    st.markdown('<div class="xt-page-title">➕ Novo Campeonato</div>', unsafe_allow_html=True)
    st.markdown('<div class="xt-page-sub">Configure e crie seu campeonato</div>', unsafe_allow_html=True)

    with st.form("form_novo"):
        nome = st.text_input("Nome do Campeonato", placeholder="Ex: Copa da Firma 2025, Interclasses 3ºA...")

        col1, col2 = st.columns(2)
        with col1:
            modalidade = st.selectbox("Modalidade", MODALIDADES)
        with col2:
            formato = st.selectbox("Formato", FORMATOS,
                help="Copa = eliminatória com chaveamento | Liga = pontos corridos")

        esporte = None
        if modalidade == "Interclasses":
            esporte = st.selectbox("Esporte/Disciplina", ESPORTES)
        elif modalidade == "Genérico":
            esporte = st.text_input("Nome da Disputa", placeholder="Ex: CS2, Xadrez, Corrida...")

        col3, col4 = st.columns(2)
        with col3:
            ida_volta = st.checkbox("Ida e volta", value=True,
                disabled=(formato == "Copa"),
                help="Apenas para formato Liga")
        with col4:
            sorteio = st.checkbox("Sorteio automático de chaves", value=True)

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("⚡ CRIAR CAMPEONATO", use_container_width=True, type="primary")

    if submitted:
        if not nome.strip():
            st.error("Informe o nome do campeonato!")
            return
        config = {"ida_volta": ida_volta, "sorteio": sorteio}
        cid = criar_campeonato(nome.strip(), modalidade, formato, esporte, config)
        st.success(f"✅ **{nome}** criado! Vá em **📋 Gerenciar** para adicionar times e jogadores.")
