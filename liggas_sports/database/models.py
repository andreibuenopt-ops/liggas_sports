from sqlalchemy import (Column, Integer, String, Float, DateTime, Date, Time,
                        Text, Boolean, ForeignKey, Enum, create_engine)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import enum

Base = declarative_base()

class PerfilEnum(str, enum.Enum):
    admin = "admin"
    organizador = "organizador"
    arbitro = "arbitro"

class FormatoEnum(str, enum.Enum):
    liga = "Liga"
    mata_mata = "Mata-Mata"
    grupos = "Fase de Grupos"
    grupos_mata = "Grupos + Mata-Mata"
    pontos_corridos = "Pontos Corridos"

class StatusJogoEnum(str, enum.Enum):
    agendado = "Agendado"
    em_andamento = "Em Andamento"
    finalizado = "Finalizado"
    suspenso = "Suspenso"
    cancelado = "Cancelado"

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    perfil = Column(String(20), default="organizador")
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)

class Campeonato(Base):
    __tablename__ = "campeonatos"
    id = Column(Integer, primary_key=True)
    nome = Column(String(150), nullable=False)
    descricao = Column(Text)
    regulamento = Column(Text)
    formato = Column(String(30), default="Liga")
    data_inicio = Column(Date)
    data_fim = Column(Date)
    status = Column(String(20), default="ativo")
    logo_path = Column(String(255))
    n_grupos = Column(Integer, default=4)
    classificados_por_grupo = Column(Integer, default=2)
    ida_volta = Column(Boolean, default=True)
    ida_volta_mata = Column(Boolean, default=False)
    tipo_sorteio = Column(String(20), default="potes")
    criado_em = Column(DateTime, default=datetime.utcnow)
    equipes = relationship("EquipeCampeonato", back_populates="campeonato", cascade="all, delete")
    rodadas = relationship("Rodada", back_populates="campeonato", cascade="all, delete")
    historico = relationship("Historico", back_populates="campeonato", cascade="all, delete")

class Equipe(Base):
    __tablename__ = "equipes"
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    cidade = Column(String(100))
    estado = Column(String(2))
    responsavel = Column(String(100))
    telefone = Column(String(20))
    email = Column(String(150))
    escudo_path = Column(String(255))
    cor = Column(String(7), default="#0066ff")
    rating = Column(Integer, default=75)
    criado_em = Column(DateTime, default=datetime.utcnow)
    jogadores = relationship("Jogador", back_populates="equipe", cascade="all, delete")
    campeonatos = relationship("EquipeCampeonato", back_populates="equipe", cascade="all, delete")

class EquipeCampeonato(Base):
    __tablename__ = "equipes_campeonatos"
    id = Column(Integer, primary_key=True)
    equipe_id = Column(Integer, ForeignKey("equipes.id"))
    campeonato_id = Column(Integer, ForeignKey("campeonatos.id"))
    grupo = Column(String(5))
    equipe = relationship("Equipe", back_populates="campeonatos")
    campeonato = relationship("Campeonato", back_populates="equipes")

class Jogador(Base):
    __tablename__ = "jogadores"
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    data_nascimento = Column(Date)
    numero = Column(Integer)
    posicao = Column(String(30))
    telefone = Column(String(20))
    email = Column(String(150))
    foto_path = Column(String(255))
    equipe_id = Column(Integer, ForeignKey("equipes.id"))
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    equipe = relationship("Equipe", back_populates="jogadores")
    gols = relationship("Gol", back_populates="jogador", cascade="all, delete")
    assistencias = relationship("Assistencia", back_populates="jogador", cascade="all, delete")
    cartoes = relationship("Cartao", back_populates="jogador", cascade="all, delete")

class Rodada(Base):
    __tablename__ = "rodadas"
    id = Column(Integer, primary_key=True)
    campeonato_id = Column(Integer, ForeignKey("campeonatos.id"))
    numero = Column(Integer)
    nome = Column(String(50))
    fase = Column(String(50), default="Liga")
    data_inicio = Column(Date)
    data_fim = Column(Date)
    campeonato = relationship("Campeonato", back_populates="rodadas")
    jogos = relationship("Jogo", back_populates="rodada", cascade="all, delete")

