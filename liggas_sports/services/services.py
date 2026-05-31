import random
import math
from datetime import date, timedelta
from sqlalchemy.orm import Session
from database.models import *
from database.database import SessionLocal

# ── helpers ──────────────────────────────────────────────────
def _pot2(n):
    p = 1
    while p < n: p *= 2
    return p

FASES = {32:"16 avos",16:"Oitavas de Final",8:"Quartas de Final",4:"Semifinal",2:"Final"}

def nome_fase(n):
    for k,v in sorted(FASES.items()):
        if n <= k: return v
    return f"Fase de {n}"

# ── Campeonatos ───────────────────────────────────────────────
def listar_campeonatos(status=None):
    db = SessionLocal()
    try:
        q = db.query(Campeonato)
        if status: q = q.filter_by(status=status)
        return [_camp_dict(c) for c in q.order_by(Campeonato.criado_em.desc()).all()]
    finally: db.close()

def _camp_dict(c):
    return {k: getattr(c, k) for k in [
        "id","nome","descricao","formato","status","data_inicio","data_fim",
        "n_grupos","classificados_por_grupo","ida_volta","ida_volta_mata",
        "tipo_sorteio","logo_path","criado_em","regulamento"]}

def get_campeonato(cid):
    db = SessionLocal()
    try:
        c = db.query(Campeonato).get(cid)
        return _camp_dict(c) if c else None
    finally: db.close()

def criar_campeonato(dados: dict):
    db = SessionLocal()
    try:
        c = Campeonato(**dados)
        db.add(c); db.commit(); db.refresh(c)
        return c.id
    finally: db.close()

def atualizar_campeonato(cid, dados):
    db = SessionLocal()
    try:
        db.query(Campeonato).filter_by(id=cid).update(dados)
        db.commit()
    finally: db.close()

def deletar_campeonato(cid):
    db = SessionLocal()
    try:
        c = db.query(Campeonato).get(cid)
        if c: db.delete(c); db.commit()
    finally: db.close()

# ── Equipes ───────────────────────────────────────────────────
def listar_equipes():
    db = SessionLocal()
    try:
        return [_eq_dict(e) for e in db.query(Equipe).order_by(Equipe.nome).all()]
    finally: db.close()

def _eq_dict(e):
    return {k: getattr(e, k) for k in [
        "id","nome","cidade","estado","responsavel","telefone","email",
        "escudo_path","cor","rating","criado_em"]}

def get_equipe(eid):
    db = SessionLocal()
    try:
        e = db.query(Equipe).get(eid)
        return _eq_dict(e) if e else None
    finally: db.close()

def criar_equipe(dados):
    db = SessionLocal()
    try:
        e = Equipe(**dados); db.add(e); db.commit(); db.refresh(e)
        return e.id
    finally: db.close()

def atualizar_equipe(eid, dados):
    db = SessionLocal()
    try:
        db.query(Equipe).filter_by(id=eid).update(dados); db.commit()
    finally: db.close()

def deletar_equipe(eid):
    db = SessionLocal()
    try:
        e = db.query(Equipe).get(eid)
        if e: db.delete(e); db.commit()
    finally: db.close()

def equipes_campeonato(cid):
    db = SessionLocal()
    try:
        ecs = db.query(EquipeCampeonato).filter_by(campeonato_id=cid).all()
        return [{"id": ec.equipe.id, "nome": ec.equipe.nome, "cor": ec.equipe.cor,
                 "rating": ec.equipe.rating, "grupo": ec.grupo, "ec_id": ec.id}
                for ec in ecs]
    finally: db.close()

def adicionar_equipe_campeonato(cid, eid):
    db = SessionLocal()
    try:
        ex = db.query(EquipeCampeonato).filter_by(campeonato_id=cid, equipe_id=eid).first()
        if not ex:
            db.add(EquipeCampeonato(equipe_id=eid, campeonato_id=cid))
            db.commit()
    finally: db.close()

