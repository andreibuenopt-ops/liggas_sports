import streamlit as st
import random
from utils.database import (
    listar_jogadores, adicionar_jogador, deletar_jogador,
    adicionar_jogadores_em_lote, listar_times, atribuir_time_jogador,
    limpar_times_jogadores, get_campeonato
)

def render(campeonato_id):
    camp = get_campeonato(campeonato_id)
    st.markdown('<div class="xt-page-title">👥 Jogadores</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="xt-page-sub">{camp["nome"]}</div>', unsafe_allow_html=True)

    times    = listar_times(campeonato_id)
    jogadores = listar_jogadores(campeonato_id)
    sem_time  = sum(1 for j in jogadores if not j["time_id"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Jogadores", len(jogadores))
    col2.metric("Times", len(times))
    col3.metric("Sem Time", sem_time)

    st.markdown("<hr class='xt-divider'>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["➕ Cadastrar", "🎲 Sortear", "📋 Por Time"])

    # ── Cadastrar ─────────────────────────────────────────────
    with tab1:
        modo = st.radio("Modo", ["📝 Um por vez", "📋 Lista (vários de uma vez)"],
                        horizontal=True, label_visibility="collapsed")

        if modo == "📝 Um por vez":
            with st.form("form_jog_unico"):
                nome = st.text_input("Nome", placeholder="Ex: João Silva")
                s = st.form_submit_button("➕ ADICIONAR", use_container_width=True, type="primary")
            if s:
                if nome.strip():
                    adicionar_jogador(campeonato_id, nome.strip())
                    st.success(f"✅ {nome.strip()} adicionado!")
                    st.rerun()
                else:
                    st.error("Informe o nome!")
        else:
            st.markdown('<div class="xt-section-label">Um nome por linha</div>', unsafe_allow_html=True)
            with st.form("form_jog_lote"):
                lista_txt = st.text_area("Nomes",
                    placeholder="João Silva\nMaria Souza\nPedro Lima\n...",
                    height=180, label_visibility="collapsed")
                s = st.form_submit_button("➕ ADICIONAR TODOS", use_container_width=True, type="primary")
            if s:
                nomes = [n.strip() for n in lista_txt.splitlines() if n.strip()]
                if nomes:
                    adicionar_jogadores_em_lote(campeonato_id, nomes)
                    st.success(f"✅ {len(nomes)} jogador(es) adicionado(s)!")
                    st.rerun()
                else:
                    st.error("Lista vazia!")

        if jogadores:
            st.markdown("<hr class='xt-divider'>", unsafe_allow_html=True)
            st.markdown(f'<div class="xt-section-label">{len(jogadores)} cadastrado(s)</div>', unsafe_allow_html=True)
            for j in jogadores:
                c1, c2 = st.columns([5, 1])
                with c1:
                    time_tag = ""
                    if j["time_nome"]:
                        cor = j["time_cor"] or "#0066ff"
                        time_tag = (f' <span style="background:{cor}20;color:{cor};'
                                    f'border:1px solid {cor}40;border-radius:3px;'
                                    f'padding:1px 7px;font-size:0.7rem;'
                                    f'font-family:Barlow Condensed,sans-serif;'
                                    f'letter-spacing:1px;font-weight:700">'
                                    f'{j["time_nome"]}</span>')
                    st.markdown(
                        f'<div style="font-family:Rajdhani,sans-serif;font-size:0.9rem;'
                        f'color:#a0b0c0;padding-top:4px">{j["nome"]}{time_tag}</div>',
                        unsafe_allow_html=True
                    )
                with c2:
                    if st.button("✕", key=f"dj_{j['id']}"):
                        deletar_jogador(j["id"])
                        st.rerun()

    # ── Sortear ───────────────────────────────────────────────
    with tab2:
        if not times:
            st.warning("⚠️ Cadastre times primeiro na aba **⚙️ Times**.")
        elif not jogadores:
            st.warning("⚠️ Cadastre jogadores na aba **➕ Cadastrar**.")
        else:
            por_time = len(jogadores) // len(times)
            st.markdown(f"""
            <div style="background:#0d1a2d;border:1px solid #1e3a5f;border-radius:6px;
                 padding:14px 18px;margin-bottom:16px">
                <span style="font-family:Barlow Condensed,sans-serif;font-size:0.9rem;
                      color:#607080;letter-spacing:1px">
                    {len(jogadores)} JOGADORES  ·  {len(times)} TIMES  ·
                    ~{por_time} POR TIME
                </span>
            </div>
            """, unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            with col_a:
                apenas_sem = st.checkbox("Sortear só quem não tem time", value=False)
            with col_b:
                balanceado = st.checkbox("Distribuição balanceada", value=True)

            if st.button("⚡ REALIZAR SORTEIO", use_container_width=True, type="primary"):
                _sortear(campeonato_id, times, jogadores, apenas_sem, balanceado)
                st.rerun()

            if any(j["time_id"] for j in jogadores):
                if st.button("🔄 Limpar Sorteio", use_container_width=True, type="secondary"):
                    limpar_times_jogadores(campeonato_id)
                    st.rerun()

                st.markdown("<hr class='xt-divider'>", unsafe_allow_html=True)
                st.markdown('<div class="xt-section-label">Distribuição Atual</div>', unsafe_allow_html=True)
                _mostrar_times(times, jogadores)

    # ── Por Time ──────────────────────────────────────────────
    with tab3:
        if not any(j["time_id"] for j in jogadores):
            st.info("Nenhum jogador atribuído ainda. Use a aba **🎲 Sortear**.")
        else:
            _mostrar_times(times, jogadores, expandido=True)


def _sortear(campeonato_id, times, jogadores, apenas_sem, balanceado):
    if apenas_sem:
        pool = [j for j in jogadores if not j["time_id"]]
    else:
        limpar_times_jogadores(campeonato_id)
        pool = list(jogadores)
    random.shuffle(pool)
    for idx, j in enumerate(pool):
        t = times[idx % len(times)] if balanceado else random.choice(times)
        atribuir_time_jogador(j["id"], t["id"])
    st.success(f"✅ {len(pool)} jogador(es) sorteado(s) em {len(times)} times!")


def _mostrar_times(times, jogadores, expandido=False):
    for t in times:
        cor = t.get("cor", "#0066ff")
        membros = [j for j in jogadores if j["time_id"] == t["id"]]
        with st.expander(
            f"**{t['nome']}**  —  {len(membros)} jogador(es)",
            expanded=expandido
        ):
            if not membros:
                st.caption("Nenhum jogador neste time.")
            else:
                for i, j in enumerate(membros, 1):
                    st.markdown(
                        f'<div class="xt-player-row">'
                        f'<span class="xt-player-num" style="color:{cor}">{i:02d}</span>'
                        f'<span class="xt-player-name">{j["nome"]}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
