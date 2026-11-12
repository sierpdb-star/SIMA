
from fastapi import FastAPI

app = FastAPI(
    title="S.I.M.A.",
    description="Sistema Inteligente de Mensagens Automatizadas",
    version="0.1.0"
)

@app.get("/")
def inicio():
    return {
        "projeto": "S.I.M.A.",
        "status": "online",
        "versao": "0.1.0",
        "mensagem": "Sistema iniciado com sucesso!"
    }

@app.get("/status")
def status():
    return {
        "sistema": "S.I.M.A.",
        "funcionamento": "inicializado",
        "envios_automaticos": False
    }
