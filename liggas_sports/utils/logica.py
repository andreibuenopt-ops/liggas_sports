import random
import math
from utils.database import *

FASES_COPA = {
    2: ["Final"],
    4: ["Semifinal", "Final"],
    8: ["Quartas de Final", "Semifinal", "Final"],
    16: ["Oitavas de Final", "Quartas de Final", "Semifinal", "Final"],
    32: ["16 avos de Final", "Oitavas de Final", "Quartas de Final", "Semifinal", "Final"],
}

def proxima_potencia_de_2(n):
    p = 1
    while p < n:
        p *= 2
    return p

# ── COPA ─────────────────────────────────────────────────────
def gerar_chaves_copa(campeonato_id, embaralhar=True):
    limpar_jogos(campeonato_id)
    times = listar_times(campeonato_id)
    if len(times) < 2:
        return False, "Mínimo 2 times necessários."

    n = len(times)
    pot = proxima_potencia_de_2(n)
    fases = FASES_COPA.get(pot, FASES_COPA[32])
    fase_inicial = fases[0]

    if embaralhar:
        random.shuffle(times)

    # Preenche com byes se não for potência de 2
    times_padded = times + [None] * (pot - n)

    for i in range(0, pot, 2):
        t1 = times_padded[i]
        t2 = times_padded[i + 1]
        t1_id = t1["id"] if t1 else None
        t2_id = t2["id"] if t2 else None
        jogo_id = criar_jogo(campeonato_id, fase_inicial, 1, t1_id, t2_id)
        # BYE automático
        if t1_id and not t2_id:
            registrar_resultado(jogo_id, 1, 0)
        elif t2_id and not t1_id:
            registrar_resultado(jogo_id, 0, 1)

    return True, f"Chaves geradas: {pot//2} jogos na {fase_inicial}"

def avancar_fase_copa(campeonato_id):
    jogos = listar_jogos(campeonato_id)
    fases_existentes = list(dict.fromkeys([j["fase"] for j in jogos]))

    # Fase atual = última fase com jogos
    fase_atual = fases_existentes[-1]
    jogos_fase = [j for j in jogos if j["fase"] == fase_atual]

    if any(j["status"] != "realizado" for j in jogos_fase):
        return False, f"Há jogos pendentes na fase: {fase_atual}"

    if fase_atual == "Final":
        return False, "Campeonato encerrado!"

    times_map = {t["id"]: t for t in listar_times(campeonato_id)}
    vencedores = []
    for j in jogos_fase:
        if j["placar1"] > j["placar2"]:
            vencedores.append(j["time1_id"])
        elif j["placar2"] > j["placar1"]:
            vencedores.append(j["time2_id"])
        else:
            # Empate → primeiro time avança (pênaltis não implementado)
            vencedores.append(j["time1_id"])

    # Determina próxima fase
    n_times = len(vencedores)
    pot = proxima_potencia_de_2(n_times)
    fases_possiveis = FASES_COPA.get(pot * 2, FASES_COPA[32])

    # Encontra a fase após a atual
    try:
        idx_atual = fases_possiveis.index(fase_atual)
        proxima_fase = fases_possiveis[idx_atual + 1]
    except (ValueError, IndexError):
        proxima_fase = "Final"

    rodada = max([j["rodada"] for j in jogos]) + 1
    for i in range(0, len(vencedores), 2):
        t1 = vencedores[i]
        t2 = vencedores[i + 1] if i + 1 < len(vencedores) else None
        criar_jogo(campeonato_id, proxima_fase, rodada, t1, t2)

    return True, f"Fase {proxima_fase} gerada com {len(vencedores)//2} jogos!"

def get_bracket(campeonato_id):
    jogos = listar_jogos(campeonato_id)
    times_map = {t["id"]: t for t in listar_times(campeonato_id)}
    bracket = {}
    for j in jogos:
        fase = j["fase"]
        if fase not in bracket:
            bracket[fase] = []
        entry = dict(j)
        entry["time1"] = times_map.get(j["time1_id"], {}).get("nome", "BYE") if j["time1_id"] else "BYE"
        entry["time2"] = times_map.get(j["time2_id"], {}).get("nome", "BYE") if j["time2_id"] else "BYE"
        bracket[fase].append(entry)
    return bracket

