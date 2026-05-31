import streamlit as st
from datetime import date
from services.services import (listar_campeonatos, listar_jogos, get_jogo,
                                registrar_resultado, adicionar_evento, eventos_jogo,
                                listar_jogadores, equipes_campeonato)
from utils.style import page_header, divider, section_label, jogo_row

STATUS_OPTS = ["Agendado","Em Andamento","Finalizado","Suspenso","Cancelado"]

def render():
    page_header("⚽ Jogos", "Gerencie partidas e resultados")
    abas = st.tabs(["📋 Listar", "📝 Registrar Resultado", "📊 Súmula"])
    with abas[0]: _listar()
    with abas[1]: _resultado()
    with abas[2]: _sumula()

def _listar():
    camps = listar_campeonatos()
    if not camps:
        st.info("Nenhum campeonato."); return

    col1, col2, col3 = st.columns(3)
    with col1:
        opcoes_camp = {"Todos": None} | {c["nome"]: c["id"] for c in camps}
        sel_camp = st.selectbox("Campeonato", list(opcoes_camp.keys()))
        cid = opcoes_camp[sel_camp]
    with col2:
        sel_status = st.selectbox("Status", ["Todos"] + STATUS_OPTS)
    with col3:
        data_filtro = st.date_input("Data", value=None)

    jogos = listar_jogos(
        cid=cid,
        status=sel_status if sel_status != "Todos" else None,
        data=data_filtro
    )

    st.metric("Jogos encontrados", len(jogos))
    divider()

    fases = list(dict.fromkeys(j["fase"] for j in jogos if j["fase"]))
    for fase in fases:
        st.markdown(f'<div class="ls-label">{fase}</div>', unsafe_allow_html=True)
        for j in [x for x in jogos if x["fase"] == fase]:
            st.markdown(jogo_row(j), unsafe_allow_html=True)

