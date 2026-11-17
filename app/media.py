from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/arquivos", tags=["Arquivos"])

PASTA_IMAGENS = Path("uploads")
PASTA_IMAGENS.mkdir(parents=True, exist_ok=True)

TIPOS_PERMITIDOS = {
    "image/jpeg": ".jpg",
    "image/png": ".png"
}

LIMITE_BYTES = 5 * 1024 * 1024


@router.post("/imagem")
async def enviar_imagem(arquivo: UploadFile = File(...)):
    if arquivo.content_type not in TIPOS_PERMITIDOS:
        raise HTTPException(
            status_code=400,
            detail="Envie uma imagem JPG ou PNG."
        )

    conteudo = await arquivo.read()

    if not conteudo:
        raise HTTPException(
            status_code=400,
            detail="O arquivo está vazio."
        )

    if len(conteudo) > LIMITE_BYTES:
        raise HTTPException(
            status_code=400,
            detail="A imagem deve ter no máximo 5 MB."
        )

    extensao = TIPOS_PERMITIDOS[arquivo.content_type]
    nome_arquivo = f"{uuid4().hex}{extensao}"

    caminho = PASTA_IMAGENS / nome_arquivo
    caminho.write_bytes(conteudo)

    return {
        "media_url": f"/arquivos/imagem/{nome_arquivo}",
        "media_type": arquivo.content_type,
        "envios_automaticos": False
    }


@router.get("/imagem/{nome_arquivo}")
def obter_imagem(nome_arquivo: str):
    if Path(nome_arquivo).name != nome_arquivo:
        raise HTTPException(status_code=400, detail="Nome inválido.")

    caminho = PASTA_IMAGENS / nome_arquivo

    if not caminho.is_file():
        raise HTTPException(
            status_code=404,
            detail="Imagem não encontrada."
        )

    return FileResponse(caminho)
