import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Barlow+Condensed:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap');

html,body,[data-testid="stAppViewContainer"]{background:#090b10!important;color:#e0e6f0!important}
[data-testid="stSidebar"]{background:#0d1117!important;border-right:1px solid #1a2535!important}
.block-container{padding-top:1.2rem!important;padding-bottom:2rem!important}
section[data-testid="stSidebar"] .stRadio label{font-family:'Barlow Condensed',sans-serif!important;font-size:.9rem!important;letter-spacing:1px!important;color:#8090a0!important;padding:5px 8px!important;border-radius:4px!important;transition:.15s!important}
section[data-testid="stSidebar"] .stRadio label:hover{background:#1a2535!important;color:#00e5ff!important}
input,textarea,[data-baseweb="select"]>div,[data-baseweb="input"]{background:#111827!important;border:1px solid #1e3a5f!important;color:#e0e6f0!important;border-radius:6px!important}
input:focus,textarea:focus{border-color:#00e5ff!important;box-shadow:0 0 0 2px rgba(0,229,255,.12)!important}
[data-baseweb="select"] *,[data-baseweb="menu"] *{color:#e0e6f0!important;background:#111827!important}
.stButton>button{background:linear-gradient(135deg,#0044cc,#00e5ff)!important;color:#000!important;font-family:'Barlow Condensed',sans-serif!important;font-weight:700!important;letter-spacing:1.5px!important;text-transform:uppercase!important;border:none!important;border-radius:4px!important;transition:all .2s!important;font-size:.9rem!important}
.stButton>button:hover{transform:translateY(-1px)!important;box-shadow:0 4px 20px rgba(0,229,255,.3)!important}
.stButton>button[kind="secondary"]{background:#1a2535!important;color:#8090a0!important;border:1px solid #2a3a50!important}
[data-testid="stTabs"] [role="tablist"]{background:#0d1117!important;border-bottom:1px solid #1a2535!important;gap:2px!important}
[data-testid="stTabs"] button[role="tab"]{font-family:'Barlow Condensed',sans-serif!important;font-weight:700!important;font-size:.78rem!important;letter-spacing:1.5px!important;text-transform:uppercase!important;color:#506070!important;border-bottom:2px solid transparent!important;padding:.45rem .9rem!important}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"]{color:#00e5ff!important;border-bottom:2px solid #00e5ff!important;background:transparent!important}
[data-testid="metric-container"]{background:#0d1a2d!important;border:1px solid #1e3a5f!important;border-radius:8px!important;padding:.9rem!important}
[data-testid="metric-container"] label{color:#506070!important;font-family:'Barlow Condensed',sans-serif!important;letter-spacing:1.5px!important;text-transform:uppercase!important;font-size:.7rem!important}
[data-testid="metric-container"] [data-testid="stMetricValue"]{color:#00e5ff!important;font-family:'Barlow Condensed',sans-serif!important;font-size:1.9rem!important;font-weight:800!important}
[data-testid="stExpander"]{background:#0d1117!important;border:1px solid #1a2535!important;border-radius:6px!important}
[data-testid="stExpander"] summary{color:#c0d0e0!important;font-family:'Barlow Condensed',sans-serif!important;letter-spacing:.5px!important}
[data-testid="stSelectbox"] label,[data-testid="stTextInput"] label,[data-testid="stNumberInput"] label,
[data-testid="stTextArea"] label,[data-testid="stCheckbox"] label,[data-testid="stRadio"] label,
[data-testid="stDateInput"] label,[data-testid="stTimeInput"] label,[data-testid="stFileUploader"] label{
    color:#506070!important;font-family:'Barlow Condensed',sans-serif!important;
    font-size:.72rem!important;letter-spacing:1.5px!important;text-transform:uppercase!important}
[data-testid="stForm"]{background:#0d1117!important;border:1px solid #1a2535!important;border-radius:8px!important;padding:1rem!important}
[data-testid="stDataFrame"]{border:1px solid #1a2535!important;border-radius:6px!important}
hr{border-color:#1a2535!important}
[data-testid="stAlert"]{border-radius:6px!important;border-left-width:3px!important}
.stCheckbox span{color:#a0b0c0!important}

/* Custom classes */
.ls-logo{font-family:'Barlow Condensed',sans-serif;font-size:1.5rem;font-weight:800;letter-spacing:4px;text-transform:uppercase;background:linear-gradient(90deg,#0066ff,#00e5ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.ls-logo-sub{font-family:Rajdhani,sans-serif;font-size:.6rem;letter-spacing:4px;color:#304050;text-transform:uppercase}
.ls-h1{font-family:'Barlow Condensed',sans-serif;font-size:2rem;font-weight:800;letter-spacing:2px;text-transform:uppercase;color:#fff;line-height:1;margin-bottom:.25rem}
.ls-h2{font-family:'Barlow Condensed',sans-serif;font-size:1.3rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:#c0d0e0;margin:1rem 0 .5rem}
.ls-sub{font-family:Rajdhani,sans-serif;font-size:.95rem;color:#506070;letter-spacing:.5px;margin-bottom:1rem}
.ls-divider{border:none;height:1px;background:linear-gradient(90deg,#1e3a5f,transparent);margin:1rem 0}
.ls-label{font-family:'Barlow Condensed',sans-serif;font-size:.65rem;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#304050;margin-bottom:.5rem}
.ls-card{background:linear-gradient(135deg,#0d1a2d,#0d1117);border:1px solid #1e3a5f;border-left:3px solid #00e5ff;border-radius:6px;padding:1rem 1.2rem;margin-bottom:.6rem;transition:.2s}
.ls-card:hover{border-left-color:#0066ff;box-shadow:0 4px 16px rgba(0,102,255,.12)}
.ls-card-title{font-family:'Barlow Condensed',sans-serif;font-size:1rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#fff}
.ls-card-meta{font-family:Rajdhani,sans-serif;font-size:.82rem;color:#506070;margin-top:2px}
.ls-badge{display:inline-block;padding:2px 9px;border-radius:2px;font-size:.65rem;font-family:'Barlow Condensed',sans-serif;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin-right:4px}
.ls-badge-ativo{background:rgba(0,229,255,.1);color:#00e5ff;border:1px solid #00e5ff30}
.ls-badge-encerrado{background:rgba(255,50,50,.1);color:#ff5050;border:1px solid #ff505030}
.ls-badge-liga{background:rgba(0,229,100,.1);color:#00e564;border:1px solid #00e56430}
.ls-badge-mata{background:rgba(255,80,80,.1);color:#ff6060;border:1px solid #ff606030}
.ls-badge-grupos{background:rgba(255,170,0,.1);color:#ffaa00;border:1px solid #ffaa0030}
.ls-jogo-card{background:#0d1a2d;border:1px solid #1e3a5f;border-radius:6px;padding:10px 16px;margin-bottom:6px;display:flex;align-items:center;justify-content:space-between}
.ls-team-name{font-family:Rajdhani,sans-serif;font-weight:700;font-size:.95rem;color:#c0d0e0}
.ls-score{font-family:'Barlow Condensed',sans-serif;font-size:1.1rem;font-weight:800;color:#405060;letter-spacing:2px;padding:0 14px}
.ls-classif-table{width:100%;border-collapse:collapse}
.ls-classif-table th{padding:8px 10px;text-align:center;font-family:'Barlow Condensed',sans-serif;font-size:.65rem;letter-spacing:2px;text-transform:uppercase;color:#304050;border-bottom:1px solid #1a2535;font-weight:700}
.ls-classif-table td{padding:7px 10px;text-align:center;font-family:'Barlow Condensed',sans-serif;font-size:.82rem;border-bottom:1px solid #0f1a28}
.ls-classif-table tr:hover td{background:#0d1a2d!important}
</style>
"""

def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)

def page_header(title, subtitle=""):
    st.markdown(f'<div class="ls-h1">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="ls-sub">{subtitle}</div>', unsafe_allow_html=True)

def divider():
    st.markdown("<hr class='ls-divider'>", unsafe_allow_html=True)

def section_label(txt):
    st.markdown(f'<div class="ls-label">{txt}</div>', unsafe_allow_html=True)

def badge(txt, tipo="ativo"):
    return f'<span class="ls-badge ls-badge-{tipo}">{txt}</span>'

def jogo_row(j, show_fase=False):
    p1 = j["placar1"]
    p2 = j["placar2"]
    placar = f"{p1} × {p2}" if p1 is not None else "VS"
    s_cor = {"Finalizado":"#00e5ff","Em Andamento":"#00e564",
              "Agendado":"#ffaa00","Suspenso":"#ff9900","Cancelado":"#ff5050"
              }.get(j["status"],"#607080")
    fase_tag = f'<span style="font-size:.65rem;color:#304050;margin-right:8px">{j["fase"]}</span>' if show_fase else ""
    return f"""
    <div class="ls-jogo-card">
        <div style="display:flex;align-items:center;gap:8px;flex:1">
            <div style="width:8px;height:8px;border-radius:50%;background:{j['cor1']}"></div>
            <span class="ls-team-name">{j['equipe1']}</span>
        </div>
        <div style="text-align:center">
            {fase_tag}
            <div class="ls-score">{placar}</div>
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:.6rem;letter-spacing:2px;color:{s_cor}">{j['status'].upper()}</div>
        </div>
        <div style="display:flex;align-items:center;gap:8px;flex:1;justify-content:flex-end">
            <span class="ls-team-name">{j['equipe2']}</span>
            <div style="width:8px;height:8px;border-radius:50%;background:{j['cor2']}"></div>
        </div>
    </div>"""

def classif_table(rows, highlight=2):
    medals = {1:"🥇",2:"🥈",3:"🥉"}
    header = "<tr>" + "".join(f"<th>{h}</th>" for h in
        ["#","EQUIPE","PJ","V","E","D","GP","GC","SG","PTS","APROV."]) + "</tr>"
    body = ""
    for i, r in enumerate(rows, 1):
        bg = "#0d1a2d" if i%2==0 else "transparent"
        borda = "border-left:3px solid #00e5ff;" if i <= highlight else ""
        pts_cor = "#00e5ff" if i==1 else "#e0e6f0"
        sg_cor = "#00e564" if r["saldo"]>0 else ("#ff5050" if r["saldo"]<0 else "#607080")
        medal = medals.get(i,"")
        body += f"""<tr style="background:{bg};{borda}">
            <td style="color:#304050;font-weight:700">{medal or i}</td>
            <td style="text-align:left;padding-left:8px">
                <div style="display:flex;align-items:center;gap:6px">
                    <div style="width:8px;height:8px;border-radius:50%;background:{r['cor']}"></div>
                    <span style="font-family:Rajdhani,sans-serif;font-weight:700;color:#e0e6f0">{r['equipe']}</span>
                </div>
            </td>
            <td style="color:#607080">{r['jogos']}</td>
            <td style="color:#00e564">{r['vitorias']}</td>
            <td style="color:#607080">{r['empates']}</td>
            <td style="color:#ff5050">{r['derrotas']}</td>
            <td style="color:#607080">{r['gols_pro']}</td>
            <td style="color:#607080">{r['gols_contra']}</td>
            <td style="color:{sg_cor};font-weight:700">{r['saldo']:+d}</td>
            <td style="color:{pts_cor};font-weight:800;font-size:.95rem">{r['pontos']}</td>
            <td style="color:#607080">{r['aproveitamento']}%</td>
        </tr>"""
    return f'<table class="ls-classif-table">{header}{body}</table>'
