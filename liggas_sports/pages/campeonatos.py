import streamlit as st
from datetime import date
from services.services import (listar_campeonatos, criar_campeonato, get_campeonato,
                                atualizar_campeonato, deletar_campeonato,
                                equipes_campeonato, listar_equipes,
                                adicionar_equipe_campeonato, remover_equipe_campeonato,
                                gerar_tabela, gerar_proxima_fase_mata,
                                gerar_mata_mata_classificados)
from utils.style import page_header, divider, section_label, badge

FORMATOS = ["Liga","Mata-Mata","Fase de Grupos","Grupos + Mata-Mata","Pontos Corridos"]

def render():
    page_header("🏆 Campeonatos", "Gerencie todos os campeonatos")

    aba = st.tabs(["📋 Listar", "➕ Novo", "⚙️ Gerenciar"])

    with aba[0]: _listar()
    with aba[1]: _novo()
    with aba[2]: _gerenciar()

def _listar():
    camps = listar_campeonatos()
    if not camps:
        st.info("Nenhum campeonato cadastrado.")
        return

    filtro = st.radio("Filtrar", ["Todos","Ativo","Encerrado"], horizontal=True)
    if filtro != "Todos":
        camps = [c for c in camps if c["status"] == filtro.lower()]

    for c in camps:
        fmt_badge = c["formato"].lower().split()[0]
        st.markdown(f"""
        <div class="ls-card">
            <div class="ls-card-title">{c['nome']}</div>
            <div class="ls-card-meta">
                {badge(c['formato'], 'grupos' if 'Grupo' in c['formato'] else ('mata' if 'Mata' in c['formato'] else 'liga'))}
                {badge(c['status'].upper(), c['status'])}
                <span style="margin-left:6px;font-size:.72rem;color:#304050">
                    {str(c['data_inicio']) if c['data_inicio'] else 'Sem data'}
                </span>
            </div>
        </div>""", unsafe_allow_html=True)

def _novo():
    section_label("Novo Campeonato")
    with st.form("form_camp"):
        nome = st.text_input("Nome *", placeholder="Copa da Firma 2025")
        descricao = st.text_area("Descrição", height=80)
        regulamento = st.text_area("Regulamento", height=100)

        col1, col2 = st.columns(2)
        with col1:
            formato = st.selectbox("Formato", FORMATOS)
            data_inicio = st.date_input("Data Início", value=date.today())
        with col2:
            status = st.selectbox("Status", ["ativo","encerrado"])
            data_fim = st.date_input("Data Fim")

        divider()
        st.markdown('<div class="ls-label">Configurações da Tabela</div>', unsafe_allow_html=True)
        col3, col4, col5 = st.columns(3)
        with col3:
            n_grupos = st.number_input("Nº Grupos", 2, 16, 4, disabled="Grupo" not in formato and "Grupos" not in formato)
            class_grupo = st.number_input("Classificados/grupo", 1, 4, 2, disabled="Grupo" not in formato and "Grupos" not in formato)
        with col4:
            ida_volta = st.checkbox("Ida e volta (Liga)", value=True)
            ida_volta_mata = st.checkbox("Ida e volta (Mata-Mata)")
        with col5:
            tipo_sorteio = st.radio("Sorteio", ["potes","aleatorio"])

        submitted = st.form_submit_button("⚡ CRIAR CAMPEONATO", use_container_width=True, type="primary")

    if submitted:
        if not nome.strip():
            st.error("Informe o nome!"); return
        cid = criar_campeonato({
            "nome": nome.strip(), "descricao": descricao, "regulamento": regulamento,
            "formato": formato, "status": status,
            "data_inicio": data_inicio, "data_fim": data_fim,
            "n_grupos": n_grupos, "classificados_por_grupo": class_grupo,
            "ida_volta": ida_volta, "ida_volta_mata": ida_volta_mata,
            "tipo_sorteio": tipo_sorteio,
        })
        st.success(f"✅ Campeonato criado! (ID {cid})")

def _gerenciar():
    camps = listar_campeonatos()
    if not camps:
        st.info("Nenhum campeonato cadastrado.")
        return

    opcoes = {f"{c['nome']} [{c['formato']}]": c["id"] for c in camps}
    sel = st.selectbox("Selecionar", list(opcoes.keys()))
    cid = opcoes[sel]
    camp = get_campeonato(cid)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📝 Editar", "👥 Equipes", "🎲 Gerar Tabela", "⏭️ Avançar Fase", "🗑️ Excluir"])

    with tab1: _editar(cid, camp)
    with tab2: _equipes(cid)
    with tab3: _gerar_tabela(cid, camp)
    with tab4: _avancar_fase(cid, camp)
    with tab5: _excluir(cid, camp)