def remover_equipe_campeonato(cid, eid):
    db = SessionLocal()
    try:
        ec = db.query(EquipeCampeonato).filter_by(campeonato_id=cid, equipe_id=eid).first()
        if ec: db.delete(ec); db.commit()
    finally: db.close()

# ── Jogadores ─────────────────────────────────────────────────
def listar_jogadores(equipe_id=None):
    db = SessionLocal()
    try:
        q = db.query(Jogador)
        if equipe_id: q = q.filter_by(equipe_id=equipe_id)
        return [_jog_dict(j) for j in q.order_by(Jogador.nome).all()]
    finally: db.close()

def _jog_dict(j):
    return {k: getattr(j, k) for k in [
        "id","nome","data_nascimento","numero","posicao","telefone",
        "email","foto_path","equipe_id","ativo","criado_em"]}

def get_jogador(jid):
    db = SessionLocal()
    try:
        j = db.query(Jogador).get(jid)
        return _jog_dict(j) if j else None
    finally: db.close()

def criar_jogador(dados):
    db = SessionLocal()
    try:
        j = Jogador(**dados); db.add(j); db.commit(); db.refresh(j)
        return j.id
    finally: db.close()

def atualizar_jogador(jid, dados):
    db = SessionLocal()
    try:
        db.query(Jogador).filter_by(id=jid).update(dados); db.commit()
    finally: db.close()

def deletar_jogador(jid):
    db = SessionLocal()
    try:
        j = db.query(Jogador).get(jid)
        if j: db.delete(j); db.commit()
    finally: db.close()

# ── Geração de tabela ─────────────────────────────────────────
def gerar_tabela(cid):
    camp = get_campeonato(cid)
    fmt = camp["formato"]
    if fmt in ("Liga","Pontos Corridos"):
        return _gerar_liga(cid, camp["ida_volta"])
    elif fmt == "Mata-Mata":
        return _gerar_mata_mata_inicial(cid, camp["ida_volta_mata"])
    elif fmt == "Fase de Grupos":
        return _gerar_grupos(cid, camp)
    elif fmt == "Grupos + Mata-Mata":
        return _gerar_grupos(cid, camp)
    return False, "Formato não suportado"

def _limpar_rodadas(cid):
    db = SessionLocal()
    try:
        rodadas = db.query(Rodada).filter_by(campeonato_id=cid).all()
        for r in rodadas:
            for j in r.jogos:
                for x in j.gols + j.assistencias + j.cartoes:
                    db.delete(x)
                db.delete(j)
            db.delete(r)
        db.commit()
    finally: db.close()