class Jogo(Base):
    __tablename__ = "jogos"
    id = Column(Integer, primary_key=True)
    rodada_id = Column(Integer, ForeignKey("rodadas.id"))
    equipe1_id = Column(Integer, ForeignKey("equipes.id"))
    equipe2_id = Column(Integer, ForeignKey("equipes.id"))
    placar1 = Column(Integer)
    placar2 = Column(Integer)
    placar1_volta = Column(Integer)
    placar2_volta = Column(Integer)
    tem_volta = Column(Boolean, default=False)
    data = Column(Date)
    hora = Column(Time)
    local = Column(String(150))
    status = Column(String(20), default="Agendado")
    arbitro = Column(String(100))
    observacoes = Column(Text)
    rodada = relationship("Rodada", back_populates="jogos")
    equipe1 = relationship("Equipe", foreign_keys=[equipe1_id])
    equipe2 = relationship("Equipe", foreign_keys=[equipe2_id])
    gols = relationship("Gol", back_populates="jogo", cascade="all, delete")
    assistencias = relationship("Assistencia", back_populates="jogo", cascade="all, delete")
    cartoes = relationship("Cartao", back_populates="jogo", cascade="all, delete")

class Gol(Base):
    __tablename__ = "gols"
    id = Column(Integer, primary_key=True)
    jogo_id = Column(Integer, ForeignKey("jogos.id"))
    jogador_id = Column(Integer, ForeignKey("jogadores.id"))
    equipe_id = Column(Integer, ForeignKey("equipes.id"))
    minuto = Column(Integer)
    tipo = Column(String(20), default="normal")
    jogo = relationship("Jogo", back_populates="gols")
    jogador = relationship("Jogador", back_populates="gols")
    equipe = relationship("Equipe")

class Assistencia(Base):
    __tablename__ = "assistencias"
    id = Column(Integer, primary_key=True)
    jogo_id = Column(Integer, ForeignKey("jogos.id"))
    jogador_id = Column(Integer, ForeignKey("jogadores.id"))
    equipe_id = Column(Integer, ForeignKey("equipes.id"))
    minuto = Column(Integer)
    jogo = relationship("Jogo", back_populates="assistencias")
    jogador = relationship("Jogador", back_populates="assistencias")
    equipe = relationship("Equipe")

class Cartao(Base):
    __tablename__ = "cartoes"
    id = Column(Integer, primary_key=True)
    jogo_id = Column(Integer, ForeignKey("jogos.id"))
    jogador_id = Column(Integer, ForeignKey("jogadores.id"))
    equipe_id = Column(Integer, ForeignKey("equipes.id"))
    tipo = Column(String(10))
    minuto = Column(Integer)
    motivo = Column(String(150))
    jogo = relationship("Jogo", back_populates="cartoes")
    jogador = relationship("Jogador", back_populates="cartoes")
    equipe = relationship("Equipe")

class Classificacao(Base):
    __tablename__ = "classificacao"
    id = Column(Integer, primary_key=True)
    campeonato_id = Column(Integer, ForeignKey("campeonatos.id"))
    equipe_id = Column(Integer, ForeignKey("equipes.id"))
    grupo = Column(String(5))
    pontos = Column(Integer, default=0)
    jogos = Column(Integer, default=0)
    vitorias = Column(Integer, default=0)
    empates = Column(Integer, default=0)
    derrotas = Column(Integer, default=0)
    gols_pro = Column(Integer, default=0)
    gols_contra = Column(Integer, default=0)
    campeonato = relationship("Campeonato")
    equipe = relationship("Equipe")

class Historico(Base):
    __tablename__ = "historico"
    id = Column(Integer, primary_key=True)
    campeonato_id = Column(Integer, ForeignKey("campeonatos.id"))
    temporada = Column(String(20))
    campeao_id = Column(Integer, ForeignKey("equipes.id"))
    vice_id = Column(Integer, ForeignKey("equipes.id"))
    artilheiro_id = Column(Integer, ForeignKey("jogadores.id"))
    artilheiro_gols = Column(Integer)
    observacoes = Column(Text)
    campeonato = relationship("Campeonato", back_populates="historico")
    campeao = relationship("Equipe", foreign_keys=[campeao_id])
    vice = relationship("Equipe", foreign_keys=[vice_id])
    artilheiro = relationship("Jogador")
