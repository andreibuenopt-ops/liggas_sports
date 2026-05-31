import random
import math
import json
from utils.database import *

# ── Potes por rating (sorteio estilo UEFA/FIFA) ───────────────
def sortear_grupos_por_potes(times, n_grupos, times_por_grupo):
    """
    Divide times em potes por rating e sorteia balanceado.
    Pote 1 = melhores times (1 por grupo), Pote 2 = seguintes, etc.
    """
    times_sorted = sorted(times, key=lambda t: -(t.get("rating") or 0))
    n_potes = times_por_grupo
    grupos = {chr(65+i): [] for i in range(n_grupos)}  # A, B, C...

    for pote_idx in range(n_potes):
        pote = times_sorted[pote_idx * n_grupos : (pote_idx + 1) * n_grupos]
        random.shuffle(pote)
        grupos_disponiveis = [g for g in grupos if len(grupos[g]) == pote_idx]
        random.shuffle(grupos_disponiveis)
        for i, time in enumerate(pote):
            if i < len(grupos_disponiveis):
                grupos[grupos_disponiveis[i]].append(time)

    return grupos

def sortear_grupos_aleatorio(times, n_grupos):
    shuffled = list(times)
    random.shuffle(shuffled)
    grupos = {chr(65+i): [] for i in range(n_grupos)}
    for i, t in enumerate(shuffled):
        grupos[chr(65 + (i % n_grupos))].append(t)
    return grupos

