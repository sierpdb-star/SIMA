

from fastapi import FastAPI

from app.database import criar_banco

# Importar os modelos para registrar todas as tabelas
from app import models
from app import campaign_models
from app import delivery_models


app = FastAPI(
    title="S.I.M.A.",
    description="Sistema Inteligente de Mensagens Automatizadas",
    version="0.2.0"
)


@app.on_event("startup")
def inicializar_sistema():
    criar_banco()


@app.get("/")
def inicio():
    return {
        "projeto": "S.I.M.A.",
        "status": "online",
        "versao": "0.2.0",
        "mensagem": "Sistema iniciado com sucesso!"
    }


@app.get("/status")
def status():
    return {
        "sistema": "S.I.M.A.",
        "funcionamento": "inicializado",
        "banco_de_dados": "configurado",
        "envios_automaticos": False
    }
