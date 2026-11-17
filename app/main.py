from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pathlib import Path

from .campaigns import router as campaigns_router
from .app.contacts import router as contacts_router

app = FastAPI(title="S.I.M.A.")

BASE_DIR = Path(__file__).resolve().parent.parent
PAINEL = BASE_DIR / "dashboard" / "index.html"

app.include_router(contacts_router)
app.include_router(campaigns_router)


@app.get("/")
def inicio():
    return {
        "sistema": "S.I.M.A.",
        "status": "online"
    }


@app.get("/status")
def status():
    return {
        "sistema": "S.I.M.A.",
        "status": "online",
        "envios_automaticos": False
    }


@app.get("/painel/", response_class=HTMLResponse)
def painel():
    return PAINEL.read_text(encoding="utf-8")
