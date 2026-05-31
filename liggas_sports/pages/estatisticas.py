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

    style.h1(st, "📈 Estatísticas", cfg.get("nome",""))

    jogadores = engine.get_jogadores()
    times = engine.get_times()
    jogos_fin = engine.get_jogos(status="Finalizado")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Times", len(times))
    c2.metric("Jogadores", len(jogadores))
    c3.metric("Jogos realizados", len(jogos_fin))
    total_gols = sum((j.get("gols_casa") or 0) + (j.get("gols_fora") or 0) for j in jogos_fin)
    c4.metric("Total de Gols", total_gols)

    style.div(st)

    tab1, tab2, tab3, tab4 = st.tabs(["⚽ Artilharia", "🟨 Cartões", "📊 Por Time", "🔍 Por Jogador"])

    with tab1:
        arts = engine.artilheiros()
        if arts:
            df = pd.DataFrame(arts)
            col1, col2 = st.columns([1, 1])
            with col1:
                style.lbl(st, "Artilheiros")
                for i, a in enumerate(arts, 1):
                    medal = {1:"🥇",2:"🥈",3:"🥉"}.get(i,"")
                    st.markdown(
                        f'<div style="display:flex;justify-content:space-between;'
                        f'padding:6px 0;border-bottom:1px solid #0d1a2d">'
                        f'<span style="font-family:Rajdhani,sans-serif;color:#c0d0e0">'
                        f'{medal or i}. {a["nome"]}'
                        f'<span style="color:#405060;font-size:.8rem"> · {a["equipe"]}</span></span>'
                        f'<span style="font-family:Barlow Condensed,sans-serif;font-weight:800;'
                        f'color:#00e5ff">{a["gols"]}</span></div>',
                        unsafe_allow_html=True)
            with col2:
                fig = px.bar(df.head(10), x="gols", y="nome", orientation="h",
                             color="gols", color_continuous_scale=["#1e3a5f","#00e5ff"])
                fig.update_layout(**_layout())
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum gol registrado via eventos. Cadastre jogadores e registre eventos nos jogos.")

    with tab2:
        evs = engine.get_eventos()
        jog_map = {j["id"]: j for j in jogadores}
        amarelos = {}; vermelhos = {}
        for e in evs:
            jid = e["jogador_id"]
            if jid not in jog_map: continue
            nome = jog_map[jid]["nome"]
            eq = jog_map[jid].get("equipe","")
            if e["tipo"] == "amarelo":
                amarelos[nome] = amarelos.get(nome, {"nome":nome,"equipe":eq,"total":0})
                amarelos[nome]["total"] += 1
            elif e["tipo"] == "vermelho":
                vermelhos[nome] = vermelhos.get(nome, {"nome":nome,"equipe":eq,"total":0})
                vermelhos[nome]["total"] += 1

        col1, col2 = st.columns(2)
        with col1:
            style.lbl(st, "🟨 Amarelos")
            for r in sorted(amarelos.values(), key=lambda x: -x["total"]):
                st.markdown(f'<div style="display:flex;justify-content:space-between;'
                            f'padding:5px 0;border-bottom:1px solid #0d1a2d;'
                            f'font-family:Rajdhani,sans-serif;color:#c0d0e0">'
                            f'{r["nome"]} <span style="color:#405060;font-size:.8rem">· {r["equipe"]}</span>'
                            f'<span style="color:#ffaa00;font-weight:700;float:right">{r["total"]}</span>'
                            f'</div>', unsafe_allow_html=True)
        with col2:
            style.lbl(st, "🟥 Vermelhos")
            for r in sorted(vermelhos.values(), key=lambda x: -x["total"]):
                st.markdown(f'<div style="display:flex;justify-content:space-between;'
                            f'padding:5px 0;border-bottom:1px solid #0d1a2d;'
                            f'font-family:Rajdhani,sans-serif;color:#c0d0e0">'
                            f'{r["nome"]} <span style="color:#405060;font-size:.8rem">· {r["equipe"]}</span>'
                            f'<span style="color:#ff5050;font-weight:700;float:right">{r["total"]}</span>'
                            f'</div>', unsafe_allow_html=True)

    with tab3:
        style.lbl(st, "Desempenho por time")
        tabela = engine.calcular_classificacao()
        if tabela:
            df = pd.DataFrame(tabela)
            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(df, x="time", y=["V","E","D"], barmode="stack",
                             color_discrete_sequence=["#00e564","#ffaa00","#ff5050"],
                             labels={"value":"Jogos","time":""})
                fig.update_layout(**_layout(), title=None)
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig2 = px.scatter(df, x="GP", y="GC", text="time", size="P",
                                  color="P", color_continuous_scale=["#1e3a5f","#00e5ff"],
                                  labels={"GP":"Gols Pró","GC":"Gols Contra"})
                fig2.update_traces(textposition="top center",
                                   textfont=dict(color="#c0d0e0", size=10))
                fig2.update_layout(**_layout())
                st.plotly_chart(fig2, use_container_width=True)

    with tab4:
        if jogadores:
            opts = {j["nome"]: j for j in jogadores}
            sel = st.selectbox("Jogador", list(opts.keys()))
            j = opts[sel]
            eq = j.get("equipe","")
            evs_j = [e for e in evs if e["jogador_id"] == j["id"]]
            gols_j = sum(1 for e in evs_j if e["tipo"] == "gol")
            assist_j = sum(1 for e in evs_j if e["tipo"] == "assist")
            am_j = sum(1 for e in evs_j if e["tipo"] == "amarelo")
            vm_j = sum(1 for e in evs_j if e["tipo"] == "vermelho")

            c1,c2,c3,c4 = st.columns(4)
            c1.metric("⚽ Gols", gols_j)
            c2.metric("🎯 Assistências", assist_j)
            c3.metric("🟨 Amarelos", am_j)
            c4.metric("🟥 Vermelhos", vm_j)
        else:
            st.info("Nenhum jogador cadastrado.")
