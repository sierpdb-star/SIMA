
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
        consent_status="granted" if consentimento else "pending"
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
