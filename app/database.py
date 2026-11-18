
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# Diretório principal do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Banco de dados local
DATABASE_DIR = BASE_DIR / "data"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{DATABASE_DIR / 'sima.db'}"


# Conexão com o banco
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
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
