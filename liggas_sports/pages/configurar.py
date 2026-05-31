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
        n_t = len(cfg.get("times", []))
        fmt = cfg.get("formato","")
        n_g = cfg.get("n_grupos",1)
        cpg = cfg.get("classificados_por_grupo",2)
        st.markdown(f"""
        <div style="background:#0d1a2d;border:1px solid #1e3a5f;border-radius:8px;
             padding:12px 16px;margin-bottom:12px">
            <div style="font-family:'Barlow Condensed',sans-serif;font-weight:800;
                 font-size:1rem;color:#fff">{cfg.get('nome','—')}</div>
            <div style="font-family:Rajdhani,sans-serif;font-size:.85rem;color:#506070">
                {fmt} · {n_t} times
                {f' · {n_g} grupo(s) · {cpg} classificado(s)/grupo' if 'Grupo' in fmt or 'Chaves' in fmt or 'Mata-Mata' in fmt else ''}
            </div>
        </div>""", unsafe_allow_html=True)
        if st.button("🔄 RESETAR E CRIAR NOVO", type="secondary"):
            engine.reset()
            st.rerun()
        style.div(st)

    tab1, tab2 = st.tabs(["⚙️ Novo Campeonato", "👥 Times & Jogadores"])
    with tab1: _form_campeonato()
    with tab2:
        if not tem_camp: st.info("Configure um campeonato primeiro.")
        else: _times_jogadores()


