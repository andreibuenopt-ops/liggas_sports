import streamlit as st
from utils.database import listar_times, adicionar_time, deletar_time, get_campeonato

CORES = ["#0066ff","#00e5ff","#00e564","#ff5050","#ffaa00",
         "#9060ff","#ff6b35","#00bcd4","#e91e63","#8bc34a",
         "#ff9800","#3f51b5","#009688","#795548","#607d8b"]

def render(campeonato_id):
    camp = get_campeonato(campeonato_id)
    import json
    config = json.loads(camp.get("config") or "{}")
    game = config.get("game")
    tem_rating = game is not None
    formato = camp.get("formato", "")

    st.markdown('<div class="xt-page-title">⚙️ Times</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="xt-page-sub">{camp["nome"]}</div>', unsafe_allow_html=True)

    times = listar_times(campeonato_id)

    if game:
        st.markdown(f"""
        <div style="background:#0d1a2d;border:1px solid #1e3a5f;border-radius:6px;
             padding:10px 16px;margin-bottom:12px">
            <span style="font-family:Barlow Condensed,sans-serif;font-size:0.8rem;
                  letter-spacing:2px;text-transform:uppercase;color:#607080">Game: </span>
            <span style="font-family:Rajdhani,sans-serif;font-weight:700;color:#00e5ff">{game}</span>
            <span style="font-family:Rajdhani,sans-serif;font-size:0.8rem;color:#405060;margin-left:12px">
                — O rating será usado no sorteio por potes</span>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("➕ Adicionar Time", expanded=len(times) == 0):
        with st.form("form_time"):
            if tem_rating:
                col1, col2, col3 = st.columns([3, 1.2, 1])
            else:
                col1, col2 = st.columns([4, 1])

            with col1:
                nome_time = st.text_input("Nome do Time *",
                    placeholder="Ex: Real Madrid, Time Azul, Turma A...")
            if tem_rating:
                with col2:
                    rating = st.number_input("Rating", 0, 99, 80,
                        help=f"Rating geral do time no {game}")
            else:
                rating = 0
            with (col2 if not tem_rating else col3):
                cor_idx = st.selectbox("Cor", range(len(CORES)),
                    format_func=lambda i: f"Cor {i+1}")

            submitted = st.form_submit_button("➕ ADICIONAR", use_container_width=True, type="primary")

        if submitted:
            if not nome_time.strip():
                st.error("Informe o nome!")
            else:
                adicionar_time(campeonato_id, nome_time.strip(),
                               cor=CORES[cor_idx], rating=int(rating), game=game)
                st.success(f"✅ {nome_time} adicionado!")
                st.rerun()

    st.markdown("<hr class='xt-divider'>", unsafe_allow_html=True)
    st.markdown(f'<div class="xt-section-label">{len(times)} time(s)</div>', unsafe_allow_html=True)

    if not times:
        st.info("Nenhum time cadastrado ainda.")
        return

    for t in times:
        col1, col2, col3 = st.columns([0.4, 5, 0.8])
        with col1:
            st.markdown(
                f'<div style="width:12px;height:12px;border-radius:50%;'
                f'background:{t["cor"]};margin-top:10px;'
                f'box-shadow:0 0 8px {t["cor"]}80"></div>',
                unsafe_allow_html=True)
        with col2:
            rating_tag = ""
            if tem_rating and t.get("rating"):
                rating_tag = (f' <span style="background:#0d1a2d;border:1px solid #1e3a5f;'
                              f'border-radius:3px;padding:1px 8px;font-family:Barlow Condensed,sans-serif;'
                              f'font-size:0.75rem;font-weight:700;color:#ffaa00;letter-spacing:1px">'
                              f'⭐ {t["rating"]}</span>')
            grupo_tag = ""
            if t.get("grupo"):
                grupo_tag = (f' <span style="background:#0d1a2d;border:1px solid #1e3a5f;'
                             f'border-radius:3px;padding:1px 8px;font-family:Barlow Condensed,sans-serif;'
                             f'font-size:0.7rem;color:#607080;letter-spacing:1px">'
                             f'Grupo {t["grupo"]}</span>')
            st.markdown(
                f'<div style="font-family:Rajdhani,sans-serif;font-weight:700;'
                f'font-size:0.95rem;color:#c0d0e0;padding-top:6px">'
                f'{t["nome"]}{rating_tag}{grupo_tag}</div>',
                unsafe_allow_html=True)
        with col3:
            if st.button("✕", key=f"del_t_{t['id']}"):
                deletar_time(t["id"])
                st.rerun()