# ── FASE DE GRUPOS ────────────────────────────────────────────
def gerar_fase_grupos(campeonato_id, n_grupos, classificados_por_grupo,
                      ida_volta_grupos, tipo_sorteio="potes"):
    conn_times = listar_times(campeonato_id)
    n_times = len(conn_times)
    times_por_grupo = n_times // n_grupos

    if n_times < n_grupos * 2:
        return False, f"Precisa de pelo menos {n_grupos*2} times para {n_grupos} grupos."

    limpar_jogos(campeonato_id, "Fase de Grupos")
    # Limpa grupos anteriores
    from utils.database import get_conn
    con = get_conn()
    con.execute("UPDATE times SET grupo=NULL WHERE campeonato_id=?", (campeonato_id,))
    con.commit(); con.close()

    if tipo_sorteio == "potes" and any(t.get("rating", 0) > 0 for t in conn_times):
        grupos = sortear_grupos_por_potes(conn_times, n_grupos, times_por_grupo)
    else:
        grupos = sortear_grupos_aleatorio(conn_times, n_grupos)

    # Salva grupos nos times
    for grupo_letra, times_grupo in grupos.items():
        for t in times_grupo:
            atualizar_grupo_time(t["id"], grupo_letra)

    # Gera jogos por grupo (round-robin)
    total_jogos = 0
    for grupo_letra, times_grupo in grupos.items():
        n = len(times_grupo)
        if n % 2 != 0:
            times_grupo = times_grupo + [None]
            n += 1
        lista = list(range(n))
        rodadas = []
        for _ in range(n - 1):
            pares = []
            for i in range(n // 2):
                t1 = times_grupo[lista[i]]
                t2 = times_grupo[lista[n-1-i]]
                if t1 and t2:
                    pares.append((t1["id"], t2["id"]))
            rodadas.append(pares)
            lista = [lista[0]] + [lista[-1]] + lista[1:-1]

        for r_idx, pares in enumerate(rodadas):
            for jn, (t1, t2) in enumerate(pares):
                criar_jogo(campeonato_id, "Fase de Grupos", r_idx+1, t1, t2,
                           jogo_num=jn+1, tem_volta=0)
                total_jogos += 1
                if ida_volta_grupos:
                    criar_jogo(campeonato_id, "Fase de Grupos",
                               len(rodadas)+r_idx+1, t2, t1,
                               jogo_num=jn+1, tem_volta=0)
                    total_jogos += 1

    return True, f"Fase de grupos gerada: {n_grupos} grupos, {total_jogos} jogos"

def calcular_classificacao_grupo(campeonato_id, grupo=None):
    times = listar_times(campeonato_id)
    if grupo:
        times = [t for t in times if t.get("grupo") == grupo]
    jogos = [j for j in listar_jogos(campeonato_id, "Fase de Grupos")
             if j["status"] == "realizado" and j["placar1"] is not None]

    tabela = {}
    for t in times:
        tabela[t["id"]] = {
            "id": t["id"], "time": t["nome"], "grupo": t.get("grupo"),
            "cor": t.get("cor", "#0066ff"), "rating": t.get("rating", 0),
            "PJ":0, "V":0, "E":0, "D":0, "GP":0, "GC":0, "SG":0, "PTS":0
        }

    for j in jogos:
        t1, t2 = j["time1_id"], j["time2_id"]
        p1, p2 = j["placar1"], j["placar2"]
        if t1 not in tabela or t2 not in tabela:
            continue
        tabela[t1]["PJ"]+=1; tabela[t2]["PJ"]+=1
        tabela[t1]["GP"]+=p1; tabela[t1]["GC"]+=p2
        tabela[t2]["GP"]+=p2; tabela[t2]["GC"]+=p1
        if p1>p2:
            tabela[t1]["V"]+=1; tabela[t1]["PTS"]+=3; tabela[t2]["D"]+=1
        elif p2>p1:
            tabela[t2]["V"]+=1; tabela[t2]["PTS"]+=3; tabela[t1]["D"]+=1
        else:
            tabela[t1]["E"]+=1; tabela[t2]["E"]+=1
            tabela[t1]["PTS"]+=1; tabela[t2]["PTS"]+=1

    for t in tabela.values():
        t["SG"] = t["GP"] - t["GC"]

    return sorted(tabela.values(), key=lambda x: (-x["PTS"], -x["SG"], -x["GP"]))

def get_classificados_grupos(campeonato_id, classificados_por_grupo):
    times = listar_times(campeonato_id)
    grupos = sorted(set(t.get("grupo") for t in times if t.get("grupo")))
    classificados = []
    terceiros = []
    for g in grupos:
        classif = calcular_classificacao_grupo(campeonato_id, g)
        for i, t in enumerate(classif):
            if i < classificados_por_grupo:
                classificados.append((g, i+1, t))
            elif i == 2:
                terceiros.append((g, 3, t))
    return classificados, terceiros

# ── MATA-MATA ─────────────────────────────────────────────────
NOMES_FASES = {
    32: "Oitavas de Final",
    16: "Oitavas de Final",
    8:  "Quartas de Final",
    4:  "Semifinal",
    2:  "Final",
}

def nome_fase(n_times):
    for limite, nome in NOMES_FASES.items():
        if n_times <= limite:
            return nome
    return f"Fase de {n_times}"

def gerar_mata_mata(campeonato_id, times_ids, fase_nome, tem_volta=False, rodada_base=1):
    n = len(times_ids)
    pot = _proxima_pot2(n)
    # Preenche com BYE se necessário
    padded = list(times_ids) + [None] * (pot - n)
    random.shuffle(padded) if rodada_base == 1 else None

    jogo_num = 1
    for i in range(0, pot, 2):
        t1 = padded[i]
        t2 = padded[i+1] if i+1 < pot else None
        jid = criar_jogo(campeonato_id, fase_nome, rodada_base, t1, t2,
                         jogo_num=jogo_num, tem_volta=1 if tem_volta else 0)
        jogo_num += 1
        # BYE automático
        if t1 and not t2:
            registrar_resultado(jid, 1, 0)
        elif t2 and not t1:
            registrar_resultado(jid, 0, 1)

def _proxima_pot2(n):
    p = 1
    while p < n: p *= 2
    return p

def avancar_mata_mata(campeonato_id, fase_atual, tem_volta_proxima=False):
    jogos = listar_jogos(campeonato_id, fase_atual)
    if any(j["status"] != "realizado" for j in jogos):
        return False, f"Há jogos pendentes em: {fase_atual}"
    if fase_atual == "Final":
        return False, "Campeonato encerrado!"

    times_map = {t["id"]: t for t in listar_times(campeonato_id)}
    vencedores = []
    for j in jogos:
        if j["tem_volta"] and j["placar1_volta"] is not None:
            # Agregado
            agg1 = (j["placar1"] or 0) + (j["placar2_volta"] or 0)
            agg2 = (j["placar2"] or 0) + (j["placar1_volta"] or 0)
            vencedores.append(j["time1_id"] if agg1 >= agg2 else j["time2_id"])
        else:
            p1, p2 = j["placar1"] or 0, j["placar2"] or 0
            vencedores.append(j["time1_id"] if p1 >= p2 else j["time2_id"])

    n = len(vencedores)
    if n == 1:
        return False, "Campeonato encerrado!"

    proxima = nome_fase(n)
    rodada_base = max(j["rodada"] for j in jogos) + 1
    gerar_mata_mata(campeonato_id, vencedores, proxima, tem_volta_proxima, rodada_base)
    return True, f"✅ {proxima} gerada com {n//2} jogos!"

# ── LIGA (pontos corridos) ────────────────────────────────────
def gerar_rodadas_liga(campeonato_id, ida_volta=True):
    limpar_jogos(campeonato_id)
    times = listar_times(campeonato_id)
    n = len(times)
    if n < 2:
        return False, "Mínimo 2 times."
    if n % 2 != 0:
        times.append({"id": None, "nome": "BYE"})
        n += 1

    lista = list(range(n))
    rodadas = []
    for _ in range(n - 1):
        pares = []
        for i in range(n // 2):
            t1 = times[lista[i]]
            t2 = times[lista[n-1-i]]
            if t1["id"] and t2["id"]:
                pares.append((t1["id"], t2["id"]))
        rodadas.append(pares)
        lista = [lista[0]] + [lista[-1]] + lista[1:-1]

    total = 0
    for r_idx, pares in enumerate(rodadas):
        for jn, (t1, t2) in enumerate(pares):
            criar_jogo(campeonato_id, "Liga", r_idx+1, t1, t2, jogo_num=jn+1)
            total += 1
    if ida_volta:
        for r_idx, pares in enumerate(rodadas):
            for jn, (t1, t2) in enumerate(pares):
                criar_jogo(campeonato_id, "Liga", len(rodadas)+r_idx+1, t2, t1, jogo_num=jn+1)
                total += 1

    return True, f"{total} jogos em {len(rodadas)*(2 if ida_volta else 1)} rodadas"

def calcular_classificacao(campeonato_id, fase="Liga"):
    times = listar_times(campeonato_id)
    jogos = [j for j in listar_jogos(campeonato_id, fase)
             if j["status"] == "realizado" and j["placar1"] is not None]

    tabela = {t["id"]: {
        "id": t["id"], "time": t["nome"], "cor": t.get("cor","#0066ff"),
        "PJ":0,"V":0,"E":0,"D":0,"GP":0,"GC":0,"SG":0,"PTS":0
    } for t in times}

    for j in jogos:
        t1, t2 = j["time1_id"], j["time2_id"]
        p1, p2 = j["placar1"], j["placar2"]
        if t1 not in tabela or t2 not in tabela: continue
        tabela[t1]["PJ"]+=1; tabela[t2]["PJ"]+=1
        tabela[t1]["GP"]+=p1; tabela[t1]["GC"]+=p2
        tabela[t2]["GP"]+=p2; tabela[t2]["GC"]+=p1
        if p1>p2: tabela[t1]["V"]+=1; tabela[t1]["PTS"]+=3; tabela[t2]["D"]+=1
        elif p2>p1: tabela[t2]["V"]+=1; tabela[t2]["PTS"]+=3; tabela[t1]["D"]+=1
        else: tabela[t1]["E"]+=1; tabela[t2]["E"]+=1; tabela[t1]["PTS"]+=1; tabela[t2]["PTS"]+=1

    for t in tabela.values():
        t["SG"] = t["GP"] - t["GC"]

    return sorted(tabela.values(), key=lambda x: (-x["PTS"], -x["SG"], -x["GP"]))

# ── Bracket visual ────────────────────────────────────────────
def get_bracket(campeonato_id):
    jogos = listar_jogos(campeonato_id)
    times_map = {t["id"]: t for t in listar_times(campeonato_id)}
    bracket = {}
    fases_ordem = ["Fase de Grupos","32 avos","Oitavas de Final",
                   "Quartas de Final","Semifinal","Final"]

    for j in jogos:
        fase = j["fase"]
        if fase == "Fase de Grupos": continue
        if fase not in bracket: bracket[fase] = []
        entry = dict(j)
        entry["time1"] = times_map.get(j["time1_id"],{}).get("nome","BYE") if j["time1_id"] else "BYE"
        entry["time2"] = times_map.get(j["time2_id"],{}).get("nome","BYE") if j["time2_id"] else "BYE"
        bracket[fase].append(entry)

    return dict(sorted(bracket.items(),
        key=lambda x: fases_ordem.index(x[0]) if x[0] in fases_ordem else 99))
