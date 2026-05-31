import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import date
from services.services import (stats_gerais, listar_campeonatos, listar_jogos,
                                artilheiros, calcular_classificacao)
from utils.style import page_header, divider, section_label, jogo_row

def render():
    page_header("⚡ Dashboard", "Visão geral da plataforma")

    stats = stats_gerais()
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Campeonatos Ativos", stats["campeonatos"])
    c2.metric("Equipes", stats["equipes"])
    c3.metric("Jogadores", stats["jogadores"])
    c4.metric("Jogos Hoje", stats["jogos_hoje"])

    c5,c6,c7,c8 = st.columns(4)
    c5.metric("Agendados", stats["jogos_agendados"])
    c6.metric("Finalizados", stats["jogos_finalizados"])
    c7.metric("Total de Gols", stats["total_gols"])
    c8.metric("Média de Gols/Jogo",
              round(stats["total_gols"]/max(stats["jogos_finalizados"],1),2))

    divider()

    col1, col2 = st.columns([1.2, 1])

    with col1:
        section_label("Próximas Partidas")
        jogos = listar_jogos(status="Agendado")[:8]
        if jogos:
            for j in jogos:
                st.markdown(jogo_row(j, show_fase=True), unsafe_allow_html=True)
        else:
            st.info("Nenhuma partida agendada.")

    with col2:
        section_label("Últimos Resultados")
        finalizados = listar_jogos(status="Finalizado")
        finalizados_sorted = sorted(finalizados, key=lambda x: x["id"], reverse=True)[:8]
        if finalizados_sorted:
            for j in finalizados_sorted:
                st.markdown(jogo_row(j, show_fase=True), unsafe_allow_html=True)
        else:
            st.info("Nenhum resultado ainda.")

    divider()

    # Gráficos
    camps = listar_campeonatos()
    if not camps:
        return

    col3, col4 = st.columns(2)

    with col3:
        section_label("Jogos por Campeonato")
        dados_camps = []
        for c in camps[:8]:
            jgs = listar_jogos(cid=c["id"])
            dados_camps.append({"Campeonato": c["nome"][:20], "Jogos": len(jgs),
                                 "Finalizados": sum(1 for j in jgs if j["status"]=="Finalizado")})
        if dados_camps:
            df = pd.DataFrame(dados_camps)
            fig = px.bar(df, x="Campeonato", y=["Jogos","Finalizados"],
                         barmode="group", color_discrete_sequence=["#1e3a5f","#00e5ff"])
            fig.update_layout(**_plotly_layout())
            st.plotly_chart(fig, use_container_width=True)

    with col4:
        section_label("Top Artilheiros")
        arts = artilheiros(limit=10)
        if arts:
            df = pd.DataFrame(arts)
            fig = px.bar(df, x="gols", y="jogador", orientation="h",
                         color="gols", color_continuous_scale=["#1e3a5f","#00e5ff"],
                         labels={"gols":"Gols","jogador":""})
            fig.update_layout(**_plotly_layout())
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum gol registrado.")

    # Ranking geral
    divider()
    section_label("Ranking Geral — Campeonatos Ativos")
    for camp in [c for c in camps if c["status"]=="ativo"][:3]:
        with st.expander(f"🏆 {camp['nome']}"):
            classif = calcular_classificacao(camp["id"])
            if classif:
                df = pd.DataFrame(classif)[["equipe","pontos","jogos","vitorias",
                                             "empates","derrotas","saldo"]]
                df.columns = ["Equipe","PTS","PJ","V","E","D","SG"]
                df.index = range(1, len(df)+1)
                st.dataframe(df, use_container_width=True)

def _plotly_layout():
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(13,17,23,0.8)",
        font=dict(family="Rajdhani", color="#8090a0", size=11),
        margin=dict(l=10,r=10,t=10,b=10),
        xaxis=dict(gridcolor="#1a2535",zerolinecolor="#1a2535"),
        yaxis=dict(gridcolor="#1a2535",zerolinecolor="#1a2535"),
        showlegend=True,
        legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color="#8090a0")),
        coloraxis_showscale=False,
    )
