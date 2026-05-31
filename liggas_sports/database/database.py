import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from database.models import Base, Usuario
import hashlib

DB_URL = os.environ.get("DATABASE_URL", "sqlite:///data/liggassports.db")
if DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if "sqlite" in DB_URL else {})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def init_db():
    os.makedirs("data", exist_ok=True)
    Base.metadata.create_all(bind=engine)
    _seed_admin()

def get_session() -> Session:
    return SessionLocal()

def _hash(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()

def _seed_admin():
    db = SessionLocal()
    try:
        if not db.query(Usuario).first():
            db.add(Usuario(
                nome="Administrador",
                email="admin@liggassports.com",
                senha_hash=_hash("admin123"),
                perfil="admin"
            ))
            db.commit()
    finally:
        db.close()

def autenticar(email: str, senha: str):
    db = SessionLocal()
    try:
        u = db.query(Usuario).filter_by(email=email, ativo=True).first()
        if u and u.senha_hash == _hash(senha):
            return {"id": u.id, "nome": u.nome, "perfil": u.perfil, "email": u.email}
        return None
    finally:
        db.close()
