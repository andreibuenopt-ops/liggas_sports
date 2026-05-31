import streamlit as st
import random
import time
from services.services import listar_campeonatos, equipes_campeonato
from utils.style import page_header, divider, section_label

def render():
    page_header("🎲 Sorteio ao Vivo", "Sorteio de grupos e confrontos com animação")

    camps = listar_campeonatos()
    if not camps:
        st.info("Nenhum campeonato cadastrado.")
        return

    opcoes = {c["nome"]: c["id"] for c in camps}
    sel = st.selectbox("Campeonato", list(opcoes.keys()))
    cid = opcoes[sel]
    camp = next(c for c in camps if c["id"] == cid)

    equipes = equipes_campeonato(cid)
    if not equipes:
        st.warning("Inscreva equipes no campeonato primeiro.")
        return

    st.markdown("<hr class='ls-divider'>", unsafe_allow_html=True)

    tipo = st.radio("Tipo de Sorteio",
                    ["🎯 Sorteio de Grupos", "⚔️ Sorteio de Confrontos (Mata-Mata)"],
                    horizontal=True)

    if "Grupos" in tipo:
        _sorteio_grupos(cid, camp, equipes)
    else:
        _sorteio_confrontos(equipes)

def _sorteio_grupos(cid, camp, equipes):
    n_grupos = camp.get("n_grupos") or 4
    tpg = len(equipes) // n_grupos

    st.markdown(f"""
    <div style="background:#0d1a2d;border:1px solid #1e3a5f;border-radius:8px;
         padding:14px 20px;margin-bottom:16px;text-align:center">
        <span style="font-family:'Barlow Condensed',sans-serif;color:#607080;
              font-size:.7rem;letter-spacing:3px">
            {len(equipes)} EQUIPES · {n_grupos} GRUPOS · ~{tpg} POR GRUPO
        </span>
    </div>""", unsafe_allow_html=True)

    usar_potes = st.checkbox("Usar potes por rating (melhores separados)", value=True)

    if st.button("⚡ INICIAR SORTEIO AO VIVO", use_container_width=True, type="primary"):
        _animar_sorteio_grupos(equipes, n_grupos, usar_potes)

def _animar_sorteio_grupos(equipes, n_grupos, usar_potes):
    grupos = {chr(65+i): [] for i in range(n_grupos)}
    placeholder = st.empty()

    if usar_potes and any(e.get("rating",0) > 0 for e in equipes):
        eq_sorted = sorted(equipes, key=lambda e: -(e.get("rating") or 0))
        tpg = len(equipes) // n_grupos
        potes = [eq_sorted[i*n_grupos:(i+1)*n_grupos] for i in range(tpg)]
    else:
        shuffled = list(equipes)
        random.shuffle(shuffled)
        potes = [shuffled[i::n_grupos] for i in range(n_grupos)]

    for pote_idx, pote in enumerate(potes):
        st.markdown(f'<div class="ls-label">SORTEANDO POTE {pote_idx+1}...</div>',
                    unsafe_allow_html=True)
        random.shuffle(pote)
        slots = [g for g in grupos if len(grupos[g]) == pote_idx]
        random.shuffle(slots)

        for i, equipe in enumerate(pote):
            grupo_dest = slots[i] if i < len(slots) else list(grupos.keys())[i % n_grupos]
            # Animação: mostra rodando
            for _ in range(6):
                eq_rand = random.choice(equipes)
                placeholder.markdown(f"""
                <div style="text-align:center;padding:20px;background:#0d1a2d;
                     border:1px solid #00e5ff;border-radius:8px;margin:10px 0">
                    <div style="font-family:'Barlow Condensed',sans-serif;font-size:.7rem;
                         letter-spacing:3px;color:#506070">SORTEANDO...</div>
                    <div style="font-family:'Barlow Condensed',sans-serif;font-size:2rem;
                         font-weight:800;color:#00e5ff;letter-spacing:2px;
                         animation:pulse 0.3s">{eq_rand['nome'].upper()}</div>
                </div>""", unsafe_allow_html=True)
                time.sleep(0.08)

            grupos[grupo_dest].append(equipe)
            placeholder.markdown(f"""
            <div style="text-align:center;padding:20px;background:#0d1a2d;
                 border:2px solid #00e5ff;border-radius:8px;margin:10px 0;
                 box-shadow:0 0 20px rgba(0,229,255,.3)">
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:.7rem;
                     letter-spacing:3px;color:#506070">GRUPO {grupo_dest}</div>
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:2.2rem;
                     font-weight:800;color:#ffffff;letter-spacing:2px">{equipe['nome'].upper()}</div>
                <div style="font-family:Rajdhani,sans-serif;color:#00e5ff">
                    → GRUPO {grupo_dest}</div>
            </div>""", unsafe_allow_html=True)
            time.sleep(0.4)

    placeholder.empty()
    st.success("✅ Sorteio concluído!")
    st.markdown("<hr class='ls-divider'>", unsafe_allow_html=True)

    # Resultado final
    cols = st.columns(min(4, n_grupos))
    for i, (g, eqs) in enumerate(grupos.items()):
        with cols[i % len(cols)]:
            st.markdown(f"""
            <div style="background:#0d1a2d;border:1px solid #1e3a5f;
                 border-top:3px solid #00e5ff;border-radius:6px;padding:12px">
                <div style="font-family:'Barlow Condensed',sans-serif;font-weight:800;
                     font-size:1rem;letter-spacing:3px;color:#00e5ff;margin-bottom:8px">
                     GRUPO {g}</div>""", unsafe_allow_html=True)
            for e in eqs:
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:6px;padding:4px 0;
                     border-bottom:1px solid #111827">
                    <div style="width:8px;height:8px;border-radius:50%;background:{e['cor']}"></div>
                    <span style="font-family:Rajdhani,sans-serif;font-weight:600;
                          color:#c0d0e0;font-size:.88rem">{e['nome']}</span>
                    {f'<span style="margin-left:auto;font-family:Barlow Condensed,sans-serif;font-size:.7rem;color:#ffaa00">⭐{e["rating"]}</span>' if e.get("rating") else ''}
                </div>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

