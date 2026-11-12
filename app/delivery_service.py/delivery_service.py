
def verificar_elegibilidade(campanha, contato):
    if campanha.company_id != contato.company_id:
        return {
            "autorizado": False,
            "motivo": "Contato pertence a outra empresa."
        }

    if campanha.channel != contato.channel:
        return {
            "autorizado": False,
            "motivo": "Canal do contato diferente da campanha."
        }

    if contato.consent_status != "granted":
        return {
            "autorizado": False,
            "motivo": "Contato sem consentimento ativo."
        }

    return {
        "autorizado": True,
        "motivo": "Contato elegível para envio."
    }
