
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile


router = APIRouter(
    prefix="/arquivos",
    tags=["Arquivos"]
)

PASTA_UPLOADS = Path(__file__).resolve().parent.parent / "uploads"

TAMANHO_MAXIMO = 5 * 1024 * 1024

PASTA_UPLOADS.mkdir(parents=True, exist_ok=True)


def identificar_imagem(conteudo: bytes):
    if conteudo.startswith(b"\xff\xd8\xff"):
        return ".jpg", "image/jpeg"

    if conteudo.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png", "image/png"

    return None, None


@router.post("/imagem")
async def enviar_imagem(
    arquivo: UploadFile = File(...)
):
    if not arquivo.filename:
        raise HTTPException(
            status_code=400,
            detail="Selecione uma imagem."
        )

    conteudo = await arquivo.read(TAMANHO_MAXIMO + 1)

    if not conteudo:
        raise HTTPException(
            status_code=400,
            detail="O arquivo está vazio."
        )

    if len(conteudo) > TAMANHO_MAXIMO:
        raise HTTPException(
            status_code=413,
            detail="A imagem deve ter no máximo 5 MB."
        )

    extensao, tipo_mime = identificar_imagem(conteudo)

    if not extensao:
        raise HTTPException(
            status_code=400,
            detail="Formato inválido. Envie uma imagem JPG ou PNG."
        )

    nome_arquivo = f"{uuid4().hex}{extensao}"
    caminho = PASTA_UPLOADS / nome_arquivo

    try:
        caminho.write_bytes(conteudo)
    except OSError:
        raise HTTPException(
            status_code=500,
            detail="Não foi possível salvar a imagem."
        )

    return {
        "mensagem": "Imagem enviada com sucesso!",
        "arquivo": nome_arquivo,
        "media_url": f"/uploads/{nome_arquivo}",
        "media_type": tipo_mime,
        "tamanho_bytes": len(conteudo),
        "envios_automaticos": False
    }
