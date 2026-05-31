import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "torneio.db")

def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS campeonatos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            modalidade TEXT NOT NULL,
            formato TEXT NOT NULL,
            esporte TEXT,
            status TEXT DEFAULT 'ativo',
            config TEXT DEFAULT '{}',
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS times (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campeonato_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            grupo TEXT,
            cor TEXT DEFAULT '#1f77b4',
            FOREIGN KEY (campeonato_id) REFERENCES campeonatos(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS jogos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campeonato_id INTEGER NOT NULL,
            fase TEXT NOT NULL,
            rodada INTEGER DEFAULT 1,
            time1_id INTEGER,
            time2_id INTEGER,
            placar1 INTEGER,
            placar2 INTEGER,
            data TEXT,
            local TEXT,
            status TEXT DEFAULT 'pendente',
            detalhes TEXT DEFAULT '{}',
            FOREIGN KEY (campeonato_id) REFERENCES campeonatos(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS artilheiros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jogo_id INTEGER NOT NULL,
            time_id INTEGER NOT NULL,
            jogador TEXT NOT NULL,
            gols INTEGER DEFAULT 1,
            FOREIGN KEY (jogo_id) REFERENCES jogos(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS cartoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jogo_id INTEGER NOT NULL,
            time_id INTEGER NOT NULL,
            jogador TEXT NOT NULL,
            tipo TEXT NOT NULL,
            FOREIGN KEY (jogo_id) REFERENCES jogos(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS jogadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campeonato_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            time_id INTEGER,
            FOREIGN KEY (campeonato_id) REFERENCES campeonatos(id),
            FOREIGN KEY (time_id) REFERENCES times(id)
        )
    """)

    conn.commit()
    conn.close()

# ── Campeonatos ──────────────────────────────────────────────
def criar_campeonato(nome, modalidade, formato, esporte=None, config=None):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO campeonatos (nome, modalidade, formato, esporte, config) VALUES (?,?,?,?,?)",
        (nome, modalidade, formato, esporte, json.dumps(config or {}))
    )
    id_ = c.lastrowid
    conn.commit()
    conn.close()
    return id_

def listar_campeonatos():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM campeonatos ORDER BY criado_em DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_campeonato(id_):
    conn = get_conn()
    row = conn.execute("SELECT * FROM campeonatos WHERE id=?", (id_,)).fetchone()
    conn.close()
    return dict(row) if row else None

def deletar_campeonato(id_):
    conn = get_conn()
    conn.execute("DELETE FROM artilheiros WHERE jogo_id IN (SELECT id FROM jogos WHERE campeonato_id=?)", (id_,))
    conn.execute("DELETE FROM cartoes WHERE jogo_id IN (SELECT id FROM jogos WHERE campeonato_id=?)", (id_,))
    conn.execute("DELETE FROM jogos WHERE campeonato_id=?", (id_,))
    conn.execute("DELETE FROM times WHERE campeonato_id=?", (id_,))
    conn.execute("DELETE FROM campeonatos WHERE id=?", (id_,))
    conn.commit()
    conn.close()

def atualizar_status_campeonato(id_, status):
    conn = get_conn()
    conn.execute("UPDATE campeonatos SET status=? WHERE id=?", (status, id_))
    conn.commit()
    conn.close()

# ── Times ────────────────────────────────────────────────────
def adicionar_time(campeonato_id, nome, grupo=None, cor="#1f77b4"):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO times (campeonato_id, nome, grupo, cor) VALUES (?,?,?,?)",
              (campeonato_id, nome, grupo, cor))
    id_ = c.lastrowid
    conn.commit()
    conn.close()
    return id_

def listar_times(campeonato_id):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM times WHERE campeonato_id=? ORDER BY nome", (campeonato_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def deletar_time(time_id):
    conn = get_conn()
    conn.execute("DELETE FROM times WHERE id=?", (time_id,))
    conn.commit()
    conn.close()

# ── Jogos ────────────────────────────────────────────────────
def criar_jogo(campeonato_id, fase, rodada, time1_id, time2_id, data=None, local=None):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO jogos (campeonato_id, fase, rodada, time1_id, time2_id, data, local)
        VALUES (?,?,?,?,?,?,?)
    """, (campeonato_id, fase, rodada, time1_id, time2_id, data, local))
    id_ = c.lastrowid
    conn.commit()
    conn.close()
    return id_

def listar_jogos(campeonato_id, fase=None):
    conn = get_conn()
    if fase:
        rows = conn.execute(
            "SELECT * FROM jogos WHERE campeonato_id=? AND fase=? ORDER BY rodada, id",
            (campeonato_id, fase)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM jogos WHERE campeonato_id=? ORDER BY rodada, id",
            (campeonato_id,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def registrar_resultado(jogo_id, placar1, placar2):
    conn = get_conn()
    conn.execute(
        "UPDATE jogos SET placar1=?, placar2=?, status='realizado' WHERE id=?",
        (placar1, placar2, jogo_id)
    )
    conn.commit()
    conn.close()

def get_jogo(jogo_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM jogos WHERE id=?", (jogo_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def limpar_jogos(campeonato_id):
    conn = get_conn()
    conn.execute("DELETE FROM artilheiros WHERE jogo_id IN (SELECT id FROM jogos WHERE campeonato_id=?)", (campeonato_id,))
    conn.execute("DELETE FROM cartoes WHERE jogo_id IN (SELECT id FROM jogos WHERE campeonato_id=?)", (campeonato_id,))
    conn.execute("DELETE FROM jogos WHERE campeonato_id=?", (campeonato_id,))
    conn.commit()
    conn.close()

# ── Artilheiros / Cartões ────────────────────────────────────
def adicionar_artilheiro(jogo_id, time_id, jogador, gols=1):
    conn = get_conn()
    conn.execute("INSERT INTO artilheiros (jogo_id, time_id, jogador, gols) VALUES (?,?,?,?)",
                 (jogo_id, time_id, jogador, gols))
    conn.commit()
    conn.close()

def adicionar_cartao(jogo_id, time_id, jogador, tipo):
    conn = get_conn()
    conn.execute("INSERT INTO cartoes (jogo_id, time_id, jogador, tipo) VALUES (?,?,?,?)",
                 (jogo_id, time_id, jogador, tipo))
    conn.commit()
    conn.close()

def artilheiros_campeonato(campeonato_id):
    conn = get_conn()
    rows = conn.execute("""
        SELECT a.jogador, t.nome as time, SUM(a.gols) as total_gols
        FROM artilheiros a
        JOIN jogos j ON a.jogo_id = j.id
        JOIN times t ON a.time_id = t.id
        WHERE j.campeonato_id=?
        GROUP BY a.jogador, a.time_id
        ORDER BY total_gols DESC
    """, (campeonato_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def cartoes_campeonato(campeonato_id):
    conn = get_conn()
    rows = conn.execute("""
        SELECT c.jogador, t.nome as time, c.tipo, COUNT(*) as total
        FROM cartoes c
        JOIN jogos j ON c.jogo_id = j.id
        JOIN times t ON c.time_id = t.id
        WHERE j.campeonato_id=?
        GROUP BY c.jogador, c.time_id, c.tipo
        ORDER BY total DESC
    """, (campeonato_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ── Jogadores ────────────────────────────────────────────────
def adicionar_jogador(campeonato_id, nome, time_id=None):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO jogadores (campeonato_id, nome, time_id) VALUES (?,?,?)",
              (campeonato_id, nome, time_id))
    id_ = c.lastrowid
    conn.commit()
    conn.close()
    return id_

def listar_jogadores(campeonato_id):
    conn = get_conn()
    rows = conn.execute("""
        SELECT j.*, t.nome as time_nome, t.cor as time_cor
        FROM jogadores j
        LEFT JOIN times t ON j.time_id = t.id
        WHERE j.campeonato_id=?
        ORDER BY j.nome
    """, (campeonato_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def deletar_jogador(jogador_id):
    conn = get_conn()
    conn.execute("DELETE FROM jogadores WHERE id=?", (jogador_id,))
    conn.commit()
    conn.close()

def atribuir_time_jogador(jogador_id, time_id):
    conn = get_conn()
    conn.execute("UPDATE jogadores SET time_id=? WHERE id=?", (time_id, jogador_id))
    conn.commit()
    conn.close()

def limpar_times_jogadores(campeonato_id):
    conn = get_conn()
    conn.execute("UPDATE jogadores SET time_id=NULL WHERE campeonato_id=?", (campeonato_id,))
    conn.commit()
    conn.close()

def adicionar_jogadores_em_lote(campeonato_id, nomes):
    conn = get_conn()
    for nome in nomes:
        nome = nome.strip()
        if nome:
            conn.execute("INSERT INTO jogadores (campeonato_id, nome) VALUES (?,?)",
                         (campeonato_id, nome))
    conn.commit()
    conn.close()
