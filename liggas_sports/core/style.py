CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Barlow+Condensed:wght@400;600;700;800&display=swap');
html,body,[data-testid="stAppViewContainer"]{background:#090b10!important;color:#e0e6f0!important}
[data-testid="stSidebar"]{background:#0d1117!important;border-right:1px solid #1a2535!important}
.block-container{padding-top:1.2rem!important}
input,textarea,[data-baseweb="select"]>div{background:#111827!important;border:1px solid #1e3a5f!important;color:#e0e6f0!important;border-radius:6px!important}
input:focus,textarea:focus{border-color:#00e5ff!important;box-shadow:0 0 0 2px rgba(0,229,255,.12)!important}
[data-baseweb="select"] *{color:#e0e6f0!important;background:#111827!important}
.stButton>button{background:linear-gradient(135deg,#0044cc,#00e5ff)!important;color:#000!important;font-family:'Barlow Condensed',sans-serif!important;font-weight:700!important;letter-spacing:1.5px!important;text-transform:uppercase!important;border:none!important;border-radius:4px!important;font-size:.88rem!important;transition:all .2s!important}
.stButton>button:hover{transform:translateY(-1px)!important;box-shadow:0 4px 20px rgba(0,229,255,.3)!important}
.stButton>button[kind="secondary"]{background:#1a2535!important;color:#8090a0!important;border:1px solid #2a3a50!important}
[data-testid="stTabs"] [role="tablist"]{background:#0d1117!important;border-bottom:1px solid #1a2535!important}
[data-testid="stTabs"] button[role="tab"]{font-family:'Barlow Condensed',sans-serif!important;font-weight:700!important;font-size:.78rem!important;letter-spacing:1.5px!important;text-transform:uppercase!important;color:#506070!important;border-bottom:2px solid transparent!important}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"]{color:#00e5ff!important;border-bottom:2px solid #00e5ff!important;background:transparent!important}
[data-testid="metric-container"]{background:#0d1a2d!important;border:1px solid #1e3a5f!important;border-radius:8px!important;padding:.9rem!important}
[data-testid="metric-container"] label{color:#506070!important;font-family:'Barlow Condensed',sans-serif!important;letter-spacing:1.5px!important;text-transform:uppercase!important;font-size:.68rem!important}
[data-testid="metric-container"] [data-testid="stMetricValue"]{color:#00e5ff!important;font-family:'Barlow Condensed',sans-serif!important;font-size:1.8rem!important;font-weight:800!important}
[data-testid="stExpander"]{background:#0d1117!important;border:1px solid #1a2535!important;border-radius:6px!important}
[data-testid="stExpander"] summary{color:#c0d0e0!important;font-family:'Barlow Condensed',sans-serif!important}
[data-testid="stSelectbox"] label,[data-testid="stTextInput"] label,[data-testid="stNumberInput"] label,
[data-testid="stTextArea"] label,[data-testid="stCheckbox"] label,[data-testid="stRadio"] label,
[data-testid="stDateInput"] label{color:#506070!important;font-family:'Barlow Condensed',sans-serif!important;font-size:.7rem!important;letter-spacing:1.5px!important;text-transform:uppercase!important}
[data-testid="stForm"]{background:#0d1117!important;border:1px solid #1a2535!important;border-radius:8px!important;padding:1rem!important}
hr{border-color:#1a2535!important}

.ifc-logo{font-family:'Barlow Condensed',sans-serif;font-size:1.5rem;font-weight:800;letter-spacing:4px;background:linear-gradient(90deg,#0066ff,#00e5ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.ifc-logo-sub{font-family:Rajdhani,sans-serif;font-size:.58rem;letter-spacing:4px;color:#304050;text-transform:uppercase}
.ifc-h1{font-family:'Barlow Condensed',sans-serif;font-size:2rem;font-weight:800;letter-spacing:2px;text-transform:uppercase;color:#fff;line-height:1}
.ifc-h2{font-family:'Barlow Condensed',sans-serif;font-size:1.2rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#c0d0e0;margin:.8rem 0 .4rem}
.ifc-sub{font-family:Rajdhani,sans-serif;font-size:.9rem;color:#506070;margin-bottom:.8rem}
.ifc-div{border:none;height:1px;background:linear-gradient(90deg,#1e3a5f,transparent);margin:.9rem 0}
.ifc-lbl{font-family:'Barlow Condensed',sans-serif;font-size:.63rem;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#304050;margin-bottom:.4rem}
.ifc-card{background:linear-gradient(135deg,#0d1a2d,#0d1117);border:1px solid #1e3a5f;border-left:3px solid #00e5ff;border-radius:6px;padding:.9rem 1.1rem;margin-bottom:.5rem;transition:.2s}
.ifc-card:hover{border-left-color:#0066ff;box-shadow:0 4px 16px rgba(0,102,255,.12)}
.ifc-badge{display:inline-block;padding:2px 8px;border-radius:2px;font-size:.62rem;font-family:'Barlow Condensed',sans-serif;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin-right:4px}
.ifc-badge-ok{background:rgba(0,229,255,.1);color:#00e5ff;border:1px solid #00e5ff30}
.ifc-badge-pend{background:rgba(255,170,0,.1);color:#ffaa00;border:1px solid #ffaa0030}
.ifc-badge-fin{background:rgba(0,229,100,.1);color:#00e564;border:1px solid #00e56430}
.ifc-jogo{background:#0d1a2d;border:1px solid #1e3a5f;border-radius:6px;padding:9px 14px;margin-bottom:5px;display:flex;align-items:center;justify-content:space-between}
.ifc-tnm{font-family:Rajdhani,sans-serif;font-weight:700;font-size:.92rem;color:#c0d0e0}
.ifc-sc{font-family:'Barlow Condensed',sans-serif;font-size:1.05rem;font-weight:800;color:#405060;letter-spacing:2px;padding:0 12px}
.ifc-tbl{width:100%;border-collapse:collapse}
.ifc-tbl th{padding:7px 9px;text-align:center;font-family:'Barlow Condensed',sans-serif;font-size:.62rem;letter-spacing:2px;text-transform:uppercase;color:#304050;border-bottom:1px solid #1a2535;font-weight:700}
.ifc-tbl td{padding:6px 9px;text-align:center;font-family:'Barlow Condensed',sans-serif;font-size:.8rem;border-bottom:1px solid #0f1a28}
.ifc-tbl tr:hover td{background:#0d1a2d!important}
.ifc-grp-hdr{font-family:'Barlow Condensed',sans-serif;font-weight:800;font-size:.95rem;letter-spacing:3px;color:#00e5ff;margin-bottom:8px;border-bottom:1px solid #1e3a5f;padding-bottom:5px}
.ifc-bracket-fase{font-family:'Barlow Condensed',sans-serif;font-size:.65rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#00e5ff;margin-bottom:8px;border-bottom:1px solid #1e3a5f;padding-bottom:5px}
.ifc-bracket-card{background:#0d1a2d;border:1px solid #1e3a5f;border-radius:4px;padding:7px 11px;margin-bottom:5px;border-left:2px solid #1e3a5f}
.ifc-mt{font-family:Rajdhani,sans-serif;font-size:.82rem;font-weight:600}
.ifc-ms{font-family:'Barlow Condensed',sans-serif;font-size:.68rem;color:#304050;text-align:center;padding:2px 0;letter-spacing:1px}
</style>
"""

def inject(st): st.markdown(CSS, unsafe_allow_html=True)
def h1(st, t, sub=""): 
    st.markdown(f'<div class="ifc-h1">{t}</div>', unsafe_allow_html=True)
    if sub: st.markdown(f'<div class="ifc-sub">{sub}</div>', unsafe_allow_html=True)
def h2(st, t): st.markdown(f'<div class="ifc-h2">{t}</div>', unsafe_allow_html=True)
def div(st): st.markdown("<hr class='ifc-div'>", unsafe_allow_html=True)
def lbl(st, t): st.markdown(f'<div class="ifc-lbl">{t}</div>', unsafe_allow_html=True)

def jogo_row(j, show_grupo=False):
    gc = j.get("gols_casa")
    gf = j.get("gols_fora")
    placar = f"{gc} × {gf}" if gc is not None else "VS"
    s_cor = {"Finalizado":"#00e5ff","Agendado":"#ffaa00","Em Andamento":"#00e564"}.get(j.get("status",""),"#607080")
    grupo_tag = f'<span style="font-family:Barlow Condensed,sans-serif;font-size:.62rem;color:#304050;margin-right:8px">Grp {j.get("grupo","")} R{j.get("rodada","")}</span>' if show_grupo else f'<span style="font-family:Barlow Condensed,sans-serif;font-size:.62rem;color:#304050;margin-right:8px">R{j.get("rodada","")}</span>'
    return f"""
    <div class="ifc-jogo">
        <div style="display:flex;align-items:center;gap:8px;flex:1">{grupo_tag}
            <span class="ifc-tnm">{j.get('casa','BYE')}</span></div>
        <div style="text-align:center">
            <div class="ifc-sc">{placar}</div>
            <div style="font-family:Barlow Condensed,sans-serif;font-size:.58rem;letter-spacing:2px;color:{s_cor}">{j.get('status','').upper()}</div>
        </div>
        <div style="display:flex;align-items:center;gap:8px;flex:1;justify-content:flex-end">
            <span class="ifc-tnm">{j.get('fora','BYE')}</span></div>
    </div>"""

def classif_table(rows, destaque=2):
    medals = {1:"🥇",2:"🥈",3:"🥉"}
    hdr = "".join(f"<th>{h}</th>" for h in ["#","TIME","J","V","E","D","GP","GC","SG","P","%"])
    body = ""
    for i, r in enumerate(rows, 1):
        bg = "#0d1a2d" if i%2==0 else "transparent"
        bord = "border-left:3px solid #00e5ff;" if i <= destaque else ""
        sg_cor = "#00e564" if r["SG"]>0 else ("#ff5050" if r["SG"]<0 else "#607080")
        p_cor = "#00e5ff" if i==1 else "#e0e6f0"
        body += f"""<tr style="background:{bg};{bord}">
            <td style="color:#304050;font-weight:700">{medals.get(i,i)}</td>
            <td style="text-align:left;padding-left:8px;font-family:Rajdhani,sans-serif;font-weight:700;color:#e0e6f0">{r['time']}</td>
            <td style="color:#607080">{r['J']}</td>
            <td style="color:#00e564">{r['V']}</td>
            <td style="color:#607080">{r['E']}</td>
            <td style="color:#ff5050">{r['D']}</td>
            <td style="color:#607080">{r['GP']}</td>
            <td style="color:#607080">{r['GC']}</td>
            <td style="color:{sg_cor};font-weight:700">{r['SG']:+d}</td>
            <td style="color:{p_cor};font-weight:800;font-size:.9rem">{r['P']}</td>
            <td style="color:#607080">{r['pct']}%</td>
        </tr>"""
    return f'<table class="ifc-tbl"><thead><tr>{hdr}</tr></thead><tbody>{body}</tbody></table>'

def bracket_card(j):
    gc, gf = j.get("gols_casa"), j.get("gols_fora")
    t1, t2 = j.get("casa","BYE"), j.get("fora","BYE")
    if j.get("status") == "Finalizado" and gc is not None:
        v1 = gc > gf; v2 = gf > gc
        c1 = "#00e5ff" if v1 else "#304050"; c2 = "#00e5ff" if v2 else "#304050"
        fw1 = "700" if v1 else "400"; fw2 = "700" if v2 else "400"
        if j.get("ida_volta") and j.get("gols_casa_volta") is not None:
            a1 = (gc or 0) + (j.get("gols_fora_volta") or 0)
            a2 = (gf or 0) + (j.get("gols_casa_volta") or 0)
            placar = f"{gc}-{gf} / {j.get('gols_fora_volta')}-{j.get('gols_casa_volta')} (agg {a1}×{a2})"
            v1 = a1 >= a2; c1 = "#00e5ff" if v1 else "#304050"; c2 = "#00e5ff" if not v1 else "#304050"
            fw1 = "700" if v1 else "400"; fw2 = "700" if not v1 else "400"
        else:
            placar = f"{gc} × {gf}"
    else:
        c1 = c2 = "#607080"; fw1 = fw2 = "400"; placar = "VS"
    return f"""
    <div class="ifc-bracket-card">
        <div class="ifc-mt" style="color:{c1};font-weight:{fw1}">{t1}</div>
        <div class="ifc-ms">{placar}</div>
        <div class="ifc-mt" style="color:{c2};font-weight:{fw2}">{t2}</div>
    </div>"""