# ── LIGA ─────────────────────────────────────────────────────
def gerar_rodadas_liga(campeonato_id, ida_e_volta=True):
    limpar_jogos(campeonato_id)
    times = listar_times(campeonato_id)
    n = len(times)
    if n < 2:
        return False, "Mínimo 2 times necessários."

    if n % 2 != 0:
        times.append({"id": None, "nome": "BYE"})
        n += 1

    rodadas = []
    lista = list(range(n))

    for rodada in range(n - 1):
        pares = []
        for i in range(n // 2):
            t1 = times[lista[i]]
            t2 = times[lista[n - 1 - i]]
            if t1["id"] and t2["id"]:
                pares.append((t1["id"], t2["id"]))
        rodadas.append(pares)
        lista = [lista[0]] + [lista[-1]] + lista[1:-1]

    total = 0
    for r_idx, pares in enumerate(rodadas):
        for t1_id, t2_id in pares:
            criar_jogo(campeonato_id, "Fase de Grupos", r_idx + 1, t1_id, t2_id)
            total += 1

    if ida_e_volta:
        for r_idx, pares in enumerate(rodadas):
            for t1_id, t2_id in pares:
                criar_jogo(campeonato_id, "Fase de Grupos", len(rodadas) + r_idx + 1, t2_id, t1_id)
                total += 1

    return True, f"{total} jogos gerados em {len(rodadas) * (2 if ida_e_volta else 1)} rodadas"

def calcular_classificacao(campeonato_id):
    times = listar_times(campeonato_id)
    jogos = [j for j in listar_jogos(campeonato_id) if j["status"] == "realizado"
             and j["placar1"] is not None]

    tabela = {}
    for t in times:
        tabela[t["id"]] = {
            "id": t["id"],
            "time": t["nome"],
            "cor": t.get("cor", "#1f77b4"),
            "PJ": 0, "V": 0, "E": 0, "D": 0,
            "GP": 0, "GC": 0, "SG": 0, "PTS": 0
        }

    for j in jogos:
        t1 = j["time1_id"]
        t2 = j["time2_id"]
        p1 = j["placar1"]
        p2 = j["placar2"]

        if t1 not in tabela or t2 not in tabela:
            continue

        tabela[t1]["PJ"] += 1
        tabela[t2]["PJ"] += 1
        tabela[t1]["GP"] += p1
        tabela[t1]["GC"] += p2
        tabela[t2]["GP"] += p2
        tabela[t2]["GC"] += p1

        if p1 > p2:
            tabela[t1]["V"] += 1
            tabela[t1]["PTS"] += 3
            tabela[t2]["D"] += 1
        elif p2 > p1:
            tabela[t2]["V"] += 1
            tabela[t2]["PTS"] += 3
            tabela[t1]["D"] += 1
        else:
            tabela[t1]["E"] += 1
            tabela[t2]["E"] += 1
            tabela[t1]["PTS"] += 1
            tabela[t2]["PTS"] += 1

    for t in tabela.values():
        t["SG"] = t["GP"] - t["GC"]

    return sorted(tabela.values(), key=lambda x: (-x["PTS"], -x["SG"], -x["GP"]))

# ── INTERCLASSES ─────────────────────────────────────────────
def calcular_pontuacao_interclasses(campeonatos_ids):
    """Agrega pontuação de vários campeonatos por turma/time"""
    pontuacao = {}
    for cid in campeonatos_ids:
        classif = calcular_classificacao(cid)
        camp = get_campeonato(cid)
        for pos, entry in enumerate(classif):
            nome = entry["time"]
            pts = [5, 3, 2, 1][pos] if pos < 4 else 0
            if nome not in pontuacao:
                pontuacao[nome] = {"time": nome, "total": 0, "detalhes": {}}
            pontuacao[nome]["total"] += pts
            pontuacao[nome]["detalhes"][camp["nome"]] = f"{pos+1}º ({pts}pts)"

    return sorted(pontuacao.values(), key=lambda x: -x["total"])
