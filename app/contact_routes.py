
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Contact

router = APIRouter(prefix="/contatos", tags=["Contatos"])


def obter_banco():
    banco = SessionLocal()
    try:
        yield banco
    finally:
        banco.close()


class RegistrarConsentimento(BaseModel):
    empresa_id: str
    origem: str


@router.post("/")
def cadastrar_contato(
    nome: str,
    telefone: str,
    canal: str,
    empresa_id: str,
    banco: Session = Depends(obter_banco)
):
    existente = banco.query(Contact).filter_by(
        company_id=empresa_id,
        phone=telefone,
        channel=canal
    ).first()

    if existente:
        raise HTTPException(
            status_code=409,
            detail="Este contato já está cadastrado."
        )

    contato = Contact(
        company_id=empresa_id,
        name=nome,
        phone=telefone,
        channel=canal,
        consent_status="pending"
    )

    banco.add(contato)
    banco.commit()
    banco.refresh(contato)

    return {
        "mensagem": "Contato cadastrado sem autorização de envio.",
        "id": contato.id,
        "nome": contato.name,
        "consentimento": contato.consent_status
    }


@router.get("/")
def listar_contatos(
    empresa_id: str,
    banco: Session = Depends(obter_banco)
):
    contatos = banco.query(Contact).filter_by(
        company_id=empresa_id
    ).all()

    return [
        {
            "id": c.id,
            "nome": c.name,
            "telefone": c.phone,
            "canal": c.channel,
            "consentimento": c.consent_status
        }
        for c in contatos
    ]


@router.post("/{contato_id}/consentimento")
def registrar_consentimento(
    contato_id: int,
    dados: RegistrarConsentimento,
    banco: Session = Depends(obter_banco)
):
    contato = banco.query(Contact).filter_by(
        id=contato_id,
        company_id=dados.empresa_id
    ).first()

    if not contato:
        raise HTTPException(
            status_code=404,
            detail="Contato não encontrado."
        )

    if not dados.origem.strip():
        raise HTTPException(
            status_code=400,
            detail="A origem do consentimento é obrigatória."
        )

    contato.consent_status = "granted"
    contato.consent_source = dados.origem
    contato.consent_at = datetime.now(timezone.utc)
    contato.opted_out_at = None

    banco.commit()

    return {
        "mensagem": "Consentimento registrado.",
        "contato_id": contato.id,
        "consentimento": contato.consent_status,
        "origem": contato.consent_source
    }


@router.post("/{contato_id}/descadastro")
def descadastrar_contato(
    contato_id: int,
    empresa_id: str,
    banco: Session = Depends(obter_banco)
):
    contato = banco.query(Contact).filter_by(
        id=contato_id,
        company_id=empresa_id
    ).first()

    if not contato:
        raise HTTPException(
            status_code=404,
            detail="Contato não encontrado."
        )

    contato.consent_status = "revoked"
    contato.opted_out_at = datetime.now(timezone.utc)

    banco.commit()

    return {
        "mensagem": "Descadastro registrado.",
        "contato_id": contato.id,
        "consentimento": contato.consent_status
    }
