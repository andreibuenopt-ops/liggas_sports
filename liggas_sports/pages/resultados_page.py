import streamlit as st
from utils.database import (
    listar_jogos, listar_times, registrar_resultado,
    adicionar_artilheiro, adicionar_cartao, get_campeonato,
    artilheiros_campeonato, cartoes_campeonato
)

def render(campeonato_id):
    camp = get_campeonato(campeonato_id)
    is_futebol = camp["modalidade"] == "Futebol"

    st.markdown('<div class="xt-page-title">📊 Resultados</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="xt-page-sub">{camp["nome"]}</div>', unsafe_allow_html=True)

    jogos = listar_jogos(campeonato_id)
    times = listar_times(campeonato_id)
    times_map = {t["id"]: t for t in times}

    pendentes  = [j for j in jogos if j["status"] == "pendente" and j["time1_id"] and j["time2_id"]]
    realizados = [j for j in jogos if j["status"] == "realizado"]

    col1, col2 = st.columns(2)
    col1.metric("⏳ Pendentes", len(pendentes))
    col2.metric("✅ Realizados", len(realizados))

    if not pendentes:
        st.success("🎉 Todos os jogos foram registrados!")
        if is_futebol:
            _destaques(campeonato_id)
        return

    st.markdown("<hr class='xt-divider'>", unsafe_allow_html=True)
    st.markdown('<div class="xt-section-label">Registrar Resultado</div>', unsafe_allow_html=True)

    opcoes = {}
    for j in pendentes:
        t1 = times_map.get(j["time1_id"], {}).get("nome", "?")
        t2 = times_map.get(j["time2_id"], {}).get("nome", "?")
        opcoes[f"[Rodada {j['rodada']}]  {t1}  ×  {t2}  ({j['fase']})"] = j

    jogo_label = st.selectbox("Jogo", list(opcoes.keys()))
    jogo = opcoes[jogo_label]
    t1_id, t2_id = jogo["time1_id"], jogo["time2_id"]
    t1_nome = times_map[t1_id]["nome"]
    t2_nome = times_map[t2_id]["nome"]

    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        st.markdown(f'<div style="font-family:Barlow Condensed,sans-serif;font-weight:800;font-size:1.2rem;color:#e0e6f0;text-align:center;letter-spacing:1px">{t1_nome}</div>', unsafe_allow_html=True)
        p1 = st.number_input("Gols", 0, 99, 0, key=f"p1_{jogo['id']}", label_visibility="collapsed")
    with col2:
        st.markdown('<div style="font-family:Barlow Condensed,sans-serif;font-size:1.4rem;font-weight:800;color:#304050;text-align:center;padding-top:8px">×</div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div style="font-family:Barlow Condensed,sans-serif;font-weight:800;font-size:1.2rem;color:#e0e6f0;text-align:center;letter-spacing:1px">{t2_nome}</div>', unsafe_allow_html=True)
        p2 = st.number_input("Gols", 0, 99, 0, key=f"p2_{jogo['id']}", label_visibility="collapsed")

    col_d, col_l = st.columns(2)
    with col_d: data_jogo = st.date_input("Data", key=f"data_{jogo['id']}")
    with col_l: local_jogo = st.text_input("Local", key=f"loc_{jogo['id']}", placeholder="Campo, arena...")

    art_input, cart_input = [], []
    if is_futebol:
        with st.expander("⚽ Artilheiros"):
            n = st.number_input("Gols a registrar", 0, 20, 0, key=f"na_{jogo['id']}")
            for i in range(int(n)):
                c1,c2,c3 = st.columns([2,1,1])
                with c1: nj = st.text_input(f"Jogador {i+1}", key=f"aj_{jogo['id']}_{i}")
                with c2: tj = st.selectbox("Time", [t1_nome, t2_nome], key=f"at_{jogo['id']}_{i}")
                with c3: gl = st.number_input("Gols", 1, 10, 1, key=f"ag_{jogo['id']}_{i}")
                art_input.append((nj, t1_id if tj==t1_nome else t2_id, gl))
        with st.expander("🟨 Cartões"):
            n = st.number_input("Cartões", 0, 20, 0, key=f"nc_{jogo['id']}")
            for i in range(int(n)):
                c1,c2,c3 = st.columns([2,1,1])
                with c1: nj = st.text_input(f"Jogador {i+1}", key=f"cj_{jogo['id']}_{i}")
                with c2: tj = st.selectbox("Time", [t1_nome, t2_nome], key=f"ct_{jogo['id']}_{i}")
                with c3: tp = st.selectbox("Tipo", ["Amarelo","Vermelho"], key=f"cp_{jogo['id']}_{i}")
                cart_input.append((nj, t1_id if tj==t1_nome else t2_id, tp))

    if st.button("⚡ CONFIRMAR RESULTADO", use_container_width=True, type="primary"):
        registrar_resultado(jogo["id"], p1, p2)
        for nj, tid, gl in art_input:
            if nj.strip(): adicionar_artilheiro(jogo["id"], tid, nj.strip(), gl)
        for nj, tid, tp in cart_input:
            if nj.strip(): adicionar_cartao(jogo["id"], tid, nj.strip(), tp)
        st.success(f"✅  {t1_nome}  {p1}  ×  {p2}  {t2_nome}")
        st.rerun()

    st.markdown("<hr class='xt-divider'>", unsafe_allow_html=True)
    if is_futebol:
        _destaques(campeonato_id)


def _destaques(campeonato_id):
    tab1, tab2 = st.tabs(["⚽ Artilheiros", "🟨 Cartões"])
    with tab1:
        arts = artilheiros_campeonato(campeonato_id)
        if arts:
            import pandas as pd
            df = pd.DataFrame(arts)[["jogador","time","total_gols"]]
            df.columns = ["Jogador","Time","Gols"]
            df.index = range(1, len(df)+1)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Nenhum artilheiro registrado.")
    with tab2:
        carts = cartoes_campeonato(campeonato_id)
        if carts:
            import pandas as pd
            df = pd.DataFrame(carts)[["jogador","time","tipo","total"]]
            df.columns = ["Jogador","Time","Tipo","Total"]
            df.index = range(1, len(df)+1)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Nenhum cartão registrado.")