def _sorteio_confrontos(equipes):
    st.markdown(f'<div class="ls-label">{len(equipes)} equipes disponíveis</div>',
                unsafe_allow_html=True)

    if len(equipes) < 2:
        st.warning("Mínimo 2 equipes."); return

    if st.button("⚡ SORTEAR CONFRONTOS", use_container_width=True, type="primary"):
        shuffled = list(equipes)
        random.shuffle(shuffled)
        placeholder = st.empty()

        confrontos = []
        for i in range(0, len(shuffled)-1, 2):
            e1, e2 = shuffled[i], shuffled[i+1]
            for _ in range(8):
                r1 = random.choice(equipes)
                r2 = random.choice(equipes)
                placeholder.markdown(f"""
                <div style="text-align:center;padding:16px;background:#0d1a2d;
                     border:1px solid #1e3a5f;border-radius:8px">
                    <span style="font-family:'Barlow Condensed',sans-serif;font-size:1.3rem;
                          font-weight:800;color:#c0d0e0">{r1['nome']} 
                          <span style="color:#304050">×</span> {r2['nome']}</span>
                </div>""", unsafe_allow_html=True)
                time.sleep(0.06)
            confrontos.append((e1, e2))
            placeholder.markdown(f"""
            <div style="text-align:center;padding:16px;background:#0d1a2d;
                 border:2px solid #00e5ff;border-radius:8px;
                 box-shadow:0 0 16px rgba(0,229,255,.25)">
                <span style="font-family:'Barlow Condensed',sans-serif;font-size:1.5rem;
                      font-weight:800;color:#fff">{e1['nome']} 
                      <span style="color:#304050">×</span> {e2['nome']}</span>
            </div>""", unsafe_allow_html=True)
            time.sleep(0.5)

        placeholder.empty()
        st.success("✅ Sorteio concluído!")
        divider()
        section_label("Confrontos Sorteados")
        for i, (e1, e2) in enumerate(confrontos, 1):
            st.markdown(f"""
            <div style="background:#0d1a2d;border:1px solid #1e3a5f;border-radius:6px;
                 padding:12px 18px;margin-bottom:6px;display:flex;
                 align-items:center;justify-content:center;gap:20px">
                <span style="font-family:'Barlow Condensed',sans-serif;font-size:.65rem;
                      color:#304050;min-width:30px">#{i}</span>
                <span style="font-family:Rajdhani,sans-serif;font-weight:700;
                      font-size:1rem;color:#e0e6f0">{e1['nome']}</span>
                <span style="font-family:'Barlow Condensed',sans-serif;color:#304050;
                      font-size:.9rem;font-weight:800;letter-spacing:2px">×</span>
                <span style="font-family:Rajdhani,sans-serif;font-weight:700;
                      font-size:1rem;color:#e0e6f0">{e2['nome']}</span>
            </div>""", unsafe_allow_html=True)
        if len(shuffled) % 2:
            st.info(f"⚠️ {shuffled[-1]['nome']} ficou sem par (número ímpar de equipes)")
