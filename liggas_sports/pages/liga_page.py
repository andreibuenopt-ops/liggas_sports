import streamlit as st
import json
from utils.database import listar_times, listar_jogos, get_campeonato
from utils.logica import gerar_rodadas_liga, calcular_classificacao

def render_rodadas(campeonato_id):
    camp = get_campeonato(campeonato_id)
    config = json.loads(camp.get("config") or "{}")
    ida_volta = config.get("ida_volta", True)

    st.markdown('<div class="xt-page-title">📅 Rodadas</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="xt-page-sub">{camp["nome"]}</div>', unsafe_allow_html=True)

    times = listar_times(campeonato_id)
    jogos = listar_jogos(campeonato_id)
    times_map = {t["id"]: t for t in times}

    if st.button("🎲 GERAR / RESETAR RODADAS", use_container_width=True, type="primary"):
        if len(times) < 2:
            st.error("Adicione pelo menos 2 times!")
        else:
            ok, msg = gerar_rodadas_liga(campeonato_id, ida_volta)
            st.success(msg) if ok else st.error(msg)
            st.rerun()

    if not jogos:
        st.info("Clique em **Gerar Rodadas** para criar o calendário.")
        return

    rodadas = sorted(set(j["rodada"] for j in jogos))
    rodada_sel = st.selectbox("Selecionar Rodada", rodadas, format_func=lambda r: f"Rodada {r}")
    jogos_rodada = [j for j in jogos if j["rodada"] == rodada_sel]

    pendentes_r = sum(1 for j in jogos_rodada if j["status"] == "pendente")
    realizados_r = sum(1 for j in jogos_rodada if j["status"] == "realizado")

    c1, c2 = st.columns(2)
    c1.metric("Pendentes", pendentes_r)
    c2.metric("Realizados", realizados_r)

    st.markdown("<hr class='xt-divider'>", unsafe_allow_html=True)

    for j in jogos_rodada:
        t1 = times_map.get(j["time1_id"], {})
        t2 = times_map.get(j["time2_id"], {})
        cor1 = t1.get("cor", "#0066ff")
        cor2 = t2.get("cor", "#00e5ff")
        nome1 = t1.get("nome", "?")
        nome2 = t2.get("nome", "?")
        p1 = j["placar1"]
        p2 = j["placar2"]
        placar = f"{p1}  ×  {p2}" if p1 is not None else "VS"
        status_cor = "#00e5ff" if j["status"] == "realizado" else "#ffaa00"

        st.markdown(f"""
        <div style="background:#0d1a2d;border:1px solid #1e3a5f;border-radius:6px;
             padding:12px 18px;margin-bottom:8px;display:flex;
             align-items:center;justify-content:space-between">
            <div style="display:flex;align-items:center;gap:10px;flex:1">
                <div style="width:10px;height:10px;border-radius:50%;background:{cor1}"></div>
                <span style="font-family:'Rajdhani',sans-serif;font-weight:700;
                      font-size:0.95rem;color:#e0e6f0">{nome1}</span>
            </div>
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.1rem;
                 font-weight:800;color:#607080;padding:0 20px;letter-spacing:2px">{placar}</div>
            <div style="display:flex;align-items:center;gap:10px;flex:1;justify-content:flex-end">
                <span style="font-family:'Rajdhani',sans-serif;font-weight:700;
                      font-size:0.95rem;color:#e0e6f0">{nome2}</span>
                <div style="width:10px;height:10px;border-radius:50%;background:{cor2}"></div>
            </div>
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:0.65rem;
                 font-weight:700;letter-spacing:2px;color:{status_cor};
                 margin-left:16px;min-width:70px;text-align:right">
                {j['status'].upper()}</div>
        </div>
        """, unsafe_allow_html=True)


