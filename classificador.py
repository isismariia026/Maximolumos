import sqlite3
import re


def marcar_tipo_traducao(pacote):

    traducao = pacote.get("traducao")

    if traducao == "🤖 Tradução Mecânica":
        pacote["tipo_envio"] = "traducao"

    else:
        pacote["tipo_envio"] = "acervo"

    return pacote



def definir_destino(pacote):

    if pacote.get("tipo_envio") == "traducao":
        return "traducao"

    return "acervo"



def eh_grupo_traducao(pacote):

    return pacote.get("tipo_envio") == "traducao"



def mensagem_final_envio(pacote, link):

    if eh_grupo_traducao(pacote):

        return (
            "✨ Feitiço postado no grupo de tradução!\n\n"
            "🕯️ Seu E-book está aqui:\n"
            f"{link}"
        )

    return (
        "✨ Feitiço concluído com sucesso!\n\n"
        "🕯️ Seu E-book está aqui:\n"
        f"{link}"
    )
