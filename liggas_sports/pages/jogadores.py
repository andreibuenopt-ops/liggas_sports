import streamlit as st
from datetime import date
from services.services import (listar_jogadores, criar_jogador, get_jogador,
                                atualizar_jogador, deletar_jogador, listar_equipes)
from utils.style import page_header, divider, section_label

POSICOES = ["Goleiro","Lateral Direito","Lateral Esquerdo","Zagueiro","Volante",
            "Meio-campo","Meia Atacante","Ponta Direita","Ponta Esquerda","Centroavante","Outro"]

def render():
    page_header("🧑‍🤝‍🧑 Jogadores", "Gerencie o cadastro de jogadores")
    abas = st.tabs(["📋 Listar", "➕ Novo", "📊 Perfil"])
    with abas[0]: _listar()
    with abas[1]: _novo()
    with abas[2]: _perfil()

def _listar():
    equipes = listar_equipes()
    opcoes_eq = {"Todas": None} | {e["nome"]: e["id"] for e in equipes}
    sel_eq = st.selectbox("Filtrar por Equipe", list(opcoes_eq.keys()))
    eid = opcoes_eq[sel_eq]

    jogadores = listar_jogadores(equipe_id=eid)
    busca = st.text_input("🔍 Buscar", placeholder="Nome do jogador...")
    if busca:
        jogadores = [j for j in jogadores if busca.lower() in j["nome"].lower()]

    eq_map = {e["id"]: e for e in equipes}
    st.metric("Total", len(jogadores))
    divider()

    for j in jogadores:
        eq = eq_map.get(j["equipe_id"], {})
        cor = eq.get("cor","#0066ff")
        pos = j["posicao"] or "—"
        num = f"#{j['numero']}" if j["numero"] else ""
        st.markdown(f"""
        <div class="ls-card" style="padding:.7rem 1.2rem">
            <div style="display:flex;align-items:center;gap:12px">
                <div style="width:32px;height:32px;border-radius:50%;background:{cor};
                     display:flex;align-items:center;justify-content:center;
                     font-family:'Barlow Condensed',sans-serif;font-weight:800;
                     font-size:.85rem;color:#000">{j['nome'][:2].upper()}</div>
                <div>
                    <div class="ls-card-title">{j['nome']} <span style="color:#304050;font-weight:400">{num}</span></div>
                    <div class="ls-card-meta">{eq.get('nome','?')} · {pos}</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

def _novo():
    equipes = listar_equipes()
    if not equipes:
        st.warning("Cadastre equipes antes de cadastrar jogadores.")
        return

    section_label("Cadastrar Jogador")
    with st.form("form_jogador"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome *", placeholder="João da Silva")
            posicao = st.selectbox("Posição", [""] + POSICOES)
            data_nasc = st.date_input("Data de Nascimento", value=date(2000,1,1))
            telefone = st.text_input("Telefone")
        with col2:
            equipe_id = st.selectbox("Equipe *", [e["id"] for e in equipes],
                                      format_func=lambda i: next(e["nome"] for e in equipes if e["id"]==i))
            numero = st.number_input("Número da Camisa", 0, 99, 0)
            email = st.text_input("E-mail")

        s = st.form_submit_button("⚡ CADASTRAR", use_container_width=True, type="primary")

    if s:
        if not nome.strip(): st.error("Informe o nome!"); return
        criar_jogador({
            "nome": nome.strip(), "posicao": posicao or None,
            "data_nascimento": data_nasc, "numero": numero or None,
            "telefone": telefone, "email": email, "equipe_id": equipe_id
        })
        st.success(f"✅ {nome} cadastrado!")

def _perfil():
    jogadores = listar_jogadores()
    if not jogadores:
        st.info("Nenhum jogador cadastrado.")
        return

    equipes = listar_equipes()
    eq_map = {e["id"]: e for e in equipes}

    opcoes = {j["nome"]: j["id"] for j in jogadores}
    sel = st.selectbox("Jogador", list(opcoes.keys()))
    jid = opcoes[sel]
    j = get_jogador(jid)
    eq = eq_map.get(j["equipe_id"], {})

    col1, col2 = st.columns([1, 2])
    with col1:
        cor = eq.get("cor","#0066ff")
        st.markdown(f"""
        <div style="background:#0d1a2d;border:1px solid #1e3a5f;border-radius:10px;
             padding:20px;text-align:center">
            <div style="width:64px;height:64px;border-radius:50%;background:{cor};
                 margin:0 auto 10px;display:flex;align-items:center;justify-content:center;
                 font-family:'Barlow Condensed',sans-serif;font-weight:800;font-size:1.4rem;
                 color:#000;box-shadow:0 0 16px {cor}60">{j['nome'][:2].upper()}</div>
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.1rem;
                 font-weight:800;color:#fff">{j['nome'].upper()}</div>
            <div style="font-family:Rajdhani,sans-serif;color:#506070;font-size:.85rem">
                {eq.get('nome','?')} · {j['posicao'] or '—'}</div>
            {'<div style="font-family:Barlow Condensed,sans-serif;font-size:2rem;font-weight:800;color:#00e5ff;margin-top:8px">#' + str(j['numero']) + '</div>' if j['numero'] else ''}
        </div>""", unsafe_allow_html=True)

    with col2:
        section_label("Informações")
        info = {
            "Data de Nascimento": str(j["data_nascimento"]) if j["data_nascimento"] else "—",
            "Telefone": j["telefone"] or "—",
            "E-mail": j["email"] or "—",
            "Status": "Ativo" if j["ativo"] else "Inativo",
        }
        for k, v in info.items():
            st.markdown(f'<div style="font-family:Rajdhani,sans-serif;padding:5px 0;'
                        f'border-bottom:1px solid #0d1a2d">'
                        f'<span style="color:#405060;font-size:.8rem">{k}: </span>'
                        f'<span style="color:#c0d0e0">{v}</span></div>',
                        unsafe_allow_html=True)

    divider()
    with st.expander("✏️ Editar"):
        with st.form("form_edit_jog"):
            col1, col2 = st.columns(2)
            with col1:
                nome_e = st.text_input("Nome", value=j["nome"])
                pos_e = st.selectbox("Posição", [""] + POSICOES,
                    index=(POSICOES.index(j["posicao"])+1) if j["posicao"] in POSICOES else 0)
            with col2:
                num_e = st.number_input("Número", 0, 99, int(j["numero"] or 0))
                ativo_e = st.checkbox("Ativo", value=bool(j["ativo"]))
            s = st.form_submit_button("💾 SALVAR", type="primary", use_container_width=True)
        if s:
            atualizar_jogador(jid, {"nome":nome_e,"posicao":pos_e or None,
                                     "numero":num_e or None,"ativo":ativo_e})
            st.success("✅ Atualizado!")
