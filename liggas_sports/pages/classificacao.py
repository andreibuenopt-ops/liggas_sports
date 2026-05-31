import streamlit as st
import plotly.express as px
import pandas as pd
from services.services import (listar_campeonatos, calcular_classificacao,
                                equipes_campeonato)
from utils.style import page_header, divider, section_label, classif_table

def render():
    page_header("📊 Classificação", "Tabelas automáticas por campeonato")

    camps = listar_campeonatos()
    if not camps:
        st.info("Nenhum campeonato cadastrado.")
        return

    opcoes = {c["nome"]: c["id"] for c in camps}
    sel = st.selectbox("Campeonato", list(opcoes.keys()))
    cid = opcoes[sel]
    camp = next(c for c in camps if c["id"] == cid)

    classif = calcular_classificacao(cid)
    if not classif:
        st.info("Nenhum jogo registrado ainda.")
        return

    grupos = sorted(set(r["grupo"] for r in classif if r.get("grupo")))

    if grupos and len(grupos) > 1:
        tabs = st.tabs(["Geral"] + [f"Grupo {g}" for g in grupos])
        with tabs[0]:
            st.markdown(classif_table(classif, camp.get("classificados_por_grupo",2) * len(grupos)),
                        unsafe_allow_html=True)
            _grafico_classif(classif)

        for i, g in enumerate(grupos, 1):
            with tabs[i]:
                gr = [r for r in classif if r["grupo"] == g]
                st.markdown(classif_table(gr, camp.get("classificados_por_grupo",2)),
                            unsafe_allow_html=True)
    else:
        st.markdown(classif_table(classif, 3), unsafe_allow_html=True)
        _grafico_classif(classif)

def _grafico_classif(classif):
    divider()
    col1, col2 = st.columns(2)
    df = pd.DataFrame(classif)
    with col1:
        section_label("Pontos por Equipe")
        fig = px.bar(df, x="equipe", y="pontos",
                     color="pontos", color_continuous_scale=["#1e3a5f","#00e5ff"],
                     labels={"equipe":"","pontos":"Pontos"})
        fig.update_layout(**_layout())
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        section_label("Gols Pró vs Contra")
        fig2 = px.bar(df, x="equipe", y=["gols_pro","gols_contra"],
                      barmode="group",
                      color_discrete_sequence=["#00e564","#ff5050"])
        fig2.update_layout(**_layout())
        st.plotly_chart(fig2, use_container_width=True)

def _layout():
    return dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(13,17,23,0.8)",
                font=dict(family="Rajdhani",color="#8090a0",size=10),
                margin=dict(l=5,r=5,t=5,b=5),coloraxis_showscale=False,
                xaxis=dict(gridcolor="#1a2535"),yaxis=dict(gridcolor="#1a2535"),
                legend=dict(bgcolor="rgba(0,0,0,0)"))