def _resultado():
    camps = listar_campeonatos()
    if not camps: st.info("Nenhum campeonato."); return

    opcoes_camp = {c["nome"]: c["id"] for c in camps}
    cid = st.selectbox("Campeonato", list(opcoes_camp.keys()),
                        key="camp_result")
    cid = opcoes_camp[cid]

    jogos = listar_jogos(cid=cid, status="Agendado") + listar_jogos(cid=cid, status="Em Andamento")
    if not jogos:
        st.success("✅ Todos os jogos foram registrados!")
        return

    opcoes_j = {f"R{j['rodada_num']} · {j['equipe1']} × {j['equipe2']} [{j['fase']}]": j["id"]
                for j in jogos if j["equipe1_id"] and j["equipe2_id"]}
    if not opcoes_j:
        st.info("Nenhum jogo pendente."); return

    sel_j = st.selectbox("Jogo", list(opcoes_j.keys()))
    jid = opcoes_j[sel_j]
    jogo = get_jogo(jid)

    t1, t2 = jogo["equipe1"], jogo["equipe2"]
    tem_volta = bool(jogo.get("tem_volta"))

    st.markdown(f"""
    <div style="background:#0d1a2d;border:1px solid #1e3a5f;border-radius:8px;
         padding:14px 20px;margin:10px 0;text-align:center">
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:.65rem;
             letter-spacing:3px;color:#304050;margin-bottom:6px">
            {jogo['fase']} · {('IDA E VOLTA' if tem_volta else 'JOGO ÚNICO')}
        </div>
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.4rem;
             font-weight:800;color:#e0e6f0;letter-spacing:2px">
            {t1}  <span style="color:#304050">×</span>  {t2}
        </div>
    </div>""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 0.8, 2])
    with col1:
        st.markdown(f'<div style="font-family:Barlow Condensed,sans-serif;font-weight:800;text-align:center;color:#e0e6f0;font-size:1rem">{t1}</div>', unsafe_allow_html=True)
        p1 = st.number_input("Gols", 0, 99, 0, key="p1_r", label_visibility="collapsed")
    with col2:
        st.markdown('<div style="text-align:center;padding-top:8px;font-size:1.3rem;color:#304050">×</div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div style="font-family:Barlow Condensed,sans-serif;font-weight:800;text-align:center;color:#e0e6f0;font-size:1rem">{t2}</div>', unsafe_allow_html=True)
        p2 = st.number_input("Gols", 0, 99, 0, key="p2_r", label_visibility="collapsed")

    p1v = p2v = None
    if tem_volta:
        st.markdown('<div class="ls-label" style="margin-top:10px">Jogo de Volta</div>', unsafe_allow_html=True)
        col4, col5, col6 = st.columns([2, 0.8, 2])
        with col4:
            p2v = st.number_input(f"{t2} (casa)", 0, 99, 0, key="p2v_r")
        with col5:
            st.markdown('<div style="text-align:center;padding-top:28px;color:#304050">×</div>', unsafe_allow_html=True)
        with col6:
            p1v = st.number_input(f"{t1} (fora)", 0, 99, 0, key="p1v_r")

        agg1 = p1 + (p2v or 0)
        agg2 = p2 + (p1v or 0)
        venc = t1 if agg1 >= agg2 else t2
        st.info(f"Agregado: {t1} **{agg1}** × **{agg2}** {t2} → **{venc}** avança")

    col_d, col_l, col_a = st.columns(3)
    with col_d: data_j = st.date_input("Data", value=jogo.get("data") or date.today(), key="data_j")
    with col_l: local_j = st.text_input("Local", value=jogo.get("local") or "", key="local_j")
    with col_a: arb_j = st.text_input("Árbitro", key="arb_j")

    if st.button("⚡ CONFIRMAR RESULTADO", use_container_width=True, type="primary"):
        registrar_resultado(jid, p1, p2, p1v, p2v, local_j, arb_j)
        st.success(f"✅ {t1} {p1} × {p2} {t2}" +
                   (f" | Volta: {p2v} × {p1v}" if tem_volta and p1v is not None else ""))
        st.rerun()

def _sumula():
    camps = listar_campeonatos()
    if not camps: return
    opcoes_c = {c["nome"]: c["id"] for c in camps}
    cid = opcoes_c[st.selectbox("Campeonato", list(opcoes_c.keys()), key="camp_sum")]
    cid = opcoes_c[list(opcoes_c.keys())[list(opcoes_c.keys()).index(list(opcoes_c.keys())[0])]]
    cid = list(opcoes_c.values())[list(opcoes_c.keys()).index(st.session_state.get("camp_sum_key", list(opcoes_c.keys())[0]))]

    jogos = listar_jogos(cid=cid, status="Finalizado")
    if not jogos: st.info("Nenhum jogo finalizado."); return

    opcoes_j = {f"R{j['rodada_num']} · {j['equipe1']} {j['placar1']}×{j['placar2']} {j['equipe2']}": j["id"]
                for j in jogos}
    sel = st.selectbox("Jogo", list(opcoes_j.keys()), key="jogo_sum")
    jid = opcoes_j[sel]
    jogo = get_jogo(jid)
    eventos = eventos_jogo(jid)

    st.markdown(jogo_row(jogo), unsafe_allow_html=True)
    divider()

    # Registrar eventos
    with st.expander("➕ Adicionar Evento"):
        equipes = equipes_campeonato(cid)
        eq_opts = {e["nome"]: e["id"] for e in equipes
                   if e["id"] in [jogo["equipe1_id"], jogo["equipe2_id"]]}
        if not eq_opts: st.info("Sem equipes."); return

        tipo_ev = st.radio("Tipo", ["gol","assistencia","Amarelo","Vermelho"], horizontal=True)
        eq_sel = st.selectbox("Equipe", list(eq_opts.keys()))
        eq_id = eq_opts[eq_sel]
        jogadores = listar_jogadores(equipe_id=eq_id)

        if jogadores:
            jog_opts = {j["nome"]: j["id"] for j in jogadores}
            jog_sel = st.selectbox("Jogador", list(jog_opts.keys()))
            jog_id = jog_opts[jog_sel]
            minuto = st.number_input("Minuto", 1, 120, 1)
            motivo = st.text_input("Motivo (cartão)") if tipo_ev in ["Amarelo","Vermelho"] else None

            if st.button("Registrar Evento", type="primary"):
                adicionar_evento(jid, tipo_ev, jog_id, eq_id, minuto, motivo)
                st.success("✅ Evento registrado!")
                st.rerun()

    col1, col2, col3 = st.columns(3)
    with col1:
        section_label("⚽ Gols")
        for g in eventos.get("gols",[]):
            st.markdown(f'<div style="font-family:Rajdhani,sans-serif;font-size:.9rem;color:#c0d0e0;padding:3px 0">'
                        f'<span style="color:#00e5ff">{g["minuto"] or "?"}′</span> {g["jogador"]} '
                        f'<span style="color:#304050">({g["equipe"]})</span></div>', unsafe_allow_html=True)
    with col2:
        section_label("🎯 Assistências")
        for a in eventos.get("assistencias",[]):
            st.markdown(f'<div style="font-family:Rajdhani,sans-serif;font-size:.9rem;color:#c0d0e0;padding:3px 0">'
                        f'<span style="color:#9060ff">{a["minuto"] or "?"}′</span> {a["jogador"]}</div>',
                        unsafe_allow_html=True)
    with col3:
        section_label("🟨 Cartões")
        for c in eventos.get("cartoes",[]):
            cor_c = "#ffaa00" if c["tipo"]=="Amarelo" else "#ff5050"
            st.markdown(f'<div style="font-family:Rajdhani,sans-serif;font-size:.9rem;color:#c0d0e0;padding:3px 0">'
                        f'<span style="color:{cor_c}">■</span> {c["jogador"]} '
                        f'<span style="color:#304050">{c["minuto"] or "?"}′</span></div>',
                        unsafe_allow_html=True)
