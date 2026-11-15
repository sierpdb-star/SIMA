
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.campaign_models import Campaign
from app.content_models import CampaignContent
from app.models import Contact
from app.delivery_models import DeliveryLog

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
    mensagem: str = ""
    canal: str
    tipo_conteudo: str = "text"
    media_url: str | None = None
    media_type: str | None = None
    legenda: str | None = None


@router.post("/")
def criar_campanha(
    dados: NovaCampanha,
    banco: Session = Depends(obter_banco)
):
    if not dados.nome.strip():
        raise HTTPException(
            status_code=400,
            detail="O nome da campanha é obrigatório."
        )

    tipo = dados.tipo_conteudo.strip().lower()

    if tipo not in ["text", "image"]:
        raise HTTPException(
            status_code=400,
            detail="Tipo de conteúdo inválido. Use text ou image."
        )

    if tipo == "text" and not dados.mensagem.strip():
        raise HTTPException(
            status_code=400,
            detail="A mensagem da campanha é obrigatória."
        )

    if tipo == "image" and not dados.media_url:
        raise HTTPException(
            status_code=400,
            detail="Informe a URL da imagem."
        )

    campanha = Campaign(
        company_id=dados.empresa_id,
        name=dados.nome,
        message=dados.mensagem or dados.legenda or "",
        channel=dados.canal,
        status="draft"
    )

    banco.add(campanha)
    banco.flush()

    conteudo = CampaignContent(
        campaign_id=campanha.id,
        content_type=tipo,
        text_content=(
            dados.legenda
            if tipo == "image"
            else dados.mensagem
        ),
        media_url=dados.media_url if tipo == "image" else None,
        media_type=dados.media_type if tipo == "image" else None
    )

    banco.add(conteudo)
    banco.commit()
    banco.refresh(campanha)
    banco.refresh(conteudo)

    return {
        "mensagem": "Campanha criada como rascunho!",
        "id": campanha.id,
        "nome": campanha.name,
        "canal": campanha.channel,
        "status": campanha.status,
        "tipo_conteudo": conteudo.content_type,
        "texto": conteudo.text_content,
        "media_url": conteudo.media_url,
        "media_type": conteudo.media_type,
        "envios_automaticos": False
    }


@router.get("/")
def listar_campanhas(
    empresa_id: str,
    banco: Session = Depends(obter_banco)
):
    campanhas = banco.query(Campaign).filter_by(
        company_id=empresa_id
    ).all()

    resultado = []

    for campanha in campanhas:
        conteudo = banco.query(CampaignContent).filter_by(
            campaign_id=campanha.id
        ).first()

        resultado.append({
            "id": campanha.id,
            "nome": campanha.name,
            "mensagem": campanha.message,
            "canal": campanha.channel,
            "status": campanha.status,
            "tipo_conteudo": (
                conteudo.content_type if conteudo else "text"
            ),
            "texto": (
                conteudo.text_content if conteudo else campanha.message
            ),
            "media_url": conteudo.media_url if conteudo else None,
            "media_type": conteudo.media_type if conteudo else None
        })

    return resultado


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
                "id": c.id,
                "nome": c.name,
                "telefone": c.phone,
                "canal": c.channel
            }
            for c in contatos
        ],
        "envios_automaticos": False
    }


@router.post("/{campanha_id}/preparar")
def preparar_historico(
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

    novos_registros = 0

    for contato in contatos:
        existente = banco.query(DeliveryLog).filter_by(
            campaign_id=campanha.id,
            contact_id=contato.id
        ).first()

        if existente:
            continue

        registro = DeliveryLog(
            campaign_id=campanha.id,
            contact_id=contato.id,
            channel=campanha.channel,
            status="pending"
        )

        banco.add(registro)
        novos_registros += 1

    banco.commit()

    return {
        "mensagem": "Destinatários preparados para processamento futuro.",
        "campanha_id": campanha.id,
        "novos_registros": novos_registros,
        "envios_automaticos": False
    }


@router.get("/{campanha_id}/historico")
def consultar_historico(
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

    registros = (
        banco.query(DeliveryLog, Contact)
        .join(Contact, DeliveryLog.contact_id == Contact.id)
        .filter(
            DeliveryLog.campaign_id == campanha.id,
            Contact.company_id == empresa_id
        )
        .all()
    )

    return {
        "campanha_id": campanha.id,
        "campanha": campanha.name,
        "total_registros": len(registros),
        "historico": [
            {
                "contato": contato.name,
                "telefone": contato.phone,
                "canal": registro.channel,
                "status": registro.status,
                "criado_em": registro.created_at.isoformat()
                if registro.created_at else None
            }
            for registro, contato in registros
        ],
        "envios_automaticos": False
    }
