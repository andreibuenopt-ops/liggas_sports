import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from core import engine, style

def _layout():
    return dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,17,23,.8)",
                font=dict(family="Rajdhani", color="#8090a0", size=10),
                margin=dict(l=5,r=5,t=10,b=5), coloraxis_showscale=False,
                xaxis=dict(gridcolor="#1a2535"), yaxis=dict(gridcolor="#1a2535"),
                legend=dict(bgcolor="rgba(0,0,0,0)"))

def render():
    style.h1(st, "🏠 Dashboard", "Visão geral do campeonato")

    cfg = engine.get_config()
    if not cfg:
        _tela_boas_vindas()
        return

    times   = engine.get_times()
    jogs    = engine.get_jogadores()
    todos   = engine.get_jogos()
    finalizados = [j for j in todos if j.get("status") == "Finalizado"]
    pendentes   = [j for j in todos if j.get("status") == "Agendado"
                   and j.get("casa") and j.get("fora")]

    total_gols = sum((j.get("gols_casa") or 0) + (j.get("gols_fora") or 0)
                     for j in finalizados)
    media_gols = round(total_gols / max(len(finalizados), 1), 2)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Times",         len(times))
    c2.metric("Jogadores",     len(jogs))
    c3.metric("Total de Jogos", len(todos))
    c4.metric("Realizados",    len(finalizados))
    c5.metric("Total de Gols", total_gols)
    c6.metric("Média Gols/Jogo", media_gols)

    style.div(st)

    col1, col2 = st.columns([1.1, 1])

    # Próximos jogos
    with col1:
        style.lbl(st, f"Próximos Jogos ({len(pendentes)} pendentes)")
        if pendentes:
            for j in pendentes[:8]:
                st.markdown(style.jogo_row(j, show_grupo=True), unsafe_allow_html=True)
        else:
            st.info("Nenhum jogo agendado.")

    # Últimos resultados
    with col2:
        style.lbl(st, "Últimos Resultados")
        ultimos = sorted(finalizados, key=lambda x: x.get("id",""), reverse=True)[:8]
        if ultimos:
            for j in ultimos:
                st.markdown(style.jogo_row(j, show_grupo=True), unsafe_allow_html=True)
        else:
            st.info("Nenhum resultado registrado.")

    style.div(st)

    # Gráficos
    col3, col4 = st.columns(2)

    with col3:
        style.lbl(st, "Jogos por Fase")
        fases_count = {}
        for j in todos:
            f = j.get("fase","")
            fases_count[f] = fases_count.get(f, 0) + 1
        if fases_count:
            df_f = pd.DataFrame(
                [{"Fase": k, "Total": v} for k, v in fases_count.items()])
            fig = px.bar(df_f, x="Fase", y="Total",
                         color="Total",
                         color_continuous_scale=["#1e3a5f","#00e5ff"])
            fig.update_layout(**_layout())
            st.plotly_chart(fig, use_container_width=True)

    with col4:
        style.lbl(st, "Gols por Rodada")
        rodadas_gols = {}
        for j in finalizados:
            r = j.get("rodada", 1)
            rodadas_gols[r] = rodadas_gols.get(r, 0) + \
                              (j.get("gols_casa") or 0) + (j.get("gols_fora") or 0)
        if rodadas_gols:
            df_r = pd.DataFrame(
                sorted([{"Rodada": k, "Gols": v} for k, v in rodadas_gols.items()],
                       key=lambda x: x["Rodada"]))
            fig2 = px.line(df_r, x="Rodada", y="Gols",
                           markers=True,
                           color_discrete_sequence=["#00e5ff"])
            fig2.update_layout(**_layout())
            st.plotly_chart(fig2, use_container_width=True)

    # Classificação resumida
    style.div(st)
    fmt = cfg.get("formato","")

    if "Grupo" in fmt or "Chaves" in fmt:
        style.lbl(st, "Classificação por Grupo")
        grupos_c = engine.get_grupos_classificacao()
        if grupos_c:
            cols_g = st.columns(min(4, len(grupos_c)))
            for col, (g, tabela) in zip(cols_g, grupos_c.items()):
                with col:
                    st.markdown(f'<div class="ifc-grp-hdr">GRUPO {g}</div>',
                                unsafe_allow_html=True)
                    st.markdown(style.classif_table(
                        tabela, cfg.get("classificados_por_grupo", 2)),
                        unsafe_allow_html=True)
    else:
        style.lbl(st, "Classificação")
        tabela = engine.calcular_classificacao()
        if tabela:
            st.markdown(style.classif_table(tabela[:8], 3), unsafe_allow_html=True)

    # Artilheiros
    arts = engine.artilheiros()
    if arts:
        style.div(st)
        style.lbl(st, "Top Artilheiros")
        col_a, _ = st.columns([1, 2])
        with col_a:
            for i, a in enumerate(arts[:5], 1):
                medal = {1:"🥇",2:"🥈",3:"🥉"}.get(i,"")
                st.markdown(
                    f'<div style="display:flex;justify-content:space-between;'
                    f'padding:5px 0;border-bottom:1px solid #0d1a2d">'
                    f'<span style="font-family:Rajdhani,sans-serif;color:#c0d0e0">'
                    f'{medal or i}. {a["nome"]}'
                    f'<span style="color:#405060;font-size:.78rem"> · {a["equipe"]}</span>'
                    f'</span>'
                    f'<span style="font-family:Barlow Condensed,sans-serif;'
                    f'font-weight:800;color:#00e5ff">{a["gols"]}</span>'
                    f'</div>',
                    unsafe_allow_html=True)

    # Campeão
    camp = engine.campeao()
    if camp:
        style.div(st)
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0d1a2d,#1a2d10);
             border:2px solid #ffaa00;border-radius:10px;padding:18px;
             text-align:center;box-shadow:0 0 30px rgba(255,170,0,.2)">
            <div style="font-size:2.2rem">🏆</div>
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:.62rem;
                 letter-spacing:4px;color:#806030;text-transform:uppercase">
                CAMPEÃO</div>
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:2rem;
                 font-weight:800;color:#ffaa00;letter-spacing:3px;
                 text-transform:uppercase">{camp}</div>
        </div>""", unsafe_allow_html=True)


def _tela_boas_vindas():
    st.markdown("""
    <div style="text-align:center;padding:3rem 0 2rem">
        <div style="font-size:4rem">⚽</div>
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:2.5rem;
             font-weight:800;letter-spacing:4px;text-transform:uppercase;
             background:linear-gradient(90deg,#0066ff,#00e5ff);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent;
             margin-bottom:6px">Basic IFC</div>
        <div style="font-family:Rajdhani,sans-serif;color:#506070;font-size:1rem;
             letter-spacing:2px">Gerenciador de Campeonatos · Python Edition</div>
    </div>""", unsafe_allow_html=True)

    style.div(st)
    style.lbl(st, "Formatos disponíveis")

    formatos = [
        ("🏆", "Pontos Corridos", "Liga clássica com tabela automática. Ida e volta opcional."),
        ("🌍", "Grupos",          "Fase de grupos estilo Copa do Mundo. Sorteio por potes ou aleatório."),
        ("⚔️", "Chaves Cruzadas", "2 grupos cruzados + mata-mata completo com disputa de 3º lugar."),
        ("🔀", "Pontos Corridos + Mata-Mata", "Fase de liga seguida de eliminatórias com os classificados."),
        ("💥", "Eliminatórias",   "Mata-mata puro, jogo único ou ida e volta por fase."),
    ]

    cols = st.columns(len(formatos))
    for col, (icone, nome, desc) in zip(cols, formatos):
        with col:
            st.markdown(f"""
            <div style="background:#0d1a2d;border:1px solid #1e3a5f;
                 border-radius:8px;padding:14px 12px;text-align:center;height:140px">
                <div style="font-size:1.6rem">{icone}</div>
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:.85rem;
                     font-weight:700;color:#e0e6f0;letter-spacing:1px;
                     text-transform:uppercase;margin:6px 0 4px">{nome}</div>
                <div style="font-family:Rajdhani,sans-serif;font-size:.75rem;
                     color:#405060">{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;margin-top:2rem">
        <div style="font-family:Rajdhani,sans-serif;color:#304050;font-size:.9rem">
            👈 Clique em <strong style="color:#00e5ff">⚙️ Configurar</strong>
            no menu lateral para criar seu campeonato
        </div>
    </div>""", unsafe_allow_html=True)
