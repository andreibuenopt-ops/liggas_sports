import streamlit as st
import plotly.express as px
import pandas as pd
from core import engine, style

def _layout():
    return dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(13,17,23,.8)",
                font=dict(family="Rajdhani",color="#8090a0",size=10),
                margin=dict(l=5,r=5,t=5,b=5),coloraxis_showscale=False,
                xaxis=dict(gridcolor="#1a2535"),yaxis=dict(gridcolor="#1a2535"),
                legend=dict(bgcolor="rgba(0,0,0,0)"))

def render():
    cfg = engine.get_config()
    if not cfg:
        st.info("Configure um campeonato primeiro."); return

    style.h1(st, "📊 Classificação", cfg.get("nome",""))
    fmt = cfg.get("formato","")

    if fmt in ("Grupos","Chaves Cruzadas","Pontos Corridos + Mata-Mata"):
        _classif_grupos(cfg)
    else:
        _classif_liga()

def _classif_grupos(cfg):
    grupos_class = engine.get_grupos_classificacao()
    if not grupos_class:
        st.info("Nenhum grupo gerado ainda."); return

    grupos = list(grupos_class.keys())
    class_por_grupo = cfg.get("classificados_por_grupo", 2)

    # Visão geral
    col_n = min(4, len(grupos))
    rows = [grupos[i:i+col_n] for i in range(0, len(grupos), col_n)]

    for row in rows:
        cols = st.columns(len(row))
        for col, g in zip(cols, row):
            tabela = grupos_class[g]
            with col:
                st.markdown(f'<div class="ifc-grp-hdr">GRUPO {g}</div>', unsafe_allow_html=True)
                st.markdown(style.classif_table(tabela, class_por_grupo), unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

    style.div(st)

    # Gráfico pontos por grupo
    dados = []
    for g, tabela in grupos_class.items():
        for t in tabela:
            dados.append({"Grupo": f"Grp {g}", "Time": t["time"][:10], "Pontos": t["P"]})
    if dados:
        df = pd.DataFrame(dados)
        fig = px.bar(df, x="Time", y="Pontos", color="Grupo",
                     color_discrete_sequence=["#0066ff","#00e5ff","#00e564","#ffaa00",
                                               "#9060ff","#ff5050","#ff6b35","#8bc34a"])
        fig.update_layout(**_layout())
        st.plotly_chart(fig, use_container_width=True)

def _classif_liga():
    tabela = engine.calcular_classificacao()
    if not tabela:
        st.info("Nenhum jogo registrado ainda."); return

    st.markdown(style.classif_table(tabela, 4), unsafe_allow_html=True)
    style.div(st)

    df = pd.DataFrame(tabela)
    col1, col2 = st.columns(2)
    with col1:
        style.lbl(st, "Pontos")
        fig = px.bar(df, x="time", y="P",
                     color="P", color_continuous_scale=["#1e3a5f","#00e5ff"])
        fig.update_layout(**_layout())
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        style.lbl(st, "Gols Pró vs Contra")
        fig2 = px.bar(df, x="time", y=["GP","GC"], barmode="group",
                      color_discrete_sequence=["#00e564","#ff5050"])
        fig2.update_layout(**_layout())
        st.plotly_chart(fig2, use_container_width=True)