def _gerar_liga(cid, ida_volta):
    _limpar_rodadas(cid)
    equipes = equipes_campeonato(cid)
    n = len(equipes)
    if n < 2: return False, "Mínimo 2 equipes."
    if n % 2: equipes.append({"id": None}); n += 1

    lista = list(range(n))
    rodadas_pares = []
    for _ in range(n - 1):
        pares = [(equipes[lista[i]]["id"], equipes[lista[n-1-i]]["id"])
                 for i in range(n//2)
                 if equipes[lista[i]]["id"] and equipes[lista[n-1-i]]["id"]]
        rodadas_pares.append(pares)
        lista = [lista[0]] + [lista[-1]] + lista[1:-1]

    db = SessionLocal()
    try:
        camp = db.query(Campeonato).get(cid)
        data_base = camp.data_inicio or date.today()
        total = 0
        for ri, pares in enumerate(rodadas_pares):
            rod = Rodada(campeonato_id=cid, numero=ri+1,
                         nome=f"Rodada {ri+1}", fase="Liga",
                         data_inicio=data_base + timedelta(weeks=ri))
            db.add(rod); db.flush()
            for e1, e2 in pares:
                db.add(Jogo(rodada_id=rod.id, equipe1_id=e1, equipe2_id=e2,
                            data=data_base + timedelta(weeks=ri), status="Agendado"))
                total += 1
        if ida_volta:
            for ri, pares in enumerate(rodadas_pares):
                rod = Rodada(campeonato_id=cid, numero=len(rodadas_pares)+ri+1,
                             nome=f"Rodada {len(rodadas_pares)+ri+1}", fase="Volta",
                             data_inicio=data_base + timedelta(weeks=len(rodadas_pares)+ri))
                db.add(rod); db.flush()
                for e1, e2 in pares:
                    db.add(Jogo(rodada_id=rod.id, equipe1_id=e2, equipe2_id=e1,
                                data=data_base + timedelta(weeks=len(rodadas_pares)+ri),
                                status="Agendado"))
                    total += 1
        db.commit()
        recalcular_classificacao(cid)
        return True, f"{total} jogos gerados em {len(rodadas_pares)*(2 if ida_volta else 1)} rodadas"
    finally: db.close()

def _gerar_grupos(cid, camp):
    _limpar_rodadas(cid)
    equipes = equipes_campeonato(cid)
    n_grupos = camp["n_grupos"]
    sorteio = camp["tipo_sorteio"]

    if len(equipes) < n_grupos * 2:
        return False, f"Mínimo {n_grupos*2} equipes para {n_grupos} grupos."

    # Sorteia grupos
    db = SessionLocal()
    try:
        db.query(EquipeCampeonato).filter_by(campeonato_id=cid).update({"grupo": None})
        db.commit()

        eq_sorted = sorted(equipes, key=lambda e: -(e.get("rating") or 0))
        tpg = len(equipes) // n_grupos
        grupos = {chr(65+i): [] for i in range(n_grupos)}

        if sorteio == "potes" and any(e.get("rating", 0) > 0 for e in equipes):
            for pote_idx in range(tpg):
                pote = eq_sorted[pote_idx*n_grupos:(pote_idx+1)*n_grupos]
                random.shuffle(pote)
                slots = [g for g in grupos if len(grupos[g]) == pote_idx]
                random.shuffle(slots)
                for i, e in enumerate(pote):
                    if i < len(slots): grupos[slots[i]].append(e)
        else:
            random.shuffle(eq_sorted)
            for i, e in enumerate(eq_sorted):
                grupos[chr(65 + (i % n_grupos))].append(e)

        # Salva grupos
        for g, eqs in grupos.items():
            for e in eqs:
                db.query(EquipeCampeonato).filter_by(
                    campeonato_id=cid, equipe_id=e["id"]).update({"grupo": g})
        db.commit()

        # Gera jogos por grupo
        data_base = db.query(Campeonato).get(cid).data_inicio or date.today()
        total = 0
        max_rod = 0
        for g, eqs in grupos.items():
            n = len(eqs)
            if n % 2: eqs.append({"id": None}); n += 1
            lista = list(range(n))
            for ri in range(n-1):
                pares = [(eqs[lista[i]]["id"], eqs[lista[n-1-i]]["id"])
                         for i in range(n//2)
                         if eqs[lista[i]]["id"] and eqs[lista[n-1-i]]["id"]]
                rod_num = ri+1
                rod = db.query(Rodada).filter_by(campeonato_id=cid, numero=rod_num, fase=f"Grupo {g}").first()
                if not rod:
                    rod = Rodada(campeonato_id=cid, numero=rod_num,
                                 nome=f"Grupo {g} · R{rod_num}", fase=f"Grupo {g}",
                                 data_inicio=data_base + timedelta(weeks=ri))
                    db.add(rod); db.flush()
                for e1, e2 in pares:
                    db.add(Jogo(rodada_id=rod.id, equipe1_id=e1, equipe2_id=e2,
                                data=data_base + timedelta(weeks=ri), status="Agendado"))
                    total += 1
                max_rod = max(max_rod, ri+1)
                lista = [lista[0]] + [lista[-1]] + lista[1:-1]

        db.commit()
        recalcular_classificacao(cid)
        return True, f"Fase de grupos: {n_grupos} grupos, {total} jogos"
    finally: db.close()

def _gerar_mata_mata_inicial(cid, tem_volta):
    _limpar_rodadas(cid)
    equipes = equipes_campeonato(cid)
    if len(equipes) < 2: return False, "Mínimo 2 equipes."
    ids = [e["id"] for e in equipes]
    random.shuffle(ids)
    _criar_rodada_mata(cid, ids, tem_volta, 1)
    return True, f"{nome_fase(len(ids))} gerada com {len(ids)//2} jogos"

def _criar_rodada_mata(cid, ids, tem_volta, rodada_num):
    pot = _pot2(len(ids))
    padded = ids + [None] * (pot - len(ids))
    random.shuffle(padded)
    fase = nome_fase(len(ids))
    db = SessionLocal()
    try:
        camp = db.query(Campeonato).get(cid)
        data_base = camp.data_inicio or date.today()
        rod = Rodada(campeonato_id=cid, numero=rodada_num,
                     nome=fase, fase=fase,
                     data_inicio=data_base + timedelta(weeks=rodada_num))
        db.add(rod); db.flush()
        for i in range(0, pot, 2):
            e1, e2 = padded[i], padded[i+1] if i+1 < pot else None
            j = Jogo(rodada_id=rod.id, equipe1_id=e1, equipe2_id=e2,
                     data=data_base + timedelta(weeks=rodada_num),
                     status="Agendado", tem_volta=tem_volta)
            db.add(j); db.flush()
            if e1 and not e2: j.placar1=1; j.placar2=0; j.status="Finalizado"
            elif e2 and not e1: j.placar1=0; j.placar2=1; j.status="Finalizado"
        db.commit()
    finally: db.close()

def gerar_proxima_fase_mata(cid):
    db = SessionLocal()
    try:
        rodadas = db.query(Rodada).filter_by(campeonato_id=cid).order_by(Rodada.numero.desc()).all()
        fases_mata = [r for r in rodadas if r.fase not in
                      [f"Grupo {g}" for g in "ABCDEFGH"] and "Liga" not in r.fase and "Volta" not in r.fase]
        if not fases_mata: return False, "Nenhuma fase mata-mata encontrada."

        ultima = fases_mata[0]
        jogos = ultima.jogos
        if any(j.status != "Finalizado" for j in jogos if j.equipe1_id and j.equipe2_id):
            return False, f"Há jogos pendentes em: {ultima.fase}"
        if ultima.fase == "Final": return False, "Campeonato encerrado!"

        camp = db.query(Campeonato).get(cid)
        vencedores = []
        for j in jogos:
            if not j.equipe1_id or not j.equipe2_id: continue
            if j.tem_volta and j.placar1_volta is not None:
                agg1 = (j.placar1 or 0) + (j.placar2_volta or 0)
                agg2 = (j.placar2 or 0) + (j.placar1_volta or 0)
                vencedores.append(j.equipe1_id if agg1 >= agg2 else j.equipe2_id)
            else:
                vencedores.append(j.equipe1_id if (j.placar1 or 0) >= (j.placar2 or 0) else j.equipe2_id)

        if len(vencedores) <= 1: return False, "Campeonato encerrado!"
        novo_num = max(r.numero for r in rodadas) + 1
        _criar_rodada_mata(cid, vencedores, camp.ida_volta_mata, novo_num)
        db.commit()
        return True, f"{nome_fase(len(vencedores))} gerada!"
    finally: db.close()

def gerar_mata_mata_classificados(cid):
    camp = get_campeonato(cid)
    db = SessionLocal()
    try:
        rodadas_grp = db.query(Rodada).filter(
            Rodada.campeonato_id == cid,
            Rodada.fase.like("Grupo%")).all()
        jogos_pend = [j for r in rodadas_grp for j in r.jogos
                      if j.status != "Finalizado" and j.equipe1_id and j.equipe2_id]
        if jogos_pend:
            return False, f"{len(jogos_pend)} jogo(s) pendentes na fase de grupos."

        class_data = calcular_classificacao(cid)
        grupos = sorted(set(r["grupo"] for r in class_data if r.get("grupo")))
        classificados = []
        for g in grupos:
            eq_g = [r for r in class_data if r["grupo"] == g]
            classificados.extend([r["equipe_id"] for r in eq_g[:camp["classificados_por_grupo"]]])

        if not classificados:
            return False, "Nenhum classificado. Registre os resultados dos grupos."

        ultimo_num = max((r.numero for r in rodadas_grp), default=0)
        _criar_rodada_mata(cid, classificados, camp["ida_volta_mata"], ultimo_num + 1)
        return True, f"{nome_fase(len(classificados))} gerada com {len(classificados)} equipes!"
    finally: db.close()

# ── Jogos ─────────────────────────────────────────────────────
def listar_jogos(cid=None, status=None, data=None):
    db = SessionLocal()
    try:
        q = db.query(Jogo).join(Rodada)
        if cid: q = q.filter(Rodada.campeonato_id == cid)
        if status: q = q.filter(Jogo.status == status)
        if data: q = q.filter(Jogo.data == data)
        jogos = q.order_by(Rodada.numero, Jogo.id).all()
        return [_jogo_dict(j) for j in jogos]
    finally: db.close()

def _jogo_dict(j):
    return {
        "id": j.id, "rodada_id": j.rodada_id,
        "rodada_num": j.rodada.numero if j.rodada else None,
        "rodada_nome": j.rodada.nome if j.rodada else None,
        "fase": j.rodada.fase if j.rodada else None,
        "equipe1_id": j.equipe1_id, "equipe2_id": j.equipe2_id,
        "equipe1": j.equipe1.nome if j.equipe1 else "BYE",
        "equipe2": j.equipe2.nome if j.equipe2 else "BYE",
        "cor1": j.equipe1.cor if j.equipe1 else "#666",
        "cor2": j.equipe2.cor if j.equipe2 else "#666",
        "placar1": j.placar1, "placar2": j.placar2,
        "placar1_volta": j.placar1_volta, "placar2_volta": j.placar2_volta,
        "tem_volta": j.tem_volta, "data": j.data, "hora": j.hora,
        "local": j.local, "status": j.status, "arbitro": j.arbitro,
    }

def get_jogo(jid):
    db = SessionLocal()
    try:
        j = db.query(Jogo).get(jid)
        return _jogo_dict(j) if j else None
    finally: db.close()

def registrar_resultado(jid, p1, p2, p1v=None, p2v=None, local=None,
                        arbitro=None, obs=None):
    db = SessionLocal()
    try:
        j = db.query(Jogo).get(jid)
        if not j: return
        j.placar1=p1; j.placar2=p2
        j.placar1_volta=p1v; j.placar2_volta=p2v
        j.status="Finalizado"
        if local: j.local=local
        if arbitro: j.arbitro=arbitro
        if obs: j.observacoes=obs
        db.commit()
        # Recalcula classificação
        if j.rodada:
            recalcular_classificacao(j.rodada.campeonato_id)
    finally: db.close()

def adicionar_evento(jid, tipo, jogador_id, equipe_id, minuto=None, motivo=None):
    db = SessionLocal()
    try:
        if tipo == "gol":
            db.add(Gol(jogo_id=jid, jogador_id=jogador_id,
                       equipe_id=equipe_id, minuto=minuto))
        elif tipo == "assistencia":
            db.add(Assistencia(jogo_id=jid, jogador_id=jogador_id,
                               equipe_id=equipe_id, minuto=minuto))
        elif tipo in ("Amarelo","Vermelho"):
            db.add(Cartao(jogo_id=jid, jogador_id=jogador_id,
                          equipe_id=equipe_id, tipo=tipo,
                          minuto=minuto, motivo=motivo))
        db.commit()
    finally: db.close()

def eventos_jogo(jid):
    db = SessionLocal()
    try:
        j = db.query(Jogo).get(jid)
        if not j: return {}
        gols = [{"jogador": g.jogador.nome if g.jogador else "?",
                  "equipe": g.equipe.nome if g.equipe else "?",
                  "minuto": g.minuto} for g in j.gols]
        asts = [{"jogador": a.jogador.nome if a.jogador else "?",
                  "equipe": a.equipe.nome if a.equipe else "?",
                  "minuto": a.minuto} for a in j.assistencias]
        carts = [{"jogador": c.jogador.nome if c.jogador else "?",
                   "equipe": c.equipe.nome if c.equipe else "?",
                   "tipo": c.tipo, "minuto": c.minuto} for c in j.cartoes]
        return {"gols": gols, "assistencias": asts, "cartoes": carts}
    finally: db.close()

# ── Classificação ─────────────────────────────────────────────
def recalcular_classificacao(cid):
    db = SessionLocal()
    try:
        db.query(Classificacao).filter_by(campeonato_id=cid).delete()
        ecs = db.query(EquipeCampeonato).filter_by(campeonato_id=cid).all()
        tabela = {}
        for ec in ecs:
            tabela[ec.equipe_id] = Classificacao(
                campeonato_id=cid, equipe_id=ec.equipe_id, grupo=ec.grupo)
            db.add(tabela[ec.equipe_id])

        rodadas = db.query(Rodada).filter_by(campeonato_id=cid).all()
        fases_liga = ["Liga","Volta","Pontos Corridos"]
        fases_grupo = [f"Grupo {g}" for g in "ABCDEFGHIJKLMNOP"]

        for rod in rodadas:
            if rod.fase not in fases_liga and rod.fase not in fases_grupo:
                continue
            for j in rod.jogos:
                if j.status != "Finalizado" or j.placar1 is None: continue
                e1, e2 = j.equipe1_id, j.equipe2_id
                if e1 not in tabela or e2 not in tabela: continue
                p1, p2 = j.placar1, j.placar2
                tabela[e1].jogos+=1; tabela[e2].jogos+=1
                tabela[e1].gols_pro+=p1; tabela[e1].gols_contra+=p2
                tabela[e2].gols_pro+=p2; tabela[e2].gols_contra+=p1
                if p1>p2: tabela[e1].vitorias+=1; tabela[e1].pontos+=3; tabela[e2].derrotas+=1
                elif p2>p1: tabela[e2].vitorias+=1; tabela[e2].pontos+=3; tabela[e1].derrotas+=1
                else: tabela[e1].empates+=1; tabela[e2].empates+=1; tabela[e1].pontos+=1; tabela[e2].pontos+=1
        db.commit()
    finally: db.close()

def calcular_classificacao(cid, grupo=None):
    db = SessionLocal()
    try:
        q = db.query(Classificacao, Equipe).join(
            Equipe, Classificacao.equipe_id==Equipe.id).filter(
            Classificacao.campeonato_id==cid)
        if grupo: q = q.filter(Classificacao.grupo==grupo)
        rows = q.all()
        result = []
        for c, e in rows:
            sg = c.gols_pro - c.gols_contra
            aprov = round(c.pontos / max(c.jogos*3,1)*100,1) if c.jogos else 0
            result.append({
                "equipe_id":e.id,"equipe":e.nome,"cor":e.cor,
                "grupo":c.grupo,"pontos":c.pontos,"jogos":c.jogos,
                "vitorias":c.vitorias,"empates":c.empates,"derrotas":c.derrotas,
                "gols_pro":c.gols_pro,"gols_contra":c.gols_contra,
                "saldo":sg,"aproveitamento":aprov
            })
        return sorted(result, key=lambda x: (-x["pontos"],-x["saldo"],-x["gols_pro"]))
    finally: db.close()

# ── Estatísticas ──────────────────────────────────────────────
def artilheiros(cid=None, limit=20):
    db = SessionLocal()
    try:
        from sqlalchemy import func
        q2 = db.query(Jogador.nome, Equipe.nome.label("equipe"),
                      func.count(Gol.id).label("gols"))\
            .join(Gol, Gol.jogador_id==Jogador.id)\
            .join(Equipe, Equipe.id==Jogador.equipe_id)
        if cid:
            q2 = q2.join(Rodada, Rodada.id==Jogo.rodada_id)\
                   .filter(Rodada.campeonato_id==cid)
        result = q2.group_by(Jogador.id).order_by(func.count(Gol.id).desc()).limit(limit).all()
        return [{"jogador":r.nome,"equipe":r.equipe,"gols":r.gols} for r in result]
    finally: db.close()

def assistencias_ranking(cid=None, limit=20):
    db = SessionLocal()
    try:
        from sqlalchemy import func
        q = db.query(Jogador.nome, Equipe.nome.label("equipe"),
                     func.count(Assistencia.id).label("total"))\
            .join(Assistencia, Assistencia.jogador_id==Jogador.id)\
            .join(Equipe, Equipe.id==Jogador.equipe_id)\
            .group_by(Jogador.id)\
            .order_by(func.count(Assistencia.id).desc()).limit(limit).all()
        return [{"jogador":r.nome,"equipe":r.equipe,"assistencias":r.total} for r in q]
    finally: db.close()

def cartoes_ranking(cid=None, limit=20):
    db = SessionLocal()
    try:
        from sqlalchemy import func
        q = db.query(Jogador.nome, Equipe.nome.label("equipe"),
                     Cartao.tipo, func.count(Cartao.id).label("total"))\
            .join(Cartao, Cartao.jogador_id==Jogador.id)\
            .join(Equipe, Equipe.id==Jogador.equipe_id)\
            .group_by(Jogador.id, Cartao.tipo)\
            .order_by(func.count(Cartao.id).desc()).limit(limit).all()
        return [{"jogador":r.nome,"equipe":r.equipe,"tipo":r.tipo,"total":r.total} for r in q]
    finally: db.close()

def stats_gerais():
    db = SessionLocal()
    try:
        from sqlalchemy import func
        return {
            "campeonatos": db.query(Campeonato).filter_by(status="ativo").count(),
            "equipes": db.query(Equipe).count(),
            "jogadores": db.query(Jogador).filter_by(ativo=True).count(),
            "jogos_hoje": db.query(Jogo).filter_by(data=date.today()).count(),
            "jogos_agendados": db.query(Jogo).filter_by(status="Agendado").count(),
            "jogos_finalizados": db.query(Jogo).filter_by(status="Finalizado").count(),
            "total_gols": db.query(func.count(Gol.id)).scalar() or 0,
        }
    finally: db.close()

# ── Histórico ─────────────────────────────────────────────────
def salvar_historico(dados):
    db = SessionLocal()
    try:
        h = Historico(**dados); db.add(h); db.commit(); db.refresh(h)
        return h.id
    finally: db.close()

def listar_historico(cid=None):
    db = SessionLocal()
    try:
        q = db.query(Historico)
        if cid: q = q.filter_by(campeonato_id=cid)
        rows = q.order_by(Historico.temporada.desc()).all()
        return [{
            "id":h.id,"temporada":h.temporada,
            "campeonato":h.campeonato.nome if h.campeonato else "",
            "campeao":h.campeao.nome if h.campeao else "",
            "vice":h.vice.nome if h.vice else "",
            "artilheiro":h.artilheiro.nome if h.artilheiro else "",
            "artilheiro_gols":h.artilheiro_gols,
            "observacoes":h.observacoes
        } for h in rows]
    finally: db.close()

# ── Usuários ──────────────────────────────────────────────────
def listar_usuarios():
    db = SessionLocal()
    try:
        return [{"id":u.id,"nome":u.nome,"email":u.email,"perfil":u.perfil,"ativo":u.ativo}
                for u in db.query(Usuario).all()]
    finally: db.close()

def criar_usuario(nome, email, senha, perfil):
    import hashlib
    db = SessionLocal()
    try:
        u = Usuario(nome=nome, email=email,
                    senha_hash=hashlib.sha256(senha.encode()).hexdigest(),
                    perfil=perfil)
        db.add(u); db.commit()
    finally: db.close()
