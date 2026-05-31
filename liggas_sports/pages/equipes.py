import streamlit as st
from services.services import (listar_equipes, criar_equipe, get_equipe,
                                atualizar_equipe, deletar_equipe, listar_jogadores,
                                calcular_classificacao, listar_campeonatos)
from utils.style import page_header, divider, section_label

ESTADOS = ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG",
           "PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"]
CORES = ["#0066ff","#00e5ff","#00e564","#ff5050","#ffaa00","#9060ff",
         "#ff6b35","#e91e63","#8bc34a","#ff9800","#009688","#3f51b5"]

def render():
    page_header("👥 Equipes", "Gerencie as equipes cadastradas")
    abas = st.tabs(["📋 Listar", "➕ Nova Equipe", "📊 Perfil da Equipe"])
    with abas[0]: _listar()
    with abas[1]: _nova()
    with abas[2]: _perfil()

def _listar():
    equipes = listar_equipes()
    if not equipes:
        st.info("Nenhuma equipe cadastrada.")
        return

    busca = st.text_input("🔍 Buscar equipe", placeholder="Nome, cidade, estado...")
    if busca:
        equipes = [e for e in equipes if busca.lower() in
                   (e["nome"]+str(e["cidade"])+str(e["estado"])).lower()]

    st.metric("Total", len(equipes))
    divider()

    cols = st.columns(3)
    for i, e in enumerate(equipes):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="ls-card">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
                    <div style="width:36px;height:36px;border-radius:50%;
                         background:{e['cor']};display:flex;align-items:center;
                         justify-content:center;font-family:'Barlow Condensed',sans-serif;
                         font-weight:800;font-size:1rem;color:#000;
                         box-shadow:0 0 12px {e['cor']}60">
                        {e['nome'][:2].upper()}
                    </div>
                    <div>
                        <div class="ls-card-title">{e['nome']}</div>
                        <div class="ls-card-meta">{e['cidade'] or '—'} · {e['estado'] or '—'}</div>
                    </div>
                </div>
                <div style="font-family:Rajdhani,sans-serif;font-size:.8rem;color:#304050">
                    {e['responsavel'] or ''} {'·' if e['responsavel'] and e['telefone'] else ''} {e['telefone'] or ''}
                </div>
            </div>""", unsafe_allow_html=True)

def _nova():
    section_label("Cadastrar Nova Equipe")
    with st.form("form_equipe"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome *", placeholder="Ex: Flamengo FC")
            cidade = st.text_input("Cidade", placeholder="São Paulo")
            responsavel = st.text_input("Responsável", placeholder="João Silva")
            email = st.text_input("E-mail", placeholder="contato@equipe.com")
        with col2:
            estado = st.selectbox("Estado", [""] + ESTADOS)
            telefone = st.text_input("Telefone", placeholder="(11) 99999-9999")
            rating = st.number_input("Rating (para sorteio por potes)", 0, 99, 75)
            cor_idx = st.selectbox("Cor da equipe", range(len(CORES)),
                                    format_func=lambda i: f"Cor {i+1}")
        s = st.form_submit_button("⚡ CADASTRAR", use_container_width=True, type="primary")

    if s:
        if not nome.strip(): st.error("Informe o nome!"); return
        criar_equipe({
            "nome": nome.strip(), "cidade": cidade, "estado": estado or None,
            "responsavel": responsavel, "telefone": telefone, "email": email,
            "rating": rating, "cor": CORES[cor_idx]
        })
        st.success(f"✅ {nome} cadastrada!")

def _perfil():
    equipes = listar_equipes()
    if not equipes:
        st.info("Nenhuma equipe cadastrada.")
        return

    opcoes = {e["nome"]: e["id"] for e in equipes}
    sel = st.selectbox("Equipe", list(opcoes.keys()))
    eid = opcoes[sel]
    e = get_equipe(eid)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"""
        <div style="background:#0d1a2d;border:1px solid #1e3a5f;border-radius:10px;padding:20px;text-align:center">
            <div style="width:70px;height:70px;border-radius:50%;background:{e['cor']};
                 margin:0 auto 12px;display:flex;align-items:center;justify-content:center;
                 font-family:'Barlow Condensed',sans-serif;font-weight:800;font-size:1.6rem;
                 color:#000;box-shadow:0 0 20px {e['cor']}60">{e['nome'][:2].upper()}</div>
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.2rem;
                 font-weight:800;color:#fff;letter-spacing:1px">{e['nome'].upper()}</div>
            <div style="font-family:Rajdhani,sans-serif;font-size:.85rem;color:#506070">
                {e['cidade'] or '—'} · {e['estado'] or '—'}</div>
            <div style="margin-top:10px;font-family:'Barlow Condensed',sans-serif;
                 font-size:1.5rem;font-weight:800;color:#ffaa00">⭐ {e['rating']}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        jogadores = listar_jogadores(equipe_id=eid)
        st.metric("Jogadores", len(jogadores))
        if jogadores:
            section_label("Elenco")
            for j in jogadores:
                pos = j["posicao"] or "—"
                num = f"#{j['numero']}" if j["numero"] else ""
                st.markdown(
                    f'<div style="font-family:Rajdhani,sans-serif;font-size:.9rem;'
                    f'color:#a0b0c0;padding:3px 0;border-bottom:1px solid #0d1a2d">'
                    f'<span style="color:#304050;margin-right:8px">{num}</span>'
                    f'{j["nome"]} <span style="color:#304050;font-size:.75rem">· {pos}</span></div>',
                    unsafe_allow_html=True)

    divider()

    # Editar
    with st.expander("✏️ Editar Equipe"):
        with st.form("form_edit_eq"):
            col1, col2 = st.columns(2)
            with col1:
                nome_e = st.text_input("Nome", value=e["nome"])
                cidade_e = st.text_input("Cidade", value=e["cidade"] or "")
                responsavel_e = st.text_input("Responsável", value=e["responsavel"] or "")
            with col2:
                estado_e = st.selectbox("Estado", [""] + ESTADOS,
                    index=(ESTADOS.index(e["estado"])+1) if e["estado"] in ESTADOS else 0)
                telefone_e = st.text_input("Telefone", value=e["telefone"] or "")
                rating_e = st.number_input("Rating", 0, 99, int(e["rating"] or 75))
            s = st.form_submit_button("💾 SALVAR", use_container_width=True, type="primary")
        if s:
            atualizar_equipe(eid, {"nome":nome_e,"cidade":cidade_e,"estado":estado_e or None,
                                    "responsavel":responsavel_e,"telefone":telefone_e,"rating":rating_e})
            st.success("✅ Atualizado!")

    with st.expander("🗑️ Excluir Equipe"):
        if st.button("EXCLUIR PERMANENTEMENTE", type="secondary"):
            deletar_equipe(eid)
            st.success("Equipe excluída.")
            st.rerun()