def _editar(cid, camp):
    with st.form("form_edit_camp"):
        nome = st.text_input("Nome", value=camp["nome"] or "")
        descricao = st.text_area("Descrição", value=camp["descricao"] or "", height=80)
        col1, col2 = st.columns(2)
        with col1:
            status = st.selectbox("Status", ["ativo","encerrado"],
                                   index=0 if camp["status"]=="ativo" else 1)
        with col2:
            formato = st.selectbox("Formato", FORMATOS,
                                    index=FORMATOS.index(camp["formato"]) if camp["formato"] in FORMATOS else 0)
        s = st.form_submit_button("💾 SALVAR", use_container_width=True, type="primary")
    if s:
        atualizar_campeonato(cid, {"nome":nome,"descricao":descricao,"status":status,"formato":formato})
        st.success("✅ Atualizado!")

def _equipes(cid):
    todas = listar_equipes()
    inscritas = equipes_campeonato(cid)
    inscritas_ids = {e["id"] for e in inscritas}

    col1, col2 = st.columns(2)
    with col1:
        section_label(f"Equipes Inscritas ({len(inscritas)})")
        for e in inscritas:
            c1, c2_ = st.columns([4,1])
            with c1:
                grupo_tag = f' <span style="color:#304050;font-size:.75rem">Grupo {e["grupo"]}</span>' if e.get("grupo") else ""
                st.markdown(f'<div style="font-family:Rajdhani,sans-serif;font-weight:700;color:#c0d0e0;padding:4px 0">'
                            f'<span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:{e["cor"]};margin-right:6px"></span>'
                            f'{e["nome"]}{grupo_tag}</div>', unsafe_allow_html=True)
            with c2_:
                if st.button("✕", key=f"rem_{e['id']}", help="Remover"):
                    remover_equipe_campeonato(cid, e["id"])
                    st.rerun()

    with col2:
        section_label("Adicionar Equipe")
        disponiveis = [e for e in todas if e["id"] not in inscritas_ids]
        if disponiveis:
            opcoes_eq = {e["nome"]: e["id"] for e in disponiveis}
            sel_eq = st.selectbox("Equipe", list(opcoes_eq.keys()))
            if st.button("➕ Adicionar", use_container_width=True, type="primary"):
                adicionar_equipe_campeonato(cid, opcoes_eq[sel_eq])
                st.rerun()
        else:
            st.info("Todas as equipes já estão inscritas.")

def _gerar_tabela(cid, camp):
    st.markdown(f"""
    <div style="background:#0d1a2d;border:1px solid #1e3a5f;border-radius:6px;padding:12px 16px;margin-bottom:12px">
        <div style="font-family:'Barlow Condensed',sans-serif;color:#506070;font-size:.7rem;letter-spacing:2px;text-transform:uppercase">Formato</div>
        <div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:1rem;color:#e0e6f0">{camp['formato']}</div>
        <div style="font-family:Rajdhani,sans-serif;font-size:.85rem;color:#506070">
            {'Ida e volta ·' if camp['ida_volta'] else ''} 
            {f'{camp["n_grupos"]} grupos · {camp["classificados_por_grupo"]} classificados' if 'Grupo' in camp['formato'] else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)

    eqs = equipes_campeonato(cid)
    st.metric("Equipes inscritas", len(eqs))

    if len(eqs) < 2:
        st.warning("Inscreva pelo menos 2 equipes antes de gerar a tabela.")
        return

    if st.button("⚡ GERAR / RESETAR TABELA", use_container_width=True, type="primary"):
        ok, msg = gerar_tabela(cid)
        st.success(msg) if ok else st.error(msg)

def _avancar_fase(cid, camp):
    fmt = camp["formato"]
    if fmt in ("Liga","Pontos Corridos"):
        st.info("Liga não tem fases para avançar.")
        return

    if "Grupo" in fmt or fmt == "Grupos + Mata-Mata":
        st.markdown('<div class="ls-label">Gerar Mata-Mata com Classificados dos Grupos</div>', unsafe_allow_html=True)
        if st.button("⏭️ GERAR MATA-MATA COM CLASSIFICADOS", use_container_width=True, type="primary"):
            ok, msg = gerar_mata_mata_classificados(cid)
            st.success(msg) if ok else st.warning(msg)
        divider()

    st.markdown('<div class="ls-label">Avançar Fase do Mata-Mata</div>', unsafe_allow_html=True)
    if st.button("⏭️ AVANÇAR FASE", use_container_width=True):
        ok, msg = gerar_proxima_fase_mata(cid)
        st.success(msg) if ok else st.warning(msg)

def _excluir(cid, camp):
    st.warning(f"⚠️ Isso excluirá **{camp['nome']}** e todos os dados relacionados permanentemente.")
    confirmar = st.text_input("Digite o nome do campeonato para confirmar:")
    if st.button("🗑️ EXCLUIR PERMANENTEMENTE", type="secondary"):
        if confirmar == camp["nome"]:
            deletar_campeonato(cid)
            st.success("Campeonato excluído.")
            st.rerun()
        else:
            st.error("Nome incorreto.")
