from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/contatos", tags=["Contatos"])

contatos = []
proximo_id = 1


@router.post("/")
def cadastrar_contato(
    nome: str,
    telefone: str,
    canal: str = "whatsapp",
    empresa_id: str = "padrao"
):
    global proximo_id

    if not nome.strip() or not telefone.strip():
        raise HTTPException(
            status_code=400,
            detail="Nome e telefone são obrigatórios."
        )

    contato = {
        "id": proximo_id,
        "nome": nome,
        "telefone": telefone,
        "canal": canal,
        "empresa_id": empresa_id
    }

    contatos.append(contato)
    proximo_id += 1

    return contato


@router.get("/")
def listar_contatos(empresa_id: str):
    return [
        contato for contato in contatos
        if contato["empresa_id"] == empresa_id
    ]
