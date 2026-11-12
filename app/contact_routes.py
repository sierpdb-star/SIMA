
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
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


@router.post("/")
def cadastrar_contato(
    nome: str,
    telefone: str,
    canal: str,
    empresa_id: str,
    consentimento: bool = False,
    origem_consentimento: str | None = None,
    banco: Session = Depends(obter_banco)
):
    if not nome.strip() or not telefone.strip():
        raise HTTPException(
            status_code=400,
            detail="Nome e telefone são obrigatórios."
        )

    if not empresa_id.strip():
        raise HTTPException(
            status_code=400,
            detail="Empresa é obrigatória."
        )

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

    autorizado = consentimento and bool(
        origem_consentimento and origem_consentimento.strip()
    )

    agora = datetime.now(timezone.utc)

    contato = Contact(
        company_id=empresa_id,
        name=nome.strip(),
        phone=telefone.strip(),
        channel=canal,
        consent_status="granted" if autorizado else "pending",
        consent_source=origem_consentimento.strip()
        if autorizado else None,
        consent_at=agora if autorizado else None
    )

    banco.add(contato)
    banco.commit()
    banco.refresh(contato)

    return {
        "mensagem": "Contato cadastrado com sucesso!",
        "id": contato.id,
        "nome": contato.name,
        "telefone": contato.phone,
        "canal": contato.channel,
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


@router.post("/{contato_id}/descadastrar")
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
        "mensagem": "Contato descadastrado com sucesso.",
        "id": contato.id,
        "consentimento": contato.consent_status
    }
