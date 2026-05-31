"""
Motor de campeonato — fiel ao Basic IFC 2013
Formatos suportados:
  1. Pontos Corridos (Liga)
  2. Grupos (fase de grupos estilo Copa do Mundo)
  3. Chaves Cruzadas (2 grupos → mata-mata)
  4. Pontos Corridos + Mata-Mata (fase + eliminatórias)
  5. Eliminatórias (mata-mata puro)
"""
import json, random, math
from datetime import date, timedelta
from pathlib import Path

DATA_FILE = Path("data/campeonato.json")

# ── persistência ─────────────────────────────────────────────
def _load() -> dict:
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return {}

def _save(state: dict):
    DATA_FILE.parent.mkdir(exist_ok=True)
    DATA_FILE.write_text(json.dumps(state, ensure_ascii=False, default=str), encoding="utf-8")

def get_state() -> dict:
    return _load()

def reset():
    _save({})

# ── helpers ───────────────────────────────────────────────────
def _pot2(n):
    p = 1
    while p < n: p *= 2
    return p

FASES_MM = {32:"16 avos de Final", 16:"Oitavas de Final",
            8:"Quartas de Final", 4:"Semifinal", 2:"Final"}

def _nome_fase(n):
    for k, v in sorted(FASES_MM.items()):
        if n <= k: return v
    return "Final"

# ── configuração ──────────────────────────────────────────────
def configurar(dados: dict):
    """Salva configuração inicial do campeonato."""
    state = _load()
    state["config"] = dados
    state["times"] = dados.get("times", [])
    state["jogadores"] = state.get("jogadores", [])
    state["jogos"] = {}
    state["fase_atual"] = "grupos" if "Grupo" in dados.get("formato","") else "liga"
    _save(state)

def get_config() -> dict:
    return _load().get("config", {})

# ── times ─────────────────────────────────────────────────────
def salvar_times(times: list):
    state = _load()
    state["times"] = times
    state["config"]["times"] = times
    _save(state)

def get_times() -> list:
    return _load().get("times", [])

# ── jogadores ─────────────────────────────────────────────────
def salvar_jogador(jog: dict):
    state = _load()
    jogs = state.get("jogadores", [])
    existing = next((i for i, j in enumerate(jogs) if j["id"] == jog.get("id")), None)
    if existing is not None:
        jogs[existing] = jog
    else:
        jog["id"] = len(jogs) + 1
        jogs.append(jog)
    state["jogadores"] = jogs
    _save(state)

def deletar_jogador(jid: int):
    state = _load()
    state["jogadores"] = [j for j in state.get("jogadores",[]) if j["id"] != jid]
    _save(state)

def get_jogadores(equipe=None) -> list:
    jogs = _load().get("jogadores", [])
    if equipe:
        return [j for j in jogs if j.get("equipe") == equipe]
    return jogs

# ── geração de tabela ─────────────────────────────────────────
def gerar_tabela():
    state = _load()
    cfg = state.get("config", {})
    fmt = cfg.get("formato", "")
    times = state.get("times", [])

    n_grupos         = max(1, int(cfg.get("n_grupos", 1)))
    class_por_grupo  = max(1, int(cfg.get("classificados_por_grupo", 2)))
    ida_volta        = cfg.get("ida_volta", True)
    ida_volta_grupos = cfg.get("ida_volta_grupos", False)
    ida_volta_mata   = cfg.get("ida_volta_mata", False)
    tipo_sorteio     = cfg.get("tipo_sorteio", "aleatorio")

    if fmt == "Pontos Corridos":
        jogos = _gerar_pontos_corridos(times, ida_volta)
        state["jogos"] = jogos
        state["fase_atual"] = "liga"

    elif fmt in ("Grupos", "Chaves Cruzadas", "Pontos Corridos + Mata-Mata"):
        # n_grupos=1 → grupo único, todos jogam entre si → X se classificam pro mata-mata
        # n_grupos=2 → 2 chaves, 1 a 4 classificados por chave
        # n_grupos=N → N grupos, class_por_grupo de cada
        grupos = _sortear_grupos(times, n_grupos, tipo_sorteio)
        state["grupos"] = grupos
        jogos = _gerar_jogos_grupos(grupos, ida_volta_grupos)
        state["jogos"] = jogos
        state["fase_atual"] = "grupos"

    elif fmt == "Eliminatórias":
        ids = [t["nome"] for t in times]
        random.shuffle(ids)
        fase = _nome_fase(len(ids))
        jogos = _gerar_mata_mata_jogos(ids, fase, ida_volta_mata)
        state["jogos"] = jogos
        state["fase_atual"] = "mata_mata"
        state["fase_mm_atual"] = fase

    _save(state)
    return True

