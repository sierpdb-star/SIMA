from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pathlib import Path

app = FastAPI(title="S.I.M.A.")

BASE_DIR = Path(__file__).resolve().parent.parent
PAINEL = BASE_DIR / "dashboard" / "index.html"


@app.get("/")
def inicio():
    return {"sistema": "S.I.M.A.", "status": "online"}


@app.get("/status")
def status():
    return {"envios_automaticos": False}


@app.get("/painel/", response_class=HTMLResponse)
def painel():
    return PAINEL.read_text(encoding="utf-8")
