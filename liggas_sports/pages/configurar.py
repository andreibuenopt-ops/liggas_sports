import streamlit as st
from core import engine, style

FORMATOS = [
    "Pontos Corridos",
    "Grupos",
    "Chaves Cruzadas",
    "Pontos Corridos + Mata-Mata",
    "Eliminatórias",
]

TIMES_SUGERIDOS = {
    "Seleções Copa do Mundo": [
        "Brasil","Argentina","França","Alemanha","Espanha","Inglaterra",
        "Portugal","Holanda","Bélgica","Croácia","Uruguai","Estados Unidos",
        "Japão","Marrocos","Senegal","México"
    ],
    "Times Brasileiros": [
        "Flamengo","Palmeiras","Corinthians","São Paulo","Santos","Grêmio",
        "Internacional","Fluminense","Athletico-PR","Atlético-MG","Cruzeiro","Botafogo"
    ],
    "Times Europeus": [
        "Real Madrid","Barcelona","Manchester City","Liverpool","Bayern","PSG",
        "Inter Milão","Juventus","Chelsea","Arsenal","Benfica","Porto"
    ],
    "Em branco": []
}

def render():
    style.h1(st, "⚙️ Configurar Campeonato", "Defina o formato e cadastre os times")

    cfg = engine.get_config()
    tem_camp = bool(cfg)

    if tem_camp:
        st.markdown(f"""
        <div style="background:#0d1a2d;border:1px solid #1e3a5f;border-radius:8px;
             padding:12px 16px;margin-bottom:12px">
            <div style="font-family:'Barlow Condensed',sans-serif;font-weight:800;
                 font-size:1rem;color:#fff">{cfg.get('nome','—')}</div>
            <div style="font-family:Rajdhani,sans-serif;font-size:.85rem;color:#506070">
                {cfg.get('formato','—')} · {len(cfg.get('times',[]))} times
            </div>
        </div>""", unsafe_allow_html=True)
        if st.button("🔄 RESETAR E CRIAR NOVO", type="secondary"):
            engine.reset()
            st.rerun()
        style.div(st)

    tab1, tab2 = st.tabs(["⚙️ Novo Campeonato", "👥 Times & Jogadores"])

    with tab1:
        _form_campeonato()

    with tab2:
        if not tem_camp:
            st.info("Configure um campeonato primeiro.")
        else:
            _times_jogadores()

def _form_campeonato():
    with st.form("form_cfg"):
        nome = st.text_input("Nome do Campeonato *", placeholder="Copa do Bairro 2025")
        formato = st.selectbox("Formato", FORMATOS)

        style.div(st)
        style.lbl(st, "Opções do formato")
        col1, col2, col3 = st.columns(3)
        with col1:
            ida_volta = st.checkbox("Ida e volta (liga)", value=True,
                disabled=formato == "Eliminatórias")
            ida_volta_mata = st.checkbox("Ida e volta (mata-mata)", value=False,
                disabled=formato == "Pontos Corridos")
        with col2:
            n_grupos = st.number_input("Nº de grupos", 2, 16, 4,
                disabled=formato not in ("Grupos","Chaves Cruzadas","Pontos Corridos + Mata-Mata"))
            class_grupo = st.number_input("Classificados/grupo", 1, 4, 2,
                disabled=formato not in ("Grupos","Chaves Cruzadas","Pontos Corridos + Mata-Mata"))
        with col3:
            tipo_sorteio = st.radio("Sorteio", ["aleatorio","potes"],
                format_func=lambda x: "🎲 Aleatório" if x=="aleatorio" else "🎯 Por potes (rating)")

        style.div(st)
        style.lbl(st, "Times — cole a lista (um por linha)")
        preset = st.selectbox("Usar times sugeridos", list(TIMES_SUGERIDOS.keys()))
        times_txt = st.text_area("Times",
            value="\n".join(TIMES_SUGERIDOS[preset]),
            height=220, label_visibility="collapsed")

        style.div(st)
        submitted = st.form_submit_button("⚡ CRIAR CAMPEONATO", use_container_width=True, type="primary")

    if submitted:
        if not nome.strip():
            st.error("Informe o nome!"); return
        times_raw = [t.strip() for t in times_txt.splitlines() if t.strip()]
        if len(times_raw) < 2:
            st.error("Informe pelo menos 2 times!"); return

        times = [{"nome": t, "rating": 50} for t in times_raw]
        engine.configurar({
            "nome": nome.strip(), "formato": formato,
            "ida_volta": ida_volta, "ida_volta_mata": ida_volta_mata,
            "n_grupos": int(n_grupos), "classificados_por_grupo": int(class_grupo),
            "tipo_sorteio": tipo_sorteio, "times": times,
        })

        ok = engine.gerar_tabela()
        st.success(f"✅ {nome} criado! {len(times_raw)} times, formato {formato}.")
        st.rerun()

def _times_jogadores():
    times = engine.get_times()
    jogadores = engine.get_jogadores()
    
    col1, col2 = st.columns(2)
    col1.metric("Times", len(times))
    col2.metric("Jogadores", len(jogadores))

    style.div(st)
    tab_t, tab_j = st.tabs(["⚙️ Times / Rating", "👤 Jogadores"])

    with tab_t:
        style.lbl(st, "Editar ratings (usado no sorteio por potes)")
        times_novo = []
        for t in times:
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f'<div style="font-family:Rajdhani,sans-serif;font-weight:700;color:#c0d0e0;padding-top:6px">{t["nome"]}</div>', unsafe_allow_html=True)
            with c2:
                r = st.number_input("Rating", 0, 99, int(t.get("rating",50)),
                                     key=f"rat_{t['nome']}", label_visibility="collapsed")
            times_novo.append({"nome": t["nome"], "rating": r})
        if st.button("💾 SALVAR RATINGS", use_container_width=True):
            engine.salvar_times(times_novo)
            st.success("✅ Salvo!")

    with tab_j:
        POSICOES = ["Goleiro","Zagueiro","Lateral","Volante","Meia","Atacante","Outro"]
        nomes_times = [t["nome"] for t in times]

        with st.expander("➕ Cadastrar Jogador"):
            with st.form("form_jog"):
                c1, c2, c3 = st.columns(3)
                with c1: nome_j = st.text_input("Nome *")
                with c2: equipe_j = st.selectbox("Equipe", nomes_times)
                with c3: pos_j = st.selectbox("Posição", POSICOES)
                num_j = st.number_input("Número", 0, 99, 0)
                s = st.form_submit_button("➕ CADASTRAR", use_container_width=True, type="primary")
            if s and nome_j.strip():
                engine.salvar_jogador({"nome": nome_j.strip(), "equipe": equipe_j,
                                        "posicao": pos_j, "numero": int(num_j),
                                        "gols": 0, "assist": 0, "amarelos": 0, "vermelhos": 0})
                st.success(f"✅ {nome_j} cadastrado!"); st.rerun()

        if jogadores:
            style.lbl(st, f"{len(jogadores)} jogadores")
            for j in jogadores:
                c1, c2 = st.columns([5, 1])
                with c1:
                    st.markdown(
                        f'<div style="font-family:Rajdhani,sans-serif;color:#a0b0c0;padding:3px 0">'
                        f'<b>{j["nome"]}</b> · {j.get("equipe","?")} · {j.get("posicao","—")}'
                        f'{" · #"+str(j["numero"]) if j.get("numero") else ""}</div>',
                        unsafe_allow_html=True)
                with c2:
                    if st.button("✕", key=f"dj_{j['id']}"):
                        engine.deletar_jogador(j["id"]); st.rerun()
