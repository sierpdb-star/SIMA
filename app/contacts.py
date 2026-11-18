
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .database import get_db
from .models import Contato


router = APIRouter(
    prefix="/contatos",
    tags=["Contatos"]
)


# Cadastrar contato
@router.post("/", status_code=201)
def criar_contato(
    nome: str = Query(..., min_length=2, max_length=150),
    telefone: str = Query(..., min_length=8, max_length=30),
    canal: str = Query("whatsapp", max_length=30),
    empresa_id: str = Query(..., min_length=1, max_length=100),
    db: Session = Depends(get_db)
):
    contato = Contato(
        nome=nome.strip(),
        telefone=telefone.strip(),
        canal=canal.strip().lower(),
        empresa_id=empresa_id.strip()
    )

    db.add(contato)
    db.commit()
    db.refresh(contato)

    return {
        "mensagem": "Contato cadastrado com sucesso.",
        "contato": {
            "id": contato.id,
            "nome": contato.nome,
            "telefone": contato.telefone,
            "canal": contato.canal,
            "empresa_id": contato.empresa_id
        }
    }


# Listar contatos de uma empresa
@router.get("/")
def listar_contatos(
    empresa_id: str = Query(...),
    db: Session = Depends(get_db)
):
    contatos = (
        db.query(Contato)
        .filter(Contato.empresa_id == empresa_id)
        .order_by(Contato.nome.asc())
        .all()
    )

    return [
        {
            "id": contato.id,
            "nome": contato.nome,
            "telefone": contato.telefone,
            "canal": contato.canal,
            "empresa_id": contato.empresa_id
        }
        for contato in contatos
    ]


# Consultar um contato específico
@router.get("/{contato_id}")
def obter_contato(
    contato_id: int,
    empresa_id: str = Query(...),
    db: Session = Depends(get_db)
):
    contato = (
        db.query(Contato)
        .filter(
            Contato.id == contato_id,
            Contato.empresa_id == empresa_id
        )
        .first()
    )

    if not contato:
        raise HTTPException(
            status_code=404,
            detail="Contato não encontrado."
        )

    return {
        "id": contato.id,
        "nome": contato.nome,
        "telefone": contato.telefone,
        "canal": contato.canal,
        "empresa_id": contato.empresa_id
    }


# Atualizar contato
@router.put("/{contato_id}")
def atualizar_contato(
    contato_id: int,
    dados: dict,
    empresa_id: str = Query(...),
    db: Session = Depends(get_db)
):
    contato = (
        db.query(Contato)
        .filter(
            Contato.id == contato_id,
            Contato.empresa_id == empresa_id
        )
        .first()
    )

    if not contato:
        raise HTTPException(
            status_code=404,
            detail="Contato não encontrado."
        )

    campos_permitidos = {
        "nome",
        "telefone",
        "canal"
    }

    for campo, valor in dados.items():
        if campo not in campos_permitidos:
            raise HTTPException(
                status_code=400,
                detail=f"Campo não permitido: {campo}"
            )

        if not isinstance(valor, str) or not valor.strip():
            raise HTTPException(
                status_code=400,
                detail=f"O campo {campo} deve conter texto válido."
            )

        setattr(
            contato,
            campo,
            valor.strip().lower() if campo == "canal" else valor.strip()
        )

    db.commit()
    db.refresh(contato)

    return {
        "mensagem": "Contato atualizado com sucesso.",
        "contato": {
            "id": contato.id,
            "nome": contato.nome,
            "telefone": contato.telefone,
            "canal": contato.canal,
            "empresa_id": contato.empresa_id
        }
    }


# Excluir contato
@router.delete("/{contato_id}")
def excluir_contato(
    contato_id: int,
    empresa_id: str = Query(...),
    db: Session = Depends(get_db)
):
    contato = (
        db.query(Contato)
        .filter(
            Contato.id == contato_id,
            Contato.empresa_id == empresa_id
        )
        .first()
    )

    if not contato:
        raise HTTPException(
            status_code=404,
            detail="Contato não encontrado."
        )

    db.delete(contato)
    db.commit()

    return {
        "mensagem": "Contato excluído com sucesso."
    }
