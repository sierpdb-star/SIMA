from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from .database import Base, engine
from . import models
from .contacts import router as contacts_router
from .campaigns import router as campaigns_router
from .media import router as media_router


BASE_DIR = Path(__file__).resolve().parent.parent
PAINEL = BASE_DIR / "dashboard" / "index.html"


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="S.I.M.A. - Sistema Inteligente de Mensagens Automatizadas",
    version="1.0.0",
    lifespan=lifespan
)


# Integração dos módulos
app.include_router(contacts_router)
app.include_router(campaigns_router)
app.include_router(media_router)


# Página inicial
@app.get("/")
def inicio():
    return {
        "sistema": "S.I.M.A.",
        "status": "online"
    }


# Status do sistema
@app.get("/status")
def status():
    return {
        "sistema": "S.I.M.A.",
        "status": "online",
        "envios_automaticos": False
    }


# Painel web
@app.get("/painel/", response_class=HTMLResponse)
def abrir_painel():
    if not PAINEL.is_file():
        raise HTTPException(
            status_code=500,
            detail="Arquivo do painel não encontrado."
        )

    return PAINEL.read_text(encoding="utf-8")
