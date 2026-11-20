
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# Diretório principal do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Banco de dados configurado pelo ambiente
DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback para desenvolvimento local
if not DATABASE_URL:
    DATABASE_DIR = BASE_DIR / "data"
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    DATABASE_URL = f"sqlite:///{DATABASE_DIR / 'sima.db'}"

# Ajustes específicos de conexão
connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql://",
        1
    )

# Conexão com o banco
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    future=True
)

# Gerenciamento das sessões
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True
)

# Base para os modelos
Base = declarative_base()


# Dependência para utilização nas rotas
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
