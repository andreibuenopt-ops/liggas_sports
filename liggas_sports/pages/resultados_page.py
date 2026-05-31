import streamlit as st
import json
from utils.database import (
    listar_jogos, listar_times, registrar_resultado, get_campeonato,
    adicionar_artilheiro, adicionar_cartao, artilheiros_campeonato, cartoes_campeonato
)

def render(campeonato_id):
    camp = get_campeonato(campeonato_id)
    config = json.loads(camp.get("config") or "{}")
    is_futebol = camp["modalidade"] == "Futebol"

    st.markdown('<div class="xt-page-title">📊 Resultados</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="xt-page-sub">{camp["nome"]}</div>', unsafe_allow_html=True)

    jogos = listar_jogos(campeonato_id)
    times = listar_times(campeonato_id)
    times_map = {t["id"]: t for t in times}

    pendentes = [j for j in jogos if j["status"] == "pendente"
                 and j["time1_id"] and j["time2_id"]]
    realizados = [j for j in jogos if j["status"] == "realizado"]

    c1, c2 = st.columns(2)
    c1.metric("⏳ Pendentes", len(pendentes))
    c2.metric("✅ Realizados", len(realizados))

    if not pendentes:
        st.success("🎉 Todos os jogos registrados!")
        if is_futebol: _destaques(campeonato_id)
        return

    st.markdown("<hr class='xt-divider'>", unsafe_allow_html=True)

    # Filtra por fase
    fases = list(dict.fromkeys(j["fase"] for j in pendentes))
    fase_sel = st.selectbox("Fase", fases) if len(fases) > 1 else fases[0]
    pendentes_fase = [j for j in pendentes if j["fase"] == fase_sel]

    st.markdown('<div class="xt-section-label">Selecionar Jogo</div>', unsafe_allow_html=True)

    opcoes = {}
    for j in pendentes_fase:
        t1 = times_map.get(j["time1_id"], {}).get("nome", "?")
        t2 = times_map.get(j["time2_id"], {}).get("nome", "?")
        volta_tag = " [IDA]" if j.get("tem_volta") else ""
        opcoes[f"R{j['rodada']} · {t1}  ×  {t2}{volta_tag}"] = j

    if not opcoes:
        st.info("Nenhum jogo pendente nesta fase.")
        return

    jogo_label = st.selectbox("Jogo", list(opcoes.keys()))
    jogo = opcoes[jogo_label]
    t1_id, t2_id = jogo["time1_id"], jogo["time2_id"]
    t1_nome = times_map[t1_id]["nome"]
    t2_nome = times_map[t2_id]["nome"]
    tem_volta = bool(jogo.get("tem_volta"))

    # ── Placar ────────────────────────────────────────────────
    st.markdown(f"""
    <div style="text-align:center;padding:8px 0 4px">
        <span style="font-family:Barlow Condensed,sans-serif;font-size:0.65rem;
              letter-spacing:3px;text-transform:uppercase;color:#405060">
            {'IDA E VOLTA' if tem_volta else 'JOGO ÚNICO'}</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 0.8, 2])
    with col1:
        st.markdown(f'<div style="font-family:Barlow Condensed,sans-serif;font-weight:800;font-size:1.1rem;color:#e0e6f0;text-align:center;letter-spacing:1px">{t1_nome}</div>', unsafe_allow_html=True)
        p1 = st.number_input("Gols", 0, 99, 0, key=f"p1_{jogo['id']}", label_visibility="collapsed")
    with col2:
        st.markdown('<div style="text-align:center;padding-top:8px;font-family:Barlow Condensed,sans-serif;font-size:1.3rem;font-weight:800;color:#304050">×</div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div style="font-family:Barlow Condensed,sans-serif;font-weight:800;font-size:1.1rem;color:#e0e6f0;text-align:center;letter-spacing:1px">{t2_nome}</div>', unsafe_allow_html=True)
        p2 = st.number_input("Gols", 0, 99, 0, key=f"p2_{jogo['id']}", label_visibility="collapsed")

    p1v = p2v = None
    if tem_volta:
        st.markdown('<div class="xt-section-label" style="margin-top:12px">Jogo de Volta</div>', unsafe_allow_html=True)
        col4, col5, col6 = st.columns([2, 0.8, 2])
        with col4:
            st.markdown(f'<div style="font-family:Barlow Condensed,sans-serif;font-size:0.9rem;color:#607080;text-align:center">{t2_nome} (casa)</div>', unsafe_allow_html=True)
            p2v = st.number_input("Gols volta", 0, 99, 0, key=f"p2v_{jogo['id']}", label_visibility="collapsed")
        with col5:
            st.markdown('<div style="text-align:center;padding-top:8px;font-family:Barlow Condensed,sans-serif;font-size:1.3rem;color:#304050">×</div>', unsafe_allow_html=True)
        with col6:
            st.markdown(f'<div style="font-family:Barlow Condensed,sans-serif;font-size:0.9rem;color:#607080;text-align:center">{t1_nome} (fora)</div>', unsafe_allow_html=True)
            p1v = st.number_input("Gols volta", 0, 99, 0, key=f"p1v_{jogo['id']}", label_visibility="collapsed")

        agg1 = p1 + (p2v or 0)
        agg2 = p2 + (p1v or 0)
        st.markdown(f"""
        <div style="background:#0d1a2d;border:1px solid #1e3a5f;border-radius:6px;
             padding:8px;text-align:center;margin:8px 0">
            <span style="font-family:Barlow Condensed,sans-serif;font-size:0.7rem;
                  letter-spacing:2px;color:#405060">AGREGADO: </span>
            <span style="font-family:Barlow Condensed,sans-serif;font-size:1rem;
                  font-weight:800;color:#{'00e5ff' if agg1!=agg2 else 'ffaa00'}">
                {t1_nome} {agg1} × {agg2} {t2_nome}
                {'→ ' + (t1_nome if agg1>agg2 else t2_nome) + ' avança' if agg1!=agg2 else '→ Empate (1º avança)'}
            </span>
        </div>
        """, unsafe_allow_html=True)

    col_d, col_l = st.columns(2)
    with col_d: st.date_input("Data", key=f"data_{jogo['id']}")
    with col_l: st.text_input("Local", key=f"loc_{jogo['id']}", placeholder="Campo, arena...")

    art_input, cart_input = [], []
    if is_futebol:
        with st.expander("⚽ Artilheiros"):
            n = st.number_input("Gols a registrar", 0, 20, 0, key=f"na_{jogo['id']}")
            for i in range(int(n)):
                c1,c2,c3 = st.columns([2,1,1])
                with c1: nj = st.text_input(f"Jogador {i+1}", key=f"aj_{jogo['id']}_{i}")
                with c2: tj = st.selectbox("Time", [t1_nome,t2_nome], key=f"at_{jogo['id']}_{i}")
                with c3: gl = st.number_input("Gols", 1, 10, 1, key=f"ag_{jogo['id']}_{i}")
                art_input.append((nj, t1_id if tj==t1_nome else t2_id, gl))
        with st.expander("🟨 Cartões"):
            n = st.number_input("Cartões", 0, 20, 0, key=f"nc_{jogo['id']}")
            for i in range(int(n)):
                c1,c2,c3 = st.columns([2,1,1])
                with c1: nj = st.text_input(f"Jogador {i+1}", key=f"cj_{jogo['id']}_{i}")
                with c2: tj = st.selectbox("Time", [t1_nome,t2_nome], key=f"ct_{jogo['id']}_{i}")
                with c3: tp = st.selectbox("Tipo", ["Amarelo","Vermelho"], key=f"cp_{jogo['id']}_{i}")
                cart_input.append((nj, t1_id if tj==t1_nome else t2_id, tp))

    if st.button("⚡ CONFIRMAR RESULTADO", use_container_width=True, type="primary"):
        registrar_resultado(jogo["id"], p1, p2, p1v, p2v)
        for nj, tid, gl in art_input:
            if nj.strip(): adicionar_artilheiro(jogo["id"], tid, nj.strip(), gl)
        for nj, tid, tp in cart_input:
            if nj.strip(): adicionar_cartao(jogo["id"], tid, nj.strip(), tp)
        st.success(f"✅ {t1_nome} {p1} × {p2} {t2_nome}" +
                   (f" | Volta: {p2v} × {p1v}" if tem_volta and p1v is not None else ""))
        st.rerun()

    st.markdown("<hr class='xt-divider'>", unsafe_allow_html=True)
    if is_futebol: _destaques(campeonato_id)


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
