import streamlit as st
import io
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from services.services import (listar_campeonatos, calcular_classificacao,
                                listar_jogos, artilheiros, get_campeonato)
from utils.style import page_header, divider, section_label

def render():
    page_header("📄 Relatórios", "Exporte dados em Excel e PDF")

    camps = listar_campeonatos()
    if not camps:
        st.info("Nenhum campeonato cadastrado.")
        return

    opcoes = {c["nome"]: c["id"] for c in camps}
    sel = st.selectbox("Campeonato", list(opcoes.keys()))
    cid = opcoes[sel]
    camp = get_campeonato(cid)

    divider()
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div style="background:#0d1a2d;border:1px solid #1e3a5f;border-radius:8px;
             padding:24px;text-align:center;margin-bottom:12px">
            <div style="font-size:2.5rem">📊</div>
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.1rem;
                 font-weight:800;letter-spacing:2px;color:#e0e6f0;margin:8px 0 4px">EXCEL</div>
            <div style="font-family:Rajdhani,sans-serif;font-size:.85rem;color:#405060">
                Classificação · Jogos · Artilheiros · Estatísticas
            </div>
        </div>""", unsafe_allow_html=True)
        try:
            buf = _gerar_excel(cid, camp)
            st.download_button("⬇️ BAIXAR EXCEL", data=buf,
                file_name=f"{camp['nome'].replace(' ','_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True, type="primary")
        except Exception as e:
            st.error(f"Erro: {e}")

    with col2:
        st.markdown("""
        <div style="background:#0d1a2d;border:1px solid #1e3a5f;border-radius:8px;
             padding:24px;text-align:center;margin-bottom:12px">
            <div style="font-size:2.5rem">📄</div>
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.1rem;
                 font-weight:800;letter-spacing:2px;color:#e0e6f0;margin:8px 0 4px">PDF</div>
            <div style="font-family:Rajdhani,sans-serif;font-size:.85rem;color:#405060">
                Relatório completo para impressão
            </div>
        </div>""", unsafe_allow_html=True)
        try:
            buf = _gerar_pdf(cid, camp)
            st.download_button("⬇️ BAIXAR PDF", data=buf,
                file_name=f"{camp['nome'].replace(' ','_')}.pdf",
                mime="application/pdf",
                use_container_width=True, type="primary")
        except Exception as e:
            st.error(f"Erro: {e}")

def _hf(hex_="1A3A5C"):
    return PatternFill("solid", start_color=hex_.lstrip("#"), end_color=hex_.lstrip("#"))

def _border():
    s = Side(style="thin", color="CCCCCC")
    return Border(left=s,right=s,top=s,bottom=s)

def _gerar_excel(cid, camp):
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    # Sheet classificação
    ws = wb.create_sheet("Classificação")
    classif = calcular_classificacao(cid)
    ws["A1"] = f"🏆 {camp['nome']} — Classificação"
    ws["A1"].font = Font(bold=True, size=13, color="FFFFFF")
    ws["A1"].fill = _hf("1A3A5C")
    ws.merge_cells("A1:K1")
    ws["A1"].alignment = Alignment(horizontal="center")

    hdrs = ["Pos","Equipe","PJ","V","E","D","GP","GC","SG","PTS","Aproveit."]
    for ci, h in enumerate(hdrs, 1):
        cell = ws.cell(row=2, column=ci, value=h)
        cell.font = Font(bold=True, color="FFFFFF", size=9)
        cell.fill = _hf("2C5282")
        cell.alignment = Alignment(horizontal="center")
        cell.border = _border()

    for ri, r in enumerate(classif, 1):
        row_data = [ri, r["equipe"], r["jogos"], r["vitorias"], r["empates"],
                    r["derrotas"], r["gols_pro"], r["gols_contra"], r["saldo"],
                    r["pontos"], f"{r['aproveitamento']}%"]
        alt = PatternFill("solid",start_color="F0F4F8",end_color="F0F4F8") if ri%2==0 else None
        for ci, val in enumerate(row_data, 1):
            cell = ws.cell(row=ri+2, column=ci, value=val)
            cell.alignment = Alignment(horizontal="center")
            cell.border = _border()
            if alt: cell.fill = alt
        ws.cell(row=ri+2, column=10).font = Font(bold=True)

    ws.column_dimensions["A"].width = 6
    ws.column_dimensions["B"].width = 24
    for ci in range(3, 12): ws.column_dimensions[get_column_letter(ci)].width = 10

    # Sheet jogos
    ws2 = wb.create_sheet("Jogos")
    jogos = listar_jogos(cid=cid)
    ws2["A1"] = f"📅 {camp['nome']} — Jogos"
    ws2["A1"].font = Font(bold=True, size=13, color="FFFFFF")
    ws2["A1"].fill = _hf("1A3A5C")
    ws2.merge_cells("A1:H1")
    ws2["A1"].alignment = Alignment(horizontal="center")

    hdrs2 = ["Rodada","Fase","Equipe 1","P1","P2","Equipe 2","Local","Status"]
    for ci, h in enumerate(hdrs2, 1):
        cell = ws2.cell(row=2, column=ci, value=h)
        cell.font = Font(bold=True, color="FFFFFF", size=9)
        cell.fill = _hf("2C5282")
        cell.alignment = Alignment(horizontal="center")
        cell.border = _border()

    for ri, j in enumerate(jogos, 1):
        alt = PatternFill("solid",start_color="F0F4F8",end_color="F0F4F8") if ri%2==0 else None
        vals = [j["rodada_num"], j["fase"], j["equipe1"],
                j["placar1"] if j["placar1"] is not None else "—",
                j["placar2"] if j["placar2"] is not None else "—",
                j["equipe2"], j["local"] or "", j["status"]]
        for ci, val in enumerate(vals, 1):
            cell = ws2.cell(row=ri+2, column=ci, value=val)
            cell.alignment = Alignment(horizontal="center")
            cell.border = _border()
            if alt: cell.fill = alt

    for ci, w in enumerate([8,18,24,8,8,24,20,14], 1):
        ws2.column_dimensions[get_column_letter(ci)].width = w

    # Sheet artilheiros
    ws3 = wb.create_sheet("Artilheiros")
    arts = artilheiros(cid=cid)
    ws3["A1"] = f"⚽ {camp['nome']} — Artilheiros"
    ws3["A1"].font = Font(bold=True, size=13, color="FFFFFF")
    ws3["A1"].fill = _hf("1A3A5C")
    ws3.merge_cells("A1:C1")
    ws3["A1"].alignment = Alignment(horizontal="center")

    for ci, h in enumerate(["Jogador","Equipe","Gols"], 1):
        cell = ws3.cell(row=2, column=ci, value=h)
        cell.font = Font(bold=True, color="FFFFFF", size=9)
        cell.fill = _hf("2C5282")
        cell.alignment = Alignment(horizontal="center")
        cell.border = _border()

    for ri, a in enumerate(arts, 1):
        alt = PatternFill("solid",start_color="F0F4F8",end_color="F0F4F8") if ri%2==0 else None
        for ci, val in enumerate([a["jogador"], a["equipe"], a["gols"]], 1):
            cell = ws3.cell(row=ri+2, column=ci, value=val)
            cell.alignment = Alignment(horizontal="center")
            cell.border = _border()
            if alt: cell.fill = alt

    for ci, w in enumerate([28,24,10], 1):
        ws3.column_dimensions[get_column_letter(ci)].width = w

    buf = io.BytesIO()
    wb.save(buf); buf.seek(0)
    return buf

def _gerar_pdf(cid, camp):
    classif = calcular_classificacao(cid)
    jogos = listar_jogos(cid=cid)
    arts = artilheiros(cid=cid, limit=15)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4),
                             leftMargin=1.5*cm, rightMargin=1.5*cm,
                             topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    title_s = ParagraphStyle("t", parent=styles["Title"],
                              textColor=colors.HexColor("#1A3A5C"), fontSize=16)
    h2_s = ParagraphStyle("h2", parent=styles["Heading2"],
                           textColor=colors.HexColor("#2C5282"), fontSize=12)
    elements = []
    elements.append(Paragraph(f"🏆 {camp['nome']}", title_s))
    elements.append(Paragraph(f"Formato: {camp['formato']} | Status: {camp['status']}", styles["Normal"]))
    elements.append(Spacer(1, 0.4*cm))

    header_style = TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#1A3A5C")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("GRID",(0,0),(-1,-1),0.5,colors.lightgrey),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F0F4F8")]),
        ("FONTSIZE",(0,0),(-1,-1),8),
    ])

    # Classificação
    elements.append(Paragraph("Classificação", h2_s))
    data_c = [["#","Equipe","PJ","V","E","D","GP","GC","SG","PTS","Aprov."]]
    for i, r in enumerate(classif, 1):
        data_c.append([i,r["equipe"],r["jogos"],r["vitorias"],r["empates"],
                        r["derrotas"],r["gols_pro"],r["gols_contra"],
                        f"{r['saldo']:+d}",r["pontos"],f"{r['aproveitamento']}%"])
    t = Table(data_c, colWidths=[1*cm,6*cm]+[1.4*cm]*9)
    t.setStyle(header_style)
    elements.append(t)
    elements.append(Spacer(1, 0.4*cm))

    # Jogos (últimos 30)
    elements.append(Paragraph("Jogos", h2_s))
    data_j = [["Rod.","Fase","Equipe 1","P1","P2","Equipe 2","Status"]]
    for j in jogos[:40]:
        data_j.append([j["rodada_num"],j["fase"],j["equipe1"],
                        j["placar1"] if j["placar1"] is not None else "—",
                        j["placar2"] if j["placar2"] is not None else "—",
                        j["equipe2"],j["status"]])
    t2 = Table(data_j, colWidths=[1.2*cm,4*cm,5.5*cm,1.2*cm,1.2*cm,5.5*cm,3*cm])
    t2.setStyle(header_style)
    elements.append(t2)

    if arts:
        elements.append(Spacer(1, 0.4*cm))
        elements.append(Paragraph("Artilheiros", h2_s))
        data_a = [["Jogador","Equipe","Gols"]]
        for a in arts: data_a.append([a["jogador"],a["equipe"],a["gols"]])
        t3 = Table(data_a, colWidths=[7*cm,7*cm,2*cm])
        t3.setStyle(header_style)
        elements.append(t3)

    doc.build(elements)
    buf.seek(0)
    return buf