def render_classificacao(campeonato_id):
    camp = get_campeonato(campeonato_id)
    st.markdown('<div class="xt-page-title">🏆 Classificação</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="xt-page-sub">{camp["nome"]}</div>', unsafe_allow_html=True)

    classif = calcular_classificacao(campeonato_id)
    if not classif:
        st.info("Nenhum jogo realizado ainda.")
        return

    medals = ["🥇", "🥈", "🥉"]
    if len(classif) >= 1:
        cols = st.columns(min(3, len(classif)))
        for i, (col, entry) in enumerate(zip(cols, classif[:3])):
            with col:
                st.metric(f"{medals[i]} {i+1}º lugar", entry["time"],
                          f"{entry['PTS']} pts  |  SG {entry['SG']:+d}")

    st.markdown("<hr class='xt-divider'>", unsafe_allow_html=True)

    # Tabela estilizada
    header = ["#", "TIME", "PJ", "V", "E", "D", "GP", "GC", "SG", "PTS"]
    header_html = "".join(
        f'<th style="padding:8px 12px;text-align:{"left" if h=="TIME" else "center"};'
        f'font-family:Barlow Condensed,sans-serif;font-size:0.7rem;letter-spacing:2px;'
        f'text-transform:uppercase;color:#405060;font-weight:700;border-bottom:1px solid #1e2a3a">'
        f'{h}</th>' for h in header
    )

    rows_html = ""
    for i, row in enumerate(classif, 1):
        cor = row.get("cor", "#0066ff")
        bg = "#0d1a2d" if i % 2 == 0 else "transparent"
        pts_color = "#00e5ff" if i == 1 else "#e0e6f0"
        sg_color  = "#00e564" if row["SG"] > 0 else ("#ff5050" if row["SG"] < 0 else "#607080")
        rows_html += f"""
        <tr style="background:{bg}">
            <td style="padding:8px 12px;text-align:center;font-family:Barlow Condensed,sans-serif;
                 font-size:0.8rem;font-weight:700;color:#304050">{i}</td>
            <td style="padding:8px 12px;text-align:left">
                <div style="display:flex;align-items:center;gap:8px">
                    <div style="width:8px;height:8px;border-radius:50%;background:{cor}"></div>
                    <span style="font-family:Rajdhani,sans-serif;font-weight:700;
                          font-size:0.95rem;color:#e0e6f0">{row['time']}</span>
                </div>
            </td>
            <td style="padding:8px 12px;text-align:center;font-family:Barlow Condensed,sans-serif;font-size:0.85rem;color:#607080">{row['PJ']}</td>
            <td style="padding:8px 12px;text-align:center;font-family:Barlow Condensed,sans-serif;font-size:0.85rem;color:#00e564">{row['V']}</td>
            <td style="padding:8px 12px;text-align:center;font-family:Barlow Condensed,sans-serif;font-size:0.85rem;color:#607080">{row['E']}</td>
            <td style="padding:8px 12px;text-align:center;font-family:Barlow Condensed,sans-serif;font-size:0.85rem;color:#ff5050">{row['D']}</td>
            <td style="padding:8px 12px;text-align:center;font-family:Barlow Condensed,sans-serif;font-size:0.85rem;color:#607080">{row['GP']}</td>
            <td style="padding:8px 12px;text-align:center;font-family:Barlow Condensed,sans-serif;font-size:0.85rem;color:#607080">{row['GC']}</td>
            <td style="padding:8px 12px;text-align:center;font-family:Barlow Condensed,sans-serif;font-size:0.85rem;color:{sg_color};font-weight:700">{row['SG']:+d}</td>
            <td style="padding:8px 12px;text-align:center;font-family:Barlow Condensed,sans-serif;font-size:1rem;font-weight:800;color:{pts_color}">{row['PTS']}</td>
        </tr>"""

    st.markdown(f"""
    <div style="border:1px solid #1e2a3a;border-radius:8px;overflow:hidden">
        <table style="width:100%;border-collapse:collapse">
            <thead><tr>{header_html}</tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)
