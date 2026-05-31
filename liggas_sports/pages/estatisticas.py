import streamlit as st
import plotly.express as px
import pandas as pd
from services.services import (artilheiros, assistencias_ranking, cartoes_ranking,
                                listar_campeonatos, calcular_classificacao)
from utils.style import page_header, divider, section_label

def _layout():
    return dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(13,17,23,0.8)",
                font=dict(family="Rajdhani",color="#8090a0",size=10),
                margin=dict(l=5,r=5,t=5,b=5),coloraxis_showscale=False,
                xaxis=dict(gridcolor="#1a2535"),yaxis=dict(gridcolor="#1a2535"),
                legend=dict(bgcolor="rgba(0,0,0,0)"))

def render():
    page_header("📈 Estatísticas", "Rankings e indicadores do campeonato")

    camps = listar_campeonatos()
    opcoes_camp = {"Todos": None} | {c["nome"]: c["id"] for c in camps}
    sel = st.selectbox("Campeonato", list(opcoes_camp.keys()))
    cid = opcoes_camp[sel]

    tab1, tab2, tab3, tab4 = st.tabs(["⚽ Artilharia", "🎯 Assistências", "🟨 Cartões", "📊 Rankings"])

    with tab1:
        arts = artilheiros(cid=cid, limit=20)
        if arts:
            df = pd.DataFrame(arts)
            col1, col2 = st.columns([1,1])
            with col1:
                section_label("Top Artilheiros")
                for i, r in enumerate(arts, 1):
                    medal = {1:"🥇",2:"🥈",3:"🥉"}.get(i,"")
                    st.markdown(
                        f'<div style="display:flex;justify-content:space-between;'
                        f'padding:6px 0;border-bottom:1px solid #0d1a2d">'
                        f'<span style="font-family:Rajdhani,sans-serif;color:#c0d0e0">'
                        f'{medal or i}. {r["jogador"]}'
                        f'<span style="color:#405060;font-size:.8rem"> · {r["equipe"]}</span></span>'
                        f'<span style="font-family:Barlow Condensed,sans-serif;font-weight:800;'
                        f'color:#00e5ff;font-size:1rem">{r["gols"]}</span></div>',
                        unsafe_allow_html=True)
            with col2:
                fig = px.bar(df.head(10), x="gols", y="jogador", orientation="h",
                             color="gols", color_continuous_scale=["#1e3a5f","#00e5ff"])
                fig.update_layout(**_layout())
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum gol registrado.")

    with tab2:
        asts = assistencias_ranking(cid=cid)
        if asts:
            df = pd.DataFrame(asts)
            col1, col2 = st.columns([1,1])
            with col1:
                section_label("Top Assistências")
                for i, r in enumerate(asts, 1):
                    st.markdown(
                        f'<div style="display:flex;justify-content:space-between;'
                        f'padding:6px 0;border-bottom:1px solid #0d1a2d">'
                        f'<span style="font-family:Rajdhani,sans-serif;color:#c0d0e0">'
                        f'{i}. {r["jogador"]}'
                        f'<span style="color:#405060;font-size:.8rem"> · {r["equipe"]}</span></span>'
                        f'<span style="font-family:Barlow Condensed,sans-serif;font-weight:800;'
                        f'color:#9060ff">{r["assistencias"]}</span></div>',
                        unsafe_allow_html=True)
            with col2:
                fig = px.bar(df.head(10), x="assistencias", y="jogador", orientation="h",
                             color="assistencias", color_continuous_scale=["#1e3a5f","#9060ff"])
                fig.update_layout(**_layout())
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhuma assistência registrada.")

    with tab3:
        carts = cartoes_ranking(cid=cid)
        if carts:
            amarelos = [c for c in carts if c["tipo"]=="Amarelo"]
            vermelhos = [c for c in carts if c["tipo"]=="Vermelho"]
            col1, col2 = st.columns(2)
            with col1:
                section_label("🟨 Amarelos")
                for r in amarelos[:10]:
                    st.markdown(f'<div style="font-family:Rajdhani,sans-serif;'
                                f'padding:5px 0;border-bottom:1px solid #0d1a2d;color:#c0d0e0">'
                                f'{r["jogador"]} <span style="color:#405060">· {r["equipe"]}</span>'
                                f'<span style="float:right;color:#ffaa00;font-weight:700">{r["total"]}</span>'
                                f'</div>', unsafe_allow_html=True)
            with col2:
                section_label("🟥 Vermelhos")
                for r in vermelhos[:10]:
                    st.markdown(f'<div style="font-family:Rajdhani,sans-serif;'
                                f'padding:5px 0;border-bottom:1px solid #0d1a2d;color:#c0d0e0">'
                                f'{r["jogador"]} <span style="color:#405060">· {r["equipe"]}</span>'
                                f'<span style="float:right;color:#ff5050;font-weight:700">{r["total"]}</span>'
                                f'</div>', unsafe_allow_html=True)
        else:
            st.info("Nenhum cartão registrado.")

    with tab4:
        if not camps: return
        camp_sel = st.selectbox("Campeonato para rankings", [c["nome"] for c in camps])
        cid2 = next(c["id"] for c in camps if c["nome"]==camp_sel)
        classif = calcular_classificacao(cid2)
        if not classif: st.info("Sem dados."); return

        col1, col2, col3 = st.columns(3)
        with col1:
            section_label("🏹 Melhor Ataque")
            top_ataque = sorted(classif, key=lambda x: -x["gols_pro"])[:5]
            for i, t in enumerate(top_ataque, 1):
                st.markdown(f'<div style="font-family:Rajdhani,sans-serif;padding:5px 0;'
                            f'border-bottom:1px solid #0d1a2d;color:#c0d0e0">'
                            f'{i}. {t["equipe"]}'
                            f'<span style="float:right;color:#00e564;font-weight:700">{t["gols_pro"]} gols</span>'
                            f'</div>', unsafe_allow_html=True)
        with col2:
            section_label("🛡️ Melhor Defesa")
            top_def = sorted(classif, key=lambda x: x["gols_contra"])[:5]
            for i, t in enumerate(top_def, 1):
                st.markdown(f'<div style="font-family:Rajdhani,sans-serif;padding:5px 0;'
                            f'border-bottom:1px solid #0d1a2d;color:#c0d0e0">'
                            f'{i}. {t["equipe"]}'
                            f'<span style="float:right;color:#00e5ff;font-weight:700">{t["gols_contra"]} sofridos</span>'
                            f'</div>', unsafe_allow_html=True)
        with col3:
            section_label("📈 Melhor Aproveitamento")
            top_aprov = sorted(classif, key=lambda x: -x["aproveitamento"])[:5]
            for i, t in enumerate(top_aprov, 1):
                st.markdown(f'<div style="font-family:Rajdhani,sans-serif;padding:5px 0;'
                            f'border-bottom:1px solid #0d1a2d;color:#c0d0e0">'
                            f'{i}. {t["equipe"]}'
                            f'<span style="float:right;color:#ffaa00;font-weight:700">{t["aproveitamento"]}%</span>'
                            f'</div>', unsafe_allow_html=True)