def _form_campeonato():
    # Passo 1: nome + formato + lista de times (fora do form para preview dinâmico)
    st.markdown('<div class="ifc-lbl">1 — NOME E FORMATO</div>', unsafe_allow_html=True)
    col_n, col_f = st.columns([2, 1])
    with col_n:
        nome = st.text_input("Nome do Campeonato *", placeholder="Copa do Bairro 2025",
                              key="cfg_nome")
    with col_f:
        formato = st.selectbox("Formato", FORMATOS, key="cfg_fmt")

    style.div(st)
    st.markdown('<div class="ifc-lbl">2 — TIMES (um por linha)</div>', unsafe_allow_html=True)
    preset = st.selectbox("Usar times sugeridos", list(TIMES_SUGERIDOS.keys()), key="cfg_preset")
    times_txt = st.text_area("Times",
        value="\n".join(TIMES_SUGERIDOS[preset]),
        height=180, label_visibility="collapsed", key="cfg_times")

    times_raw = [t.strip() for t in times_txt.splitlines() if t.strip()]
    n_times = len(times_raw)

    style.div(st)
    st.markdown('<div class="ifc-lbl">3 — CONFIGURAÇÕES DO FORMATO</div>', unsafe_allow_html=True)

    # Opções variam por formato
    tem_grupos = formato in ("Grupos", "Chaves Cruzadas", "Pontos Corridos + Mata-Mata")

    col1, col2, col3 = st.columns(3)

    with col1:
        ida_volta = st.checkbox("Ida e volta (pontos corridos)", value=True,
            disabled=formato == "Eliminatórias",
            key="cfg_iv")
        ida_volta_grupos = st.checkbox("Ida e volta nos grupos", value=False,
            disabled=not tem_grupos,
            key="cfg_ivg")
        ida_volta_mata = st.checkbox("Ida e volta no mata-mata", value=False,
            disabled=formato == "Pontos Corridos",
            key="cfg_ivm")

    with col2:
        if tem_grupos and n_times >= 2:
            # Número de grupos: mínimo 1, máximo n_times // 2
            max_grupos = max(1, n_times // 2)
            n_grupos = st.number_input(
                f"Nº de grupos (1 a {max_grupos})",
                min_value=1, max_value=max_grupos,
                value=min(4, max_grupos),
                key="cfg_ng"
            )
            n_grupos = int(n_grupos)

            # Classificados por grupo: mínimo 1, máximo times por grupo - 1
            tpg = n_times // n_grupos if n_grupos > 0 else n_times
            max_class = max(1, tpg - 1) if tpg > 1 else 1
            class_grupo = st.number_input(
                f"Classificados/grupo (1 a {max_class})",
                min_value=1, max_value=max_class,
                value=min(2, max_class),
                key="cfg_cpg"
            )
            class_grupo = int(class_grupo)

            # Preview dinâmico
            total_class = n_grupos * class_grupo
            st.markdown(f"""
            <div style="background:#0d1a2d;border:1px solid #1e3a5f;border-radius:6px;
                 padding:8px 12px;margin-top:6px">
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:.62rem;
                     letter-spacing:2px;color:#506070">PREVIEW</div>
                <div style="font-family:Rajdhani,sans-serif;font-size:.88rem;color:#c0d0e0">
                    {n_times} times → {n_grupos} grupo(s)<br>
                    ~{n_times // n_grupos if n_grupos else n_times} por grupo<br>
                    {total_class} times pro mata-mata
                    {'<span style="color:#ffaa00"> (arredondado p/ pot. de 2)</span>' if (total_class & (total_class-1)) != 0 and total_class > 1 else ''}
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            n_grupos = 1
            class_grupo = n_times - 1 if n_times > 1 else 1
            if tem_grupos:
                st.info("Insira os times para ver as opções de grupos.")

    with col3:
        tipo_sorteio = st.radio(
            "Sorteio dos grupos",
            ["aleatorio", "potes"],
            format_func=lambda x: "🎲 Aleatório" if x == "aleatorio" else "🎯 Por potes (rating)",
            disabled=not tem_grupos,
            key="cfg_sorteio"
        )

    style.div(st)

    # Botão fora do form para aproveitar o estado dinâmico
    if st.button("⚡ CRIAR CAMPEONATO", use_container_width=True, type="primary"):
        if not nome.strip():
            st.error("Informe o nome!"); return
        if n_times < 2:
            st.error("Informe pelo menos 2 times!"); return
        if tem_grupos and n_grupos > 0 and n_times < n_grupos * 2:
            st.error(f"Com {n_grupos} grupo(s) você precisa de pelo menos {n_grupos*2} times!"); return

        times = [{"nome": t, "rating": 50} for t in times_raw]
        engine.configurar({
            "nome": nome.strip(),
            "formato": formato,
            "ida_volta": ida_volta,
            "ida_volta_grupos": ida_volta_grupos,
            "ida_volta_mata": ida_volta_mata,
            "n_grupos": n_grupos,
            "classificados_por_grupo": class_grupo,
            "tipo_sorteio": tipo_sorteio,
            "times": times,
        })
        ok = engine.gerar_tabela()
        st.success(f"✅ **{nome}** criado! {n_times} times · {formato}" +
                   (f" · {n_grupos} grupo(s) · {class_grupo} classificado(s)/grupo" if tem_grupos else ""))
        st.rerun()


def _times_jogadores():
    times  = engine.get_times()
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
                st.markdown(
                    f'<div style="font-family:Rajdhani,sans-serif;font-weight:700;'
                    f'color:#c0d0e0;padding-top:6px">{t["nome"]}</div>',
                    unsafe_allow_html=True)
            with c2:
                r = st.number_input("Rating", 0, 99, int(t.get("rating", 50)),
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
                with c3: pos_j   = st.selectbox("Posição", POSICOES)
                num_j = st.number_input("Número", 0, 99, 0)
                s = st.form_submit_button("➕ CADASTRAR", use_container_width=True, type="primary")
            if s and nome_j.strip():
                engine.salvar_jogador({
                    "nome": nome_j.strip(), "equipe": equipe_j,
                    "posicao": pos_j, "numero": int(num_j),
                    "gols": 0, "assist": 0, "amarelos": 0, "vermelhos": 0
                })
                st.success(f"✅ {nome_j} cadastrado!")
                st.rerun()

        if jogadores:
            style.lbl(st, f"{len(jogadores)} jogadores cadastrados")
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
