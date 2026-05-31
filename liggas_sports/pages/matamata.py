import streamlit as st
from core import engine, style

def render():
    cfg = engine.get_config()
    if not cfg:
        st.info("Configure um campeonato primeiro."); return

    style.h1(st, "⚔️ Mata-Mata", cfg.get("nome",""))
    fmt = cfg.get("formato","")

    bracket = engine.get_bracket()

    # Botões de controle
    col1, col2 = st.columns(2)
    with col1:
        if fmt in ("Grupos","Chaves Cruzadas","Pontos Corridos + Mata-Mata"):
            if st.button("⏭️ GERAR MATA-MATA COM CLASSIFICADOS", use_container_width=True, type="primary"):
                ok, msg = engine.gerar_mata_mata_de_classificados(
                    cfg.get("classificados_por_grupo", 2))
                st.success(msg) if ok else st.warning(msg)
                st.rerun()
    with col2:
        if bracket:
            if st.button("⏭️ AVANÇAR FASE", use_container_width=True):
                ok, msg = engine.avancar_mata_mata()
                st.success(msg) if ok else st.warning(msg)
                st.rerun()

    if not bracket:
        if fmt == "Eliminatórias":
            st.info("Tabela gerada — vá em **⚽ Jogos** para registrar os resultados.")
        else:
            st.info("Finalize a fase de grupos e clique em **Gerar Mata-Mata**.")

        # Mostra bracket inicial se for Eliminatórias
        fases = engine.get_fases()
        mm_fases = [f for f in fases if not any(
            f.startswith(x) for x in ["Liga","Volta","Grupo","Pontos"])]
        if mm_fases:
            _render_bracket({f: engine.get_jogos(fase=f) for f in mm_fases})
        return

    style.div(st)
    _render_bracket(bracket)

    # Campeão
    camp = engine.campeao()
    if camp:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0d1a2d,#1a2d0d);
             border:2px solid #ffaa00;border-radius:10px;padding:20px;
             text-align:center;margin-top:16px;
             box-shadow:0 0 30px rgba(255,170,0,.2)">
            <div style="font-size:2.5rem">🏆</div>
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:.7rem;
                 letter-spacing:4px;color:#806030;text-transform:uppercase">CAMPEÃO</div>
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:2.2rem;
                 font-weight:800;color:#ffaa00;letter-spacing:3px;text-transform:uppercase">
                {camp}</div>
        </div>""", unsafe_allow_html=True)

def _render_bracket(bracket):
    fases = list(bracket.keys())
    if not fases: return
    cols = st.columns(max(1, len(fases)))
    for col, fase in zip(cols, fases):
        with col:
            st.markdown(f'<div class="ifc-bracket-fase">{fase}</div>', unsafe_allow_html=True)
            for j in bracket[fase]:
                st.markdown(style.bracket_card(j), unsafe_allow_html=True)
