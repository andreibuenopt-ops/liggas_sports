import streamlit as st
from utils.database import listar_times, adicionar_time, deletar_time, get_campeonato

CORES = ["#0066ff","#00e5ff","#00e564","#ff5050","#ffaa00",
         "#9060ff","#ff6b35","#00bcd4","#e91e63","#8bc34a",
         "#ff9800","#3f51b5","#009688","#795548","#607d8b"]

def render(campeonato_id):
    camp = get_campeonato(campeonato_id)
    st.markdown('<div class="xt-page-title">⚙️ Times</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="xt-page-sub">{camp["nome"]}</div>', unsafe_allow_html=True)

    times = listar_times(campeonato_id)

    with st.expander("➕ Adicionar Time", expanded=len(times) == 0):
        with st.form("form_time"):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                nome_time = st.text_input("Nome do Time / Participante",
                    placeholder="Ex: Turma A, Real Madrid, Player1...")
            with col2:
                grupo = st.text_input("Grupo", placeholder="A, B...")
            with col3:
                cor_idx = st.selectbox("Cor", list(range(len(CORES))),
                    format_func=lambda i: f"Cor {i+1}")
            submitted = st.form_submit_button("➕ ADICIONAR", use_container_width=True, type="primary")
        if submitted:
            if not nome_time.strip():
                st.error("Informe o nome!")
            else:
                adicionar_time(campeonato_id, nome_time.strip(), grupo.strip() or None, CORES[cor_idx])
                st.success(f"✅ {nome_time} adicionado!")
                st.rerun()

    st.markdown("<hr class='xt-divider'>", unsafe_allow_html=True)
    st.markdown(f'<div class="xt-section-label">{len(times)} time(s) cadastrado(s)</div>', unsafe_allow_html=True)

    if not times:
        st.info("Nenhum time cadastrado ainda.")
        return

    for t in times:
        col1, col2, col3 = st.columns([0.4, 4.6, 1])
        with col1:
            st.markdown(
                f'<div style="width:14px;height:14px;border-radius:50%;'
                f'background:{t["cor"]};margin-top:10px;'
                f'box-shadow:0 0 8px {t["cor"]}80"></div>',
                unsafe_allow_html=True
            )
        with col2:
            grupo_txt = f' <span style="color:#304050;font-size:0.75rem">— Grupo {t["grupo"]}</span>' if t.get("grupo") else ""
            st.markdown(
                f'<div style="font-family:Rajdhani,sans-serif;font-weight:700;'
                f'font-size:0.95rem;color:#c0d0e0;padding-top:6px">'
                f'{t["nome"]}{grupo_txt}</div>',
                unsafe_allow_html=True
            )
        with col3:
            if st.button("✕", key=f"del_t_{t['id']}", help="Remover"):
                deletar_time(t["id"])
                st.rerun()
