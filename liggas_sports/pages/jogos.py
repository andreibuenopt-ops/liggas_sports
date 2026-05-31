import streamlit as st
from core import engine, style

def render():
    cfg = engine.get_config()
    if not cfg:
        st.info("Configure um campeonato primeiro."); return

    style.h1(st, "⚽ Jogos", f"{cfg.get('nome','')}")

    fases = engine.get_fases()
    if not fases:
        st.info("Nenhum jogo gerado."); return

    tab_reg, tab_lista = st.tabs(["📝 Registrar Resultado", "📋 Todos os Jogos"])

    with tab_reg:
        _registrar(fases)

    with tab_lista:
        _listar(fases)


def _registrar(fases):
    fases_pend = [f for f in fases if engine.get_jogos(fase=f, status="Agendado")]
    if not fases_pend:
        st.success("🎉 Todos os jogos foram registrados!")
        return

    fase_sel = st.selectbox("Fase", fases_pend)
    rodadas = engine.get_rodadas(fase=fase_sel)
    rodada_sel = st.selectbox("Rodada", rodadas, format_func=lambda r: f"Rodada {r}")

    pendentes = engine.get_jogos(fase=fase_sel, rodada=rodada_sel, status="Agendado")
    if not pendentes:
        st.info("Todos os jogos desta rodada já foram registrados.")
        return

    opcoes = {f"{j['casa']}  ×  {j['fora']}": j["id"] for j in pendentes
              if j.get("casa") and j.get("fora")}
    if not opcoes: st.info("Nenhum jogo disponível."); return

    jogo_lbl = st.selectbox("Jogo", list(opcoes.keys()))
    jid = opcoes[jogo_lbl]
    jogo = next(j for j in pendentes if j["id"] == jid)
    t1, t2 = jogo["casa"], jogo["fora"]
    tem_volta = jogo.get("ida_volta", False)

    # Placar
    st.markdown(f"""
    <div style="background:#0d1a2d;border:1px solid #1e3a5f;border-radius:8px;
         padding:12px 18px;margin:10px 0;text-align:center">
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:.62rem;
             letter-spacing:3px;color:#304050;margin-bottom:4px">
            {fase_sel} · {'IDA E VOLTA' if tem_volta else 'JOGO ÚNICO'}
        </div>
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.3rem;
             font-weight:800;color:#e0e6f0;letter-spacing:2px">
            {t1}  <span style="color:#304050">×</span>  {t2}
        </div>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([2, 0.7, 2])
    with c1:
        st.markdown(f'<div style="font-family:Barlow Condensed,sans-serif;font-weight:800;text-align:center;color:#e0e6f0">{t1}</div>', unsafe_allow_html=True)
        p1 = st.number_input("Gols", 0, 99, 0, key=f"p1_{jid}", label_visibility="collapsed")
    with c2:
        st.markdown('<div style="text-align:center;padding-top:8px;font-size:1.2rem;color:#304050">×</div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div style="font-family:Barlow Condensed,sans-serif;font-weight:800;text-align:center;color:#e0e6f0">{t2}</div>', unsafe_allow_html=True)
        p2 = st.number_input("Gols", 0, 99, 0, key=f"p2_{jid}", label_visibility="collapsed")

    p1v = p2v = None
    if tem_volta:
        style.lbl(st, "Jogo de Volta")
        c4, c5, c6 = st.columns([2, 0.7, 2])
        with c4: p2v = st.number_input(f"{t2} (casa)", 0, 99, 0, key=f"p2v_{jid}")
        with c5: st.markdown('<div style="text-align:center;padding-top:28px;color:#304050">×</div>', unsafe_allow_html=True)
        with c6: p1v = st.number_input(f"{t1} (fora)", 0, 99, 0, key=f"p1v_{jid}")
        agg1 = p1 + (p2v or 0); agg2 = p2 + (p1v or 0)
        venc = t1 if agg1 >= agg2 else t2
        st.info(f"Agregado: {t1} **{agg1}** × **{agg2}** {t2} → **{venc}** avança")

    cd, cl = st.columns(2)
    with cd: data_j = str(st.date_input("Data", key=f"dt_{jid}"))
    with cl: local_j = st.text_input("Local", key=f"loc_{jid}", placeholder="Campo, arena...")

    # Eventos (gols por jogador)
    jogadores = engine.get_jogadores()
    jogs_t1 = [j for j in jogadores if j.get("equipe") == t1]
    jogs_t2 = [j for j in jogadores if j.get("equipe") == t2]

    if jogs_t1 or jogs_t2:
        with st.expander("⚽ Registrar Gols / Eventos"):
            all_jogs = jogs_t1 + jogs_t2
            opts = {f"{j['nome']} ({j.get('equipe','?')})": j["id"] for j in all_jogs}
            c_ev1, c_ev2, c_ev3 = st.columns(3)
            with c_ev1: tipo_ev = st.selectbox("Tipo", ["gol","assist","amarelo","vermelho"])
            with c_ev2: jog_sel = st.selectbox("Jogador", list(opts.keys()))
            with c_ev3: min_ev = st.number_input("Minuto", 1, 120, 1)
            if st.button("➕ Registrar Evento"):
                engine.registrar_evento(jid, tipo_ev, opts[jog_sel], min_ev)
                st.success("✅ Evento registrado!")

            # Mostra eventos já registrados
            evs = engine.get_eventos(jid)
            jog_map = {j["id"]: j["nome"] for j in jogadores}
            for e in evs:
                icone = {"gol":"⚽","assist":"🎯","amarelo":"🟨","vermelho":"🟥"}.get(e["tipo"],"•")
                st.markdown(f'<div style="font-size:.82rem;color:#a0b0c0;padding:2px 0">'
                            f'{icone} {jog_map.get(e["jogador_id"],"?")} · {e.get("minuto","?")}′</div>',
                            unsafe_allow_html=True)

    if st.button("⚡ CONFIRMAR RESULTADO", use_container_width=True, type="primary"):
        engine.registrar_resultado(jid, p1, p2, p1v, p2v, data_j, local_j)
        st.success(f"✅ {t1} {p1} × {p2} {t2}" +
                   (f" | Volta: {p2v} × {p1v}" if tem_volta and p1v is not None else ""))
        st.rerun()


def _listar(fases):
    fase_f = st.selectbox("Filtrar fase", ["Todas"] + fases, key="fase_lista")
    status_f = st.radio("Status", ["Todos","Agendado","Finalizado"], horizontal=True)

    jogos = engine.get_jogos(
        fase=fase_f if fase_f != "Todas" else None,
        status=status_f if status_f != "Todos" else None
    )

    st.metric("Jogos", len(jogos))
    style.div(st)

    fases_show = list(dict.fromkeys(j.get("fase","") for j in jogos))
    for fase in fases_show:
        style.lbl(st, fase)
        for j in [x for x in jogos if x.get("fase") == fase]:
            st.markdown(style.jogo_row(j, show_grupo=True), unsafe_allow_html=True)
