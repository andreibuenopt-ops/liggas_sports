import streamlit as st
from services.services import (listar_campeonatos, listar_historico, salvar_historico,
                                listar_equipes, listar_jogadores, artilheiros)
from utils.style import page_header, divider, section_label

def render():
    page_header("📜 Histórico", "Temporadas, campeões e recordes")

    abas = st.tabs(["🏆 Ver Histórico", "➕ Registrar Temporada"])

    with abas[0]:
        historico = listar_historico()
        if not historico:
            st.info("Nenhuma temporada registrada ainda.")
        else:
            camps_hist = list(dict.fromkeys(h["campeonato"] for h in historico))
            filtro = st.selectbox("Campeonato", ["Todos"] + camps_hist)
            if filtro != "Todos":
                historico = [h for h in historico if h["campeonato"] == filtro]

            for h in historico:
                st.markdown(f"""
                <div class="ls-card">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                        <div>
                            <div class="ls-card-title">{h['campeonato']} · {h['temporada']}</div>
                            <div class="ls-card-meta">
                                🥇 {h['campeao'] or '—'}
                                {'· 🥈 ' + h['vice'] if h['vice'] else ''}
                                {'· ⚽ ' + h['artilheiro'] + ' (' + str(h['artilheiro_gols']) + 'g)' if h['artilheiro'] else ''}
                            </div>
                            {f'<div style="font-family:Rajdhani,sans-serif;font-size:.8rem;color:#304050;margin-top:4px">{h["observacoes"]}</div>' if h['observacoes'] else ''}
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

    with abas[1]:
        section_label("Registrar Nova Temporada")
        camps = listar_campeonatos()
        equipes = listar_equipes()
        jogadores = listar_jogadores()

        if not camps: st.warning("Nenhum campeonato."); return

        with st.form("form_hist"):
            camp_sel = st.selectbox("Campeonato", [c["nome"] for c in camps])
            camp_id = next(c["id"] for c in camps if c["nome"] == camp_sel)
            temporada = st.text_input("Temporada", placeholder="2025, 2024/25...")

            col1, col2 = st.columns(2)
            with col1:
                campeao_sel = st.selectbox("Campeão 🥇", [""]+[e["nome"] for e in equipes])
                campeao_id = next((e["id"] for e in equipes if e["nome"]==campeao_sel), None)
            with col2:
                vice_sel = st.selectbox("Vice 🥈", [""]+[e["nome"] for e in equipes])
                vice_id = next((e["id"] for e in equipes if e["nome"]==vice_sel), None)

            col3, col4 = st.columns(2)
            with col3:
                art_sel = st.selectbox("Artilheiro ⚽", [""]+[j["nome"] for j in jogadores])
                art_id = next((j["id"] for j in jogadores if j["nome"]==art_sel), None)
            with col4:
                art_gols = st.number_input("Gols do artilheiro", 0, 99, 0)

            obs = st.text_area("Observações", height=70)
            s = st.form_submit_button("💾 SALVAR", use_container_width=True, type="primary")

        if s:
            if not temporada.strip(): st.error("Informe a temporada!"); return
            salvar_historico({
                "campeonato_id": camp_id, "temporada": temporada.strip(),
                "campeao_id": campeao_id, "vice_id": vice_id,
                "artilheiro_id": art_id, "artilheiro_gols": art_gols or None,
                "observacoes": obs or None
            })
            st.success("✅ Temporada registrada!")
