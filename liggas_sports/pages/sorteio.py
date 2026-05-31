import streamlit as st
import random, time
from core import engine, style

def render():
    cfg = engine.get_config()
    if not cfg:
        st.info("Configure um campeonato primeiro."); return

    style.h1(st, "🎲 Sorteio ao Vivo", cfg.get("nome",""))
    times = engine.get_times()
    if not times:
        st.warning("Nenhum time cadastrado."); return

    fmt = cfg.get("formato","")
    n_grupos = cfg.get("n_grupos", 4)
    tpg = len(times) // n_grupos

    st.markdown(f"""
    <div style="background:#0d1a2d;border:1px solid #1e3a5f;border-radius:8px;
         padding:12px 18px;margin-bottom:16px;text-align:center">
        <span style="font-family:'Barlow Condensed',sans-serif;color:#607080;
              font-size:.68rem;letter-spacing:3px">
            {len(times)} TIMES · {n_grupos} GRUPOS · ~{tpg} POR GRUPO
        </span>
    </div>""", unsafe_allow_html=True)

    usar_potes = st.checkbox("Usar potes por rating", value=True,
        help="Times com maior rating ficam separados — igual sorteio da UEFA/FIFA")

    if st.button("⚡ INICIAR SORTEIO AO VIVO", use_container_width=True, type="primary"):
        _animar(times, n_grupos, usar_potes)
        if st.button("✅ APLICAR ESTE SORTEIO AO CAMPEONATO", use_container_width=True, type="primary", key="aplicar"):
            ok = engine.gerar_tabela()
            st.success("✅ Tabela gerada com os grupos sorteados!") if ok else st.error("Erro")
            st.rerun()

def _animar(times, n_grupos, usar_potes):
    nomes = [t["nome"] for t in times]
    ratings = {t["nome"]: t.get("rating", 50) for t in times}
    grupos = {chr(65+i): [] for i in range(n_grupos)}
    placeholder = st.empty()

    if usar_potes and any(ratings.values()):
        sorted_t = sorted(nomes, key=lambda x: -ratings[x])
        tpg = len(nomes) // n_grupos
        potes = [sorted_t[i*n_grupos:(i+1)*n_grupos] for i in range(tpg)]
    else:
        shuffled = list(nomes); random.shuffle(shuffled)
        potes = [shuffled[i::n_grupos] for i in range(n_grupos)]

    for pi, pote in enumerate(potes):
        st.markdown(f'<div class="ifc-lbl">SORTEANDO POTE {pi+1}...</div>', unsafe_allow_html=True)
        random.shuffle(pote)
        slots = [g for g in grupos if len(grupos[g]) == pi]
        random.shuffle(slots)
        for i, equipe in enumerate(pote):
            for _ in range(7):
                rnd = random.choice(nomes)
                placeholder.markdown(f"""
                <div style="text-align:center;padding:18px;background:#0d1a2d;
                     border:1px solid #00e5ff;border-radius:8px;margin:8px 0">
                    <div style="font-family:'Barlow Condensed',sans-serif;font-size:.62rem;
                         letter-spacing:3px;color:#506070">SORTEANDO...</div>
                    <div style="font-family:'Barlow Condensed',sans-serif;font-size:2rem;
                         font-weight:800;color:#00e5ff;letter-spacing:2px">{rnd.upper()}</div>
                </div>""", unsafe_allow_html=True)
                time.sleep(0.07)
            g_dest = slots[i] if i < len(slots) else list(grupos.keys())[i % n_grupos]
            grupos[g_dest].append(equipe)
            placeholder.markdown(f"""
            <div style="text-align:center;padding:18px;background:#0d1a2d;
                 border:2px solid #00e5ff;border-radius:8px;margin:8px 0;
                 box-shadow:0 0 20px rgba(0,229,255,.25)">
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:.62rem;
                     letter-spacing:3px;color:#304050">GRUPO {g_dest}</div>
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:2.2rem;
                     font-weight:800;color:#fff;letter-spacing:2px">{equipe.upper()}</div>
                <div style="font-family:Rajdhani,sans-serif;color:#00e5ff">→ GRUPO {g_dest}</div>
            </div>""", unsafe_allow_html=True)
            time.sleep(0.45)

    placeholder.empty()
    st.success("✅ Sorteio concluído!")
    style.div(st)

    cols = st.columns(min(4, n_grupos))
    for i, (g, eqs) in enumerate(grupos.items()):
        with cols[i % len(cols)]:
            st.markdown(f'<div class="ifc-grp-hdr">GRUPO {g}</div>', unsafe_allow_html=True)
            for e in eqs:
                rat = next((t.get("rating",0) for t in engine.get_times() if t["nome"]==e), 0)
                st.markdown(f"""
                <div style="padding:5px 0;border-bottom:1px solid #111827;
                     font-family:Rajdhani,sans-serif;font-weight:700;
                     font-size:.88rem;color:#c0d0e0">
                    {e}
                    {f'<span style="float:right;font-family:Barlow Condensed,sans-serif;font-size:.7rem;color:#ffaa00">⭐{rat}</span>' if rat else ''}
                </div>""", unsafe_allow_html=True)
