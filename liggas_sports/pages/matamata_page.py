import streamlit as st
import json
from utils.database import listar_times, listar_jogos, get_campeonato
from utils.logica import gerar_mata_mata, avancar_mata_mata, get_bracket, nome_fase

def render(campeonato_id):
    camp = get_campeonato(campeonato_id)
    config = json.loads(camp.get("config") or "{}")
    ida_volta_mata = config.get("ida_volta_mata", False)

    st.markdown('<div class="xt-page-title">⚔️ Mata-Mata</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="xt-page-sub">{camp["nome"]}</div>', unsafe_allow_html=True)

    times = listar_times(campeonato_id)
    jogos_mata = [j for j in listar_jogos(campeonato_id) if j["fase"] != "Fase de Grupos"]
    times_map = {t["id"]: t for t in times}

    # Só mostra gerar se for Mata-Mata puro (Copa do Mundo já gera pelo grupos_page)
    if camp["formato"] == "Mata-Mata":
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎲 GERAR / RESETAR CHAVES", use_container_width=True, type="primary"):
                if len(times) < 2:
                    st.error("Adicione pelo menos 2 times!")
                else:
                    from utils.database import limpar_jogos
                    limpar_jogos(campeonato_id)
                    times_ids = [t["id"] for t in times]
                    fase = nome_fase(len(times_ids))
                    gerar_mata_mata(campeonato_id, times_ids, fase, ida_volta_mata, 1)
                    st.success(f"✅ {fase} gerada!")
                    st.rerun()
        with col2:
            if jogos_mata:
                fases_existentes = list(dict.fromkeys(j["fase"] for j in jogos_mata))
                fase_atual = fases_existentes[-1]
                if st.button(f"⏭️ AVANÇAR FASE", use_container_width=True):
                    ok, msg = avancar_mata_mata(campeonato_id, fase_atual, ida_volta_mata)
                    st.success(msg) if ok else st.warning(msg)
                    st.rerun()
    else:
        # Copa do Mundo — botão avançar fase
        if jogos_mata:
            fases_existentes = list(dict.fromkeys(j["fase"] for j in jogos_mata))
            fase_atual = fases_existentes[-1]
            col1, _ = st.columns(2)
            with col1:
                if st.button(f"⏭️ AVANÇAR: {fase_atual} → próxima fase", use_container_width=True, type="primary"):
                    ok, msg = avancar_mata_mata(campeonato_id, fase_atual, ida_volta_mata)
                    st.success(msg) if ok else st.warning(msg)
                    st.rerun()

    if not jogos_mata:
        if camp["formato"] == "Copa do Mundo":
            st.info("Finalize a fase de grupos e clique em **Gerar Mata-Mata** na aba Grupos.")
        else:
            st.info("Clique em **Gerar Chaves** para iniciar o mata-mata.")
        return

    # ── Bracket ───────────────────────────────────────────────
    bracket = get_bracket(campeonato_id)
    if not bracket:
        return

    st.markdown("<hr class='xt-divider'>", unsafe_allow_html=True)
    st.markdown('<div class="xt-section-label">Chaveamento</div>', unsafe_allow_html=True)

    fases = list(bracket.keys())
    cols = st.columns(max(1, len(fases)))

    for col_idx, fase in enumerate(fases):
        with cols[col_idx]:
            st.markdown(f"""
            <div style="font-family:Barlow Condensed,sans-serif;font-size:0.7rem;
                 font-weight:700;letter-spacing:2px;text-transform:uppercase;
                 color:#00e5ff;margin-bottom:10px;border-bottom:1px solid #1e3a5f;
                 padding-bottom:6px">{fase}</div>
            """, unsafe_allow_html=True)

            for jogo in bracket[fase]:
                _render_bracket_card(jogo, ida_volta_mata)


def _render_bracket_card(jogo, tem_volta):
    t1, t2 = jogo["time1"], jogo["time2"]
    p1, p2 = jogo["placar1"], jogo["placar2"]
    p1v, p2v = jogo.get("placar1_volta"), jogo.get("placar2_volta")

    if jogo["status"] == "realizado":
        if tem_volta and p1v is not None:
            agg1 = (p1 or 0) + (p2v or 0)
            agg2 = (p2 or 0) + (p1v or 0)
            venc1 = agg1 >= agg2
            placar_str = f"{p1}-{p2} / {p2v}-{p1v} (agg {agg1}×{agg2})"
        else:
            venc1 = (p1 or 0) > (p2 or 0)
            placar_str = f"{p1} × {p2}"

        cor1 = "#00e5ff" if venc1 else "#304050"
        cor2 = "#00e5ff" if not venc1 else "#304050"
        fw1 = "700" if venc1 else "400"
        fw2 = "700" if not venc1 else "400"
    else:
        cor1 = cor2 = "#607080"
        fw1 = fw2 = "400"
        placar_str = "VS"

    st.markdown(f"""
    <div style="background:#0d1a2d;border:1px solid #1e3a5f;border-radius:4px;
         padding:8px 12px;margin-bottom:6px;border-left:2px solid #1e3a5f">
        <div style="font-family:Rajdhani,sans-serif;font-size:0.85rem;
             font-weight:{fw1};color:{cor1}">{t1}</div>
        <div style="font-family:Barlow Condensed,sans-serif;font-size:0.7rem;
             color:#304050;text-align:center;padding:2px 0;letter-spacing:1px">{placar_str}</div>
        <div style="font-family:Rajdhani,sans-serif;font-size:0.85rem;
             font-weight:{fw2};color:{cor2}">{t2}</div>
    </div>
    """, unsafe_allow_html=True)
