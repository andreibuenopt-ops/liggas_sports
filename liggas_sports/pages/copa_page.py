import streamlit as st
from utils.database import listar_times, listar_jogos, get_campeonato
from utils.logica import gerar_chaves_copa, avancar_fase_copa, get_bracket

def render(campeonato_id):
    camp = get_campeonato(campeonato_id)
    st.markdown(f'<div class="xt-page-title">🎯 Bracket</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="xt-page-sub">{camp["nome"]}</div>', unsafe_allow_html=True)

    times = listar_times(campeonato_id)
    jogos = listar_jogos(campeonato_id)
    times_map = {t["id"]: t for t in times}

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎲 GERAR / RESETAR CHAVES", use_container_width=True, type="primary"):
            if len(times) < 2:
                st.error("Adicione pelo menos 2 times!")
            else:
                ok, msg = gerar_chaves_copa(campeonato_id)
                st.success(msg) if ok else st.error(msg)
                st.rerun()
    with col2:
        if st.button("⏭️ AVANÇAR FASE", use_container_width=True):
            ok, msg = avancar_fase_copa(campeonato_id)
            st.success(msg) if ok else st.warning(msg)
            st.rerun()

    if not jogos:
        st.info("Clique em **Gerar Chaves** para criar o chaveamento.")
        return

    bracket = get_bracket(campeonato_id)
    st.markdown("<hr class='xt-divider'>", unsafe_allow_html=True)
    st.markdown('<div class="xt-section-label">Chaveamento</div>', unsafe_allow_html=True)

    fases = list(bracket.keys())
    cols = st.columns(len(fases))

    for col_idx, fase in enumerate(fases):
        with cols[col_idx]:
            st.markdown(f"""
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:0.7rem;
                 font-weight:700;letter-spacing:2px;text-transform:uppercase;
                 color:#00e5ff;margin-bottom:10px;border-bottom:1px solid #1e3a5f;
                 padding-bottom:6px">{fase}</div>
            """, unsafe_allow_html=True)

            for jogo in bracket[fase]:
                p1, p2 = jogo["placar1"], jogo["placar2"]
                t1, t2 = jogo["time1"], jogo["time2"]

                if jogo["status"] == "realizado":
                    venc1 = p1 > p2
                    cor1 = "#00e5ff" if venc1 else "#304050"
                    cor2 = "#00e5ff" if not venc1 else "#304050"
                    fw1 = "700" if venc1 else "400"
                    fw2 = "700" if not venc1 else "400"
                    placar = f"{p1}  ×  {p2}"
                else:
                    cor1 = cor2 = "#607080"
                    fw1 = fw2 = "400"
                    placar = "VS"

                st.markdown(f"""
                <div class="xt-bracket-card">
                    <div class="xt-match-team" style="color:{cor1};font-weight:{fw1}">{t1}</div>
                    <div class="xt-match-score">{placar}</div>
                    <div class="xt-match-team" style="color:{cor2};font-weight:{fw2}">{t2}</div>
                </div>
                """, unsafe_allow_html=True)
