from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone

router = APIRouter(prefix="/campanhas", tags=["Campanhas"])

campanhas = []
historico = []
proximo_id = 1


@router.post("/")
def criar_campanha(dados: dict):
    global proximo_id

    nome = dados.get("nome", "").strip()
    empresa_id = dados.get("empresa_id", "padrao")

    if not nome:
        raise HTTPException(
            status_code=400,
            detail="O nome da campanha é obrigatório."
        )

    campanha = {
        "id": proximo_id,
        "empresa_id": empresa_id,
        "nome": nome,
        "mensagem": dados.get("mensagem", ""),
        "canal": dados.get("canal", "whatsapp"),
        "tipo_conteudo": dados.get("tipo_conteudo", "text"),
        "media_url": dados.get("media_url"),
        "media_type": dados.get("media_type"),
        "legenda": dados.get("legenda", ""),
        "status": "rascunho",
        "criada_em": datetime.now(timezone.utc).isoformat()
    }

    campanhas.append(campanha)
    proximo_id += 1

    return campanha


@router.get("/")
def listar_campanhas(empresa_id: str = None):
    if empresa_id:
        return [
            c for c in campanhas
            if c["empresa_id"] == empresa_id
        ]

    return campanhas


@router.get("/historico")
def listar_historico():
    return historico
@router.get("/{campanha_id}/historico")
def historico_campanha(campanha_id: int):
    return [
        
        item for item in historico
        if item["campanha_id"] == campanha_id
    ]


@router.get("/{campanha_id}/destinatarios")
def listar_destinatarios(campanha_id: int):
    campanha = next(
        (c for c in campanhas if c["id"] == campanha_id),
        None
    )

    if not campanha:
        raise HTTPException(
            status_code=404,
            detail="Campanha não encontrada."
        )

    return []


@router.post("/{campanha_id}/preparar")
def preparar_campanha(campanha_id: int):
    campanha = next(
        (c for c in campanhas if c["id"] == campanha_id),
        None
    )

    if not campanha:
        raise HTTPException(
            status_code=404,
            detail="Campanha não encontrada."
        )

    campanha["status"] = "preparada"

    registro = {
        "campanha_id": campanha_id,
        "nome": campanha["nome"],
        "status": "preparada",
        "data": datetime.now(timezone.utc).isoformat()
    }

    historico.append(registro)

    return {
        "mensagem": "Campanha preparada.",
        "envio_automatico": False,
        "campanha": campanha
    }