def _gerar_pontos_corridos(times, ida_volta):
    nomes = [t["nome"] for t in times]
    n = len(nomes)
    if n % 2: nomes.append(None); n += 1
    lista = list(range(n))
    jogos = {}
    rodada = 1
    for _ in range(n - 1):
        for i in range(n // 2):
            a, b = nomes[lista[i]], nomes[lista[n-1-i]]
            if a and b:
                jid = f"r{rodada}_{a}_{b}"
                jogos[jid] = {"id": jid, "casa": a, "fora": b,
                               "gols_casa": None, "gols_fora": None,
                               "rodada": rodada, "fase": "Liga",
                               "data": "", "local": "", "status": "Agendado"}
        lista = [lista[0]] + [lista[-1]] + lista[1:-1]
        rodada += 1
    if ida_volta:
        r_base = rodada
        for _ in range(n - 1):
            for i in range(n // 2):
                a, b = nomes[lista[i]], nomes[lista[n-1-i]]
                if a and b:
                    jid = f"r{rodada}_{b}_{a}"
                    jogos[jid] = {"id": jid, "casa": b, "fora": a,
                                   "gols_casa": None, "gols_fora": None,
                                   "rodada": rodada, "fase": "Volta",
                                   "data": "", "local": "", "status": "Agendado"}
            lista = [lista[0]] + [lista[-1]] + lista[1:-1]
            rodada += 1
    return jogos

def _sortear_grupos(times, n_grupos, tipo_sorteio):
    nomes = [t["nome"] for t in times]
    ratings = {t["nome"]: t.get("rating", 50) for t in times}
    grupos = {chr(65+i): [] for i in range(n_grupos)}

    if tipo_sorteio == "potes" and any(ratings.values()):
        sorted_t = sorted(nomes, key=lambda x: -ratings[x])
        tpg = len(nomes) // n_grupos
        for pote_i in range(tpg):
            pote = sorted_t[pote_i*n_grupos:(pote_i+1)*n_grupos]
            random.shuffle(pote)
            slots = [g for g in grupos if len(grupos[g]) == pote_i]
            random.shuffle(slots)
            for i, t in enumerate(pote):
                if i < len(slots): grupos[slots[i]].append(t)
    else:
        random.shuffle(nomes)
        for i, t in enumerate(nomes):
            grupos[chr(65 + (i % n_grupos))].append(t)
    return grupos

def _gerar_jogos_grupos(grupos, ida_volta):
    jogos = {}
    for g, times in grupos.items():
        n = len(times)
        lista = list(range(n))
        if n % 2: times = times + [None]; n += 1; lista = list(range(n))
        rodada = 1
        for _ in range(n - 1):
            for i in range(n // 2):
                a, b = times[lista[i]], times[lista[n-1-i]]
                if a and b:
                    jid = f"grp{g}_r{rodada}_{a}_{b}"
                    jogos[jid] = {"id": jid, "casa": a, "fora": b,
                                   "gols_casa": None, "gols_fora": None,
                                   "rodada": rodada, "grupo": g,
                                   "fase": f"Grupo {g}",
                                   "data": "", "local": "", "status": "Agendado"}
            lista = [lista[0]] + [lista[-1]] + lista[1:-1]
            rodada += 1
        if ida_volta:
            for _ in range(n - 1):
                for i in range(n // 2):
                    a, b = times[lista[i]], times[lista[n-1-i]]
                    if a and b:
                        jid = f"grp{g}_r{rodada}_{b}_{a}"
                        jogos[jid] = {"id": jid, "casa": b, "fora": a,
                                       "gols_casa": None, "gols_fora": None,
                                       "rodada": rodada, "grupo": g,
                                       "fase": f"Grupo {g} Volta",
                                       "data": "", "local": "", "status": "Agendado"}
                lista = [lista[0]] + [lista[-1]] + lista[1:-1]
                rodada += 1
    return jogos

def _gerar_mata_mata_jogos(times, fase, ida_volta):
    pot = _pot2(len(times))
    padded = times + [None] * (pot - len(times))
    random.shuffle(padded)
    jogos = {}
    for i in range(0, pot, 2):
        a, b = padded[i], padded[i+1] if i+1 < pot else None
        jid = f"mm_{fase}_{i}"
        jogo = {"id": jid, "casa": a, "fora": b,
                "gols_casa": None, "gols_fora": None,
                "gols_casa_volta": None, "gols_fora_volta": None,
                "ida_volta": ida_volta,
                "fase": fase, "data": "", "local": "", "status": "Agendado"}
        if a and not b:
            jogo.update({"gols_casa":1,"gols_fora":0,"status":"Finalizado"})
        elif b and not a:
            jogo.update({"gols_casa":0,"gols_fora":1,"status":"Finalizado"})
        jogos[jid] = jogo
    return jogos

# ── resultados ────────────────────────────────────────────────
def registrar_resultado(jid, gc, gf, gc_v=None, gf_v=None, data="", local=""):
    state = _load()
    j = state["jogos"].get(jid)
    if not j: return
    j["gols_casa"] = gc
    j["gols_fora"] = gf
    j["gols_casa_volta"] = gc_v
    j["gols_fora_volta"] = gf_v
    j["data"] = data
    j["local"] = local
    j["status"] = "Finalizado"
    state["jogos"][jid] = j

    # Atualiza gols nos jogadores
    _atualizar_gols_jogadores(state)
    _save(state)

def _atualizar_gols_jogadores(state):
    # Recalcula gols dos jogadores a partir dos eventos
    for j in state.get("jogadores", []):
        j["gols"] = 0
        j["assist"] = 0
        j["amarelos"] = 0
        j["vermelhos"] = 0
    for ev in state.get("eventos", []):
        for jog in state.get("jogadores", []):
            if jog["id"] == ev.get("jogador_id"):
                if ev["tipo"] == "gol": jog["gols"] = jog.get("gols",0) + 1
                elif ev["tipo"] == "assist": jog["assist"] = jog.get("assist",0) + 1
                elif ev["tipo"] == "amarelo": jog["amarelos"] = jog.get("amarelos",0) + 1
                elif ev["tipo"] == "vermelho": jog["vermelhos"] = jog.get("vermelhos",0) + 1

def registrar_evento(jid, tipo, jogador_id, minuto=None):
    state = _load()
    ev = {"jogo_id": jid, "tipo": tipo, "jogador_id": jogador_id, "minuto": minuto}
    evs = state.get("eventos", [])
    evs.append(ev)
    state["eventos"] = evs
    _atualizar_gols_jogadores(state)
    _save(state)

def get_eventos(jid=None):
    evs = _load().get("eventos", [])
    if jid: return [e for e in evs if e["jogo_id"] == jid]
    return evs

# ── classificação ─────────────────────────────────────────────
def calcular_classificacao(grupo=None) -> list:
    state = _load()
    times = state.get("times", [])
    jogos = state.get("jogos", {}).values()

    fases_validas = {"Liga","Volta","Pontos Corridos"}
    if grupo:
        fases_validas = {f"Grupo {grupo}", f"Grupo {grupo} Volta"}

    tabela = {}
    for t in times:
        n = t["nome"]
        if grupo and state.get("grupos", {}).get(grupo) and n not in state["grupos"][grupo]:
            continue
        tabela[n] = {"time": n, "P":0, "J":0, "V":0, "E":0, "D":0,
                     "GP":0, "GC":0, "SG":0, "pct":0.0}

    for j in jogos:
        if j.get("status") != "Finalizado": continue
        if j.get("fase") not in fases_validas: continue
        gc, gf = j.get("gols_casa"), j.get("gols_fora")
        if gc is None or gf is None: continue
        casa, fora = j["casa"], j["fora"]
        if casa not in tabela or fora not in tabela: continue
        tabela[casa]["J"] += 1; tabela[fora]["J"] += 1
        tabela[casa]["GP"] += gc; tabela[casa]["GC"] += gf
        tabela[fora]["GP"] += gf; tabela[fora]["GC"] += gc
        if gc > gf:
            tabela[casa]["V"] += 1; tabela[casa]["P"] += 3; tabela[fora]["D"] += 1
        elif gf > gc:
            tabela[fora]["V"] += 1; tabela[fora]["P"] += 3; tabela[casa]["D"] += 1
        else:
            tabela[casa]["E"] += 1; tabela[fora]["E"] += 1
            tabela[casa]["P"] += 1; tabela[fora]["P"] += 1

    for t in tabela.values():
        t["SG"] = t["GP"] - t["GC"]
        t["pct"] = round(t["P"] / max(t["J"]*3, 1) * 100, 1)

    return sorted(tabela.values(), key=lambda x: (-x["P"], -x["SG"], -x["GP"]))

def get_grupos_classificacao() -> dict:
    state = _load()
    grupos = state.get("grupos", {})
    result = {}
    for g in sorted(grupos.keys()):
        result[g] = calcular_classificacao(grupo=g)
    return result

# ── mata-mata ─────────────────────────────────────────────────
def get_bracket() -> dict:
    """Retorna todos os jogos de mata-mata organizados por fase."""
    state = _load()
    jogos = state.get("jogos", {})
    fases_liga = {"Liga","Volta","Pontos Corridos"}
    bracket = {}
    for j in jogos.values():
        fase = j.get("fase","")
        if any(fase.startswith(f) for f in ["Grupo","Liga","Volta","Pontos"]):
            continue
        bracket.setdefault(fase, []).append(j)
    ordem = ["16 avos de Final","Oitavas de Final","Quartas de Final","Semifinal","Final"]
    return dict(sorted(bracket.items(), key=lambda x: ordem.index(x[0]) if x[0] in ordem else 99))

def avancar_mata_mata():
    state = _load()
    cfg = state.get("config", {})
    bracket = get_bracket()
    if not bracket: return False, "Nenhuma fase de mata-mata encontrada."

    fase_atual = list(bracket.keys())[-1]
    jogos_fase = bracket[fase_atual]

    pendentes = [j for j in jogos_fase if j["status"] != "Finalizado"
                 and j.get("casa") and j.get("fora")]
    if pendentes:
        return False, f"Há {len(pendentes)} jogo(s) pendentes em: {fase_atual}"
    if fase_atual == "Final":
        return False, "Campeonato encerrado!"

    vencedores = []
    for j in jogos_fase:
        if not j.get("casa") or not j.get("fora"): continue
        if j.get("ida_volta") and j.get("gols_casa_volta") is not None:
            agg_casa = (j["gols_casa"] or 0) + (j["gols_fora_volta"] or 0)
            agg_fora = (j["gols_fora"] or 0) + (j["gols_casa_volta"] or 0)
            vencedores.append(j["casa"] if agg_casa >= agg_fora else j["fora"])
        else:
            gc, gf = j.get("gols_casa",0) or 0, j.get("gols_fora",0) or 0
            vencedores.append(j["casa"] if gc >= gf else j["fora"])

    if len(vencedores) < 2:
        return False, "Poucos classificados."

    nova_fase = _nome_fase(len(vencedores))
    novos = _gerar_mata_mata_jogos(vencedores, nova_fase, cfg.get("ida_volta_mata", False))
    state["jogos"].update(novos)
    state["fase_mm_atual"] = nova_fase
    _save(state)
    return True, f"✅ {nova_fase} gerada com {len(vencedores)//2} confrontos!"

def gerar_mata_mata_de_classificados(class_por_grupo: int):
    state = _load()
    cfg = state.get("config", {})
    grupos_class = get_grupos_classificacao()

    pendentes = [j for j in state.get("jogos",{}).values()
                 if "Grupo" in j.get("fase","") and j["status"] != "Finalizado"
                 and j.get("casa") and j.get("fora")]
    if pendentes:
        return False, f"{len(pendentes)} jogo(s) pendentes nos grupos."

    classificados = []
    for g, tabela in grupos_class.items():
        classificados.extend([t["time"] for t in tabela[:class_por_grupo]])

    if not classificados:
        return False, "Nenhum classificado. Registre os resultados dos grupos."

    fase = _nome_fase(len(classificados))
    novos = _gerar_mata_mata_jogos(classificados, fase, cfg.get("ida_volta_mata", False))
    state["jogos"].update(novos)
    state["fase_atual"] = "mata_mata"
    state["fase_mm_atual"] = fase
    _save(state)
    return True, f"✅ {fase} gerada com {len(classificados)} times!"

# ── estatísticas ──────────────────────────────────────────────
def artilheiros(equipe=None):
    state = _load()
    jogs = state.get("jogadores", [])
    evs = state.get("eventos", [])
    jog_map = {j["id"]: j for j in jogs}
    gols = {}
    for e in evs:
        if e["tipo"] != "gol": continue
        jid = e["jogador_id"]
        if jid not in jog_map: continue
        j = jog_map[jid]
        if equipe and j.get("equipe") != equipe: continue
        gols[jid] = gols.get(jid, 0) + 1
    result = []
    for jid, g in sorted(gols.items(), key=lambda x: -x[1]):
        j = jog_map[jid]
        result.append({"nome": j["nome"], "equipe": j.get("equipe",""), "gols": g})
    return result

def get_jogos(fase=None, rodada=None, status=None) -> list:
    state = _load()
    jogos = list(state.get("jogos", {}).values())
    if fase: jogos = [j for j in jogos if j.get("fase") == fase]
    if rodada: jogos = [j for j in jogos if j.get("rodada") == rodada]
    if status: jogos = [j for j in jogos if j.get("status") == status]
    return sorted(jogos, key=lambda x: (x.get("rodada",0), x.get("id","")))

def get_fases() -> list:
    state = _load()
    fases = list(dict.fromkeys(j.get("fase","") for j in state.get("jogos",{}).values()))
    return [f for f in fases if f]

def get_rodadas(fase=None) -> list:
    state = _load()
    jogos = state.get("jogos",{}).values()
    if fase: jogos = [j for j in jogos if j.get("fase") == fase]
    return sorted(set(j.get("rodada",1) for j in jogos if j.get("rodada")))

def campeao() -> str:
    bracket = get_bracket()
    final = bracket.get("Final", [])
    for j in final:
        if j["status"] == "Finalizado":
            gc, gf = j.get("gols_casa",0) or 0, j.get("gols_fora",0) or 0
            return j["casa"] if gc >= gf else j["fora"]
    return ""
