
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .database import get_db
from .models import Campanha, Contato, HistoricoCampanha


router = APIRouter(
    prefix="/campanhas",
    tags=["Campanhas"]
)


def campanha_para_dict(campanha):
    return {
        "id": campanha.id,
        "empresa_id": campanha.empresa_id,
        "nome": campanha.nome,
        "mensagem": campanha.mensagem,
        "canal": campanha.canal,
        "tipo_conteudo": campanha.tipo_conteudo,
        "media_url": campanha.media_url,
        "media_type": campanha.media_type,
        "legenda": campanha.legenda,
        "status": campanha.status,
        "criada_em": (
            campanha.criada_em.isoformat()
            if campanha.criada_em else None
        )
    }


def historico_para_dict(registro):
    return {
        "id": registro.id,
        "campanha_id": registro.campanha_id,
        "nome": registro.nome,
        "status": registro.status,
        "data": registro.data.isoformat() if registro.data else None
    }


# Criar campanha
@router.post("/", status_code=201)
def criar_campanha(
    dados: dict,
    db: Session = Depends(get_db)
):
    nome = dados.get("nome", "").strip()
    empresa_id = dados.get("empresa_id", "").strip()

    if not nome:
        raise HTTPException(
            status_code=400,
            detail="O nome da campanha é obrigatório."
        )

    if not empresa_id:
        raise HTTPException(
            status_code=400,
            detail="O identificador da empresa é obrigatório."
        )

    tipo_conteudo = dados.get("tipo_conteudo", "text")

    if tipo_conteudo not in {"text", "image"}:
        raise HTTPException(
            status_code=400,
            detail="Tipo de conteúdo inválido."
        )

    media_url = dados.get("media_url")
    media_type = dados.get("media_type")

    if tipo_conteudo == "image":
        if not media_url or not media_type:
            raise HTTPException(
                status_code=400,
                detail="A campanha com imagem precisa de um arquivo."
            )

        if media_type not in {"image/jpeg", "image/png"}:
            raise HTTPException(
                status_code=400,
                detail="Formato de imagem não permitido."
            )

    campanha = Campanha(
        empresa_id=empresa_id,
        nome=nome,
        mensagem=dados.get("mensagem", ""),
        canal=dados.get("canal", "whatsapp"),
        tipo_conteudo=tipo_conteudo,
        media_url=media_url,
        media_type=media_type,
        legenda=dados.get("legenda", ""),
        status="rascunho"
    )

    db.add(campanha)
    db.commit()
    db.refresh(campanha)

    return campanha_para_dict(campanha)


# Listar campanhas
@router.get("/")
def listar_campanhas(
    empresa_id: str = Query(...),
    db: Session = Depends(get_db)
):
    campanhas = (
        db.query(Campanha)
        .filter(Campanha.empresa_id == empresa_id)
        .order_by(Campanha.id.desc())
        .all()
    )

    return [
        campanha_para_dict(campanha)
        for campanha in campanhas
    ]


# Consultar histórico geral
@router.get("/historico")
def listar_historico(
    empresa_id: str = Query(...),
    db: Session = Depends(get_db)
):
    registros = (
        db.query(HistoricoCampanha)
        .join(
            Campanha,
            HistoricoCampanha.campanha_id == Campanha.id
        )
        .filter(Campanha.empresa_id == empresa_id)
        .order_by(HistoricoCampanha.data.desc())
        .all()
    )

    return [
        historico_para_dict(registro)
        for registro in registros
    ]


# Consultar histórico de uma campanha
@router.get("/{campanha_id}/historico")
def historico_campanha(
    campanha_id: int,
    empresa_id: str = Query(...),
    db: Session = Depends(get_db)
):
    campanha = (
        db.query(Campanha)
        .filter(
            Campanha.id == campanha_id,
            Campanha.empresa_id == empresa_id
        )
        .first()
    )

    if not campanha:
        raise HTTPException(
            status_code=404,
            detail="Campanha não encontrada."
        )

    registros = (
        db.query(HistoricoCampanha)
        .filter(HistoricoCampanha.campanha_id == campanha_id)
        .order_by(HistoricoCampanha.data.desc())
        .all()
    )

    return [
        historico_para_dict(registro)
        for registro in registros
    ]


# Listar destinatários de uma campanha
@router.get("/{campanha_id}/destinatarios")
def listar_destinatarios(
    campanha_id: int,
    empresa_id: str = Query(...),
    db: Session = Depends(get_db)
):
    campanha = (
        db.query(Campanha)
        .filter(
            Campanha.id == campanha_id,
            Campanha.empresa_id == empresa_id
        )
        .first()
    )

    if not campanha:
        raise HTTPException(
            status_code=404,
            detail="Campanha não encontrada."
        )

    return [
        {
            "id": contato.id,
            "nome": contato.nome,
            "telefone": contato.telefone,
            "canal": contato.canal
        }
        for contato in campanha.contatos
    ]


# Associar contatos à campanha
@router.post("/{campanha_id}/destinatarios")
def adicionar_destinatarios(
    campanha_id: int,
    dados: dict,
    empresa_id: str = Query(...),
    db: Session = Depends(get_db)
):
    campanha = (
        db.query(Campanha)
        .filter(
            Campanha.id == campanha_id,
            Campanha.empresa_id == empresa_id
        )
        .first()
    )

    if not campanha:
        raise HTTPException(
            status_code=404,
            detail="Campanha não encontrada."
        )

    ids = dados.get("contatos_ids", [])

    if not isinstance(ids, list) or not ids:
        raise HTTPException(
            status_code=400,
            detail="Informe uma lista de IDs de contatos."
        )

    contatos = (
        db.query(Contato)
        .filter(
            Contato.id.in_(ids),
            Contato.empresa_id == empresa_id
        )
        .all()
    )

    if len(contatos) != len(set(ids)):
        raise HTTPException(
            status_code=400,
            detail="Um ou mais contatos não foram encontrados nesta empresa."
        )

    existentes = {contato.id for contato in campanha.contatos}

    for contato in contatos:
        if contato.id not in existentes:
            campanha.contatos.append(contato)

    db.commit()
    db.refresh(campanha)

    return {
        "mensagem": "Destinatários associados com sucesso.",
        "total_destinatarios": len(campanha.contatos),
        "envio_automatico": False
    }


# Preparar campanha sem enviar mensagens
@router.post("/{campanha_id}/preparar")
def preparar_campanha(
    campanha_id: int,
    empresa_id: str = Query(...),
    db: Session = Depends(get_db)
):
    campanha = (
        db.query(Campanha)
        .filter(
            Campanha.id == campanha_id,
            Campanha.empresa_id == empresa_id
        )
        .first()
    )

    if not campanha:
        raise HTTPException(
            status_code=404,
            detail="Campanha não encontrada."
        )

    if campanha.tipo_conteudo == "text" and not campanha.mensagem.strip():
        raise HTTPException(
            status_code=400,
            detail="A mensagem da campanha está vazia."
        )

    if campanha.tipo_conteudo == "image" and not campanha.media_url:
        raise HTTPException(
            status_code=400,
            detail="A campanha não possui imagem."
        )

    campanha.status = "preparada"

    registro = HistoricoCampanha(
        campanha_id=campanha.id,
        nome=campanha.nome,
        status="preparada",
        data=datetime.now(timezone.utc)
    )

    db.add(registro)
    db.commit()
    db.refresh(campanha)

    return {
        "mensagem": "Campanha preparada com sucesso.",
        "envio_automatico": False,
        "campanha": campanha_para_dict(campanha)
    }
