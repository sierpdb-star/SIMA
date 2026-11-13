
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.campaign_models import Campaign
from app.models import Contact

router = APIRouter(prefix="/campanhas", tags=["Campanhas"])


def obter_banco():
    banco = SessionLocal()
    try:
        yield banco
    finally:
        banco.close()


class NovaCampanha(BaseModel):
    empresa_id: str
    nome: str
    mensagem: str
    canal: str


@router.post("/")
def criar_campanha(
    dados: NovaCampanha,
    banco: Session = Depends(obter_banco)
):
    if not dados.nome.strip() or not dados.mensagem.strip():
        raise HTTPException(
            status_code=400,
            detail="Nome e mensagem são obrigatórios."
        )

    campanha = Campaign(
        company_id=dados.empresa_id,
        name=dados.nome,
        message=dados.mensagem,
        channel=dados.canal,
        status="draft"
    )

    banco.add(campanha)
    banco.commit()
    banco.refresh(campanha)

    return {
        "mensagem": "Campanha criada como rascunho!",
        "id": campanha.id,
        "nome": campanha.name,
        "canal": campanha.channel,
        "status": campanha.status
    }


@router.get("/")
def listar_campanhas(
    empresa_id: str,
    banco: Session = Depends(obter_banco)
):
    campanhas = banco.query(Campaign).filter_by(
        company_id=empresa_id
    ).all()

    return [
        {
            "id": c.id,
            "nome": c.name,
            "mensagem": c.message,
            "canal": c.channel,
            "status": c.status
        }
        for c in campanhas
    ]


@router.get("/{campanha_id}/destinatarios")
def listar_destinatarios_autorizados(
    campanha_id: int,
    empresa_id: str,
    banco: Session = Depends(obter_banco)
):
    campanha = banco.query(Campaign).filter_by(
        id=campanha_id,
        company_id=empresa_id
    ).first()

    if not campanha:
        raise HTTPException(
            status_code=404,
            detail="Campanha não encontrada."
        )

    contatos = banco.query(Contact).filter_by(
        company_id=empresa_id,
        channel=campanha.channel,
        consent_status="granted"
    ).all()

    return {
        "campanha_id": campanha.id,
        "total_autorizados": len(contatos),
        "destinatarios": [
            {
                "id": contato.id,
                "nome": contato.name,
                "telefone": contato.phone,
                "canal": contato.channel
            }
            for contato in contatos
        ],
        "envios_automaticos": False
    }
