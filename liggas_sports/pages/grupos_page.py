import streamlit as st
import json
from utils.database import listar_times, get_campeonato, atualizar_grupo_time, get_conn
from utils.logica import (gerar_fase_grupos, calcular_classificacao_grupo,
                           get_classificados_grupos, gerar_mata_mata, nome_fase)

def render(campeonato_id):
    camp = get_campeonato(campeonato_id)
    config = json.loads(camp.get("config") or "{}")
    n_grupos = config.get("n_grupos", 4)
    class_por_grupo = config.get("classificados_por_grupo", 2)
    ida_volta_grupos = config.get("ida_volta_grupos", False)
    ida_volta_mata = config.get("ida_volta_mata", False)
    tipo_sorteio = "potes" if "potes" in config.get("tipo_sorteio","") else "aleatorio"

    st.markdown('<div class="xt-page-title">🌍 Fase de Grupos</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="xt-page-sub">{camp["nome"]} — {n_grupos} grupos · {class_por_grupo} classificados por grupo</div>', unsafe_allow_html=True)

    times = listar_times(campeonato_id)

    # ── Controles ─────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎲 SORTEAR GRUPOS", use_container_width=True, type="primary"):
            if len(times) < n_grupos * 2:
                st.error(f"Adicione pelo menos {n_grupos*2} times!")
            else:
                ok, msg = gerar_fase_grupos(campeonato_id, n_grupos, class_por_grupo,
                                            ida_volta_grupos, tipo_sorteio)
                st.success(msg) if ok else st.error(msg)
                st.rerun()
    with col2:
        if st.button("⏭️ GERAR MATA-MATA COM CLASSIFICADOS", use_container_width=True):
            _gerar_mata_mata_classificados(campeonato_id, class_por_grupo, ida_volta_mata)
            st.rerun()

    times_com_grupo = [t for t in times if t.get("grupo")]
    if not times_com_grupo:
        st.info("Clique em **Sortear Grupos** para distribuir os times.")
        return

    st.markdown("<hr class='xt-divider'>", unsafe_allow_html=True)

    # ── Grupos lado a lado ────────────────────────────────────
    grupos = sorted(set(t["grupo"] for t in times_com_grupo))
    cols_por_linha = min(4, len(grupos))
    rows = [grupos[i:i+cols_por_linha] for i in range(0, len(grupos), cols_por_linha)]

    for row in rows:
        cols = st.columns(len(row))
        for col, g in zip(cols, row):
            classif = calcular_classificacao_grupo(campeonato_id, g)
            with col:
                st.markdown(f"""
                <div style="background:#0d1a2d;border:1px solid #1e3a5f;
                     border-top:3px solid #00e5ff;border-radius:6px;
                     padding:12px;margin-bottom:12px">
                    <div style="font-family:Barlow Condensed,sans-serif;font-weight:800;
                         font-size:1rem;letter-spacing:3px;color:#00e5ff;
                         margin-bottom:10px">GRUPO {g}</div>
                """, unsafe_allow_html=True)

                for i, t in enumerate(classif):
                    cor_pos = "#ffaa00" if i < class_por_grupo else "#304050"
                    sep = "border-bottom:1px solid #111827;" if i < len(classif)-1 else ""
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;
                         align-items:center;padding:5px 0;{sep}">
                        <div style="display:flex;align-items:center;gap:6px">
                            <span style="font-family:Barlow Condensed,sans-serif;
                                  font-size:0.75rem;font-weight:700;color:{cor_pos};
                                  min-width:14px">{i+1}</span>
                            <div style="width:8px;height:8px;border-radius:50%;
                                 background:{t['cor']}"></div>
                            <span style="font-family:Rajdhani,sans-serif;font-weight:600;
                                  font-size:0.85rem;color:#c0d0e0">{t['time']}</span>
                        </div>
                        <div style="display:flex;gap:10px">
                            <span style="font-family:Barlow Condensed,sans-serif;
                                  font-size:0.75rem;color:#405060">{t['PJ']}J</span>
                            <span style="font-family:Barlow Condensed,sans-serif;
                                  font-size:0.85rem;font-weight:700;color:#e0e6f0">{t['PTS']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)

    # ── Jogos da fase de grupos ───────────────────────────────
    st.markdown("<hr class='xt-divider'>", unsafe_allow_html=True)
    st.markdown('<div class="xt-section-label">Jogos por Grupo</div>', unsafe_allow_html=True)

    from utils.database import listar_jogos
    jogos = listar_jogos(campeonato_id, "Fase de Grupos")
    times_map = {t["id"]: t for t in times}

    grupo_sel = st.selectbox("Filtrar Grupo", ["Todos"] + grupos)

    for j in jogos:
        t1 = times_map.get(j["time1_id"], {})
        t2 = times_map.get(j["time2_id"], {})
        if grupo_sel != "Todos" and t1.get("grupo") != grupo_sel:
            continue

        nome1 = t1.get("nome", "?")
        nome2 = t2.get("nome", "?")
        cor1 = t1.get("cor", "#0066ff")
        cor2 = t2.get("cor", "#0066ff")
        p1 = j["placar1"]
        p2 = j["placar2"]
        placar = f"{p1}  ×  {p2}" if p1 is not None else "VS"
        s_cor = "#00e5ff" if j["status"] == "realizado" else "#ffaa00"
        grupo_label = t1.get("grupo", "?")

        st.markdown(f"""
        <div style="background:#0d1a2d;border:1px solid #1e3a5f;border-radius:6px;
             padding:10px 16px;margin-bottom:6px;display:flex;
             align-items:center;justify-content:space-between">
            <span style="font-family:Barlow Condensed,sans-serif;font-size:0.65rem;
                  color:#304050;letter-spacing:2px;min-width:60px">GRP {grupo_label} · R{j['rodada']}</span>
            <div style="display:flex;align-items:center;gap:10px;flex:1;justify-content:center">
                <div style="display:flex;align-items:center;gap:6px">
                    <div style="width:8px;height:8px;border-radius:50%;background:{cor1}"></div>
                    <span style="font-family:Rajdhani,sans-serif;font-weight:700;color:#c0d0e0">{nome1}</span>
                </div>
                <span style="font-family:Barlow Condensed,sans-serif;font-size:0.95rem;
                      font-weight:800;color:#405060;padding:0 12px;letter-spacing:2px">{placar}</span>
                <div style="display:flex;align-items:center;gap:6px">
                    <span style="font-family:Rajdhani,sans-serif;font-weight:700;color:#c0d0e0">{nome2}</span>
                    <div style="width:8px;height:8px;border-radius:50%;background:{cor2}"></div>
                </div>
            </div>
            <span style="font-family:Barlow Condensed,sans-serif;font-size:0.65rem;
                  font-weight:700;letter-spacing:2px;color:{s_cor};min-width:70px;text-align:right">
                {j['status'].upper()}</span>
        </div>
        """, unsafe_allow_html=True)


def _gerar_mata_mata_classificados(campeonato_id, class_por_grupo, ida_volta_mata):
    from utils.database import listar_jogos
    jogos_grupos = listar_jogos(campeonato_id, "Fase de Grupos")
    pendentes = [j for j in jogos_grupos if j["status"] == "pendente"
                 and j["time1_id"] and j["time2_id"]]
    if pendentes:
        st.warning(f"⚠️ Ainda há {len(pendentes)} jogo(s) pendente(s) na fase de grupos!")
        return

    classificados, terceiros = get_classificados_grupos(campeonato_id, class_por_grupo)
    times_ids = [t["id"] for _, _, t in classificados]

    if not times_ids:
        st.error("Nenhum classificado encontrado. Registre os resultados da fase de grupos primeiro.")
        return

    n = len(times_ids)
    fase = nome_fase(n)
    rodada_base = max((j["rodada"] for j in jogos_grupos), default=0) + 1
    gerar_mata_mata(campeonato_id, times_ids, fase, ida_volta_mata, rodada_base)
    st.success(f"✅ {fase} gerada com {n} times classificados!")
