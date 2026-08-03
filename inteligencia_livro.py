from ebooklib import epub
from bs4 import BeautifulSoup
from langdetect import detect
import re


def extrair_sinopse_metadados(livro):
    campos = [
        ("DC", "description"),
        ("OPF", "description"),
        ("DC", "subject")
    ]

    for namespace, campo in campos:

        dados = livro.get_metadata(namespace, campo)

        if dados:

            texto = dados[0][0].strip()

            if len(texto) > 80:
                return texto

    return None


def extrair_sinopse_inicio(capitulos):
    palavras = [
        "sinopse",
        "sobre o livro",
        "blurb",
        "resumo"
    ]

    for texto in capitulos[:5]:

        texto_lower = texto.lower()

        for palavra in palavras:

            if palavra in texto_lower:

                indice = texto_lower.find(palavra)

                trecho = texto[indice:]

                if len(trecho) > 150:
                    return trecho[:3000]

    return None


def gerar_resumo(capitulos):
    texto = "\n".join(capitulos)

    frases = re.split(r"[.!?]", texto)

    resumo = []

    for frase in frases:

        frase = frase.strip()

        if len(frase) > 80:
            resumo.append(frase)

        if len(resumo) >= 10:
            break

    return "\n".join(resumo)


def criar_memoria_temporaria():
    return {

        "generos": {},

        "evidencias": {},

        "capitulos_lidos": 0,

        "frases_encontradas": []

    }


def ler_inicio_epub(caminho):
    livro = epub.read_epub(caminho)

    textos = []

    for item in livro.get_items():

        if item.get_type() == 9:  # documento HTML

            soup = BeautifulSoup(
                item.get_content(),
                "html.parser"
            )

            texto = soup.get_text(" ", strip=True)

            if texto:
                textos.append(texto)

    texto_final = "\n".join(textos)

    # pega somente o começo
    inicio = texto_final[:15000]

    return inicio


def ler_livro_completo(caminho):
    livro = epub.read_epub(caminho)

    capitulos = []

    for item in livro.get_items():

        if item.get_type() == 9:

            soup = BeautifulSoup(
                item.get_content(),
                "html.parser"
            )

            texto = soup.get_text(
                " ",
                strip=True
            )

            if texto:
                capitulos.append(texto)

    return capitulos


def analisar_contexto(texto, memoria):
    texto = texto.lower()

    regras = {

        # =====================
        # GÊNEROS PRINCIPAIS
        # =====================

        "#fantasia": [
            "fantasia",
            "fantasy",
            "magia",
            "mágica",
            "feitiço",
            "feitico",
            "reino mágico",
            "reino encantado",
            "criaturas sobrenaturais",
            "poderes mágicos",
            "profecia",
            "dragão",
            "dragão",
            "vampiro",
            "lobisomem",
            "bruxa",
            "feérico",
            "fae"
        ],

        "#mafia": [
            "máfia",
            "mafia",
            "mafioso",
            "bratva",
            "camorra",
            "cartel",
            "família mafiosa",
            "chefe da máfia",
            "don da máfia",
            "organização criminosa",
            "submundo criminoso"
        ],

        "#darkromance": [
            "dark romance",
            "homem possessivo",
            "obsessão por ela",
            "amor sombrio",
            "homem perigoso",
            "relacionamento obsessivo"
        ],

        "#romance": [
            "romance",
            "amor",
            "love",
            "apaixonado",
            "apaixonada"
        ],

        # =====================
        # ELEMENTOS DE FANTASIA
        # =====================

        "#dragao": [
            "dragão",
            "dragões",
            "dragon",
            "dragons",
            "montador de dragão",
            "cavaleiro de dragão"
        ],

        "#vampiro": [
            "vampiro",
            "vampira",
            "vampire",
            "sede de sangue",
            "imortal da noite",
            "mordida no pescoço"
        ],

        "#lobisomem": [
            "lobisomem",
            "werewolf",
            "homem lobo",
            "matilha",
            "alcateia",
            "alfa da matilha"
        ],

        "#bruxas": [
            "bruxa",
            "bruxas",
            "witch",
            "feiticeira",
            "feiticeiro"
        ],

        "#feericos": [
            "feérico",
            "feéricos",
            "fae",
            "fey",
            "fairy",
            "fadas",
            "corte feérica",
            "reino feérico"
        ],

        # =====================
        # ROMANCES ESPECÍFICOS
        # =====================

        "#harémreverso": [
            "reverse harem",
            "reverseharem",
            "harém reverso",
            "why choose",
            "multiple love interests"
        ],

        "#bilionario": [
            "bilionário",
            "billionaire",
            "ceo"
        ]

    }

    for genero, palavras in regras.items():

        pontos = 0

        for palavra in palavras:
            quantidade = texto.count(palavra)

            pontos += quantidade

        if pontos > 0:
            memoria["generos"][genero] = (
                    memoria["generos"].get(genero, 0)
                    + pontos
            )


def analisar_livro_com_memoria(caminho):
    memoria = criar_memoria_temporaria()

    capitulos = ler_livro_completo(caminho)

    for capitulo in capitulos:
        analisar_contexto(capitulo, memoria)

    generos = memoria["generos"]

    hashtags = []

    # ==========================
    # GÊNERO PRINCIPAL
    # ==========================

    if generos.get("#fantasia", 0) >= 15:

        hashtags.append("#fantasia")

        elementos = [

            "#dragao",
            "#vampiro",
            "#lobisomem",
            "#bruxas",
            "#feericos"

        ]

        elementos.sort(
            key=lambda x: generos.get(x, 0),
            reverse=True
        )

        for tag in elementos:

            if generos.get(tag, 0) > 0:
                hashtags.append(tag)

            if len(hashtags) == 3:
                break


    elif generos.get("#mafia", 0) >= 8:

        hashtags.append("#mafia")

        if generos.get("#darkromance", 0) > 0:
            hashtags.append("#darkromance")

        if generos.get("#romance", 0) > 0:
            hashtags.append("#romance")


    else:

        ordem = sorted(
            generos.items(),
            key=lambda x: x[1],
            reverse=True
        )

        for tag, _ in ordem:

            hashtags.append(tag)

            if len(hashtags) == 3:
                break

    memoria.clear()

    return hashtags[:3]


def gerar_hashtags(texto):
    texto = texto.lower()

    pontos = {}

    banco = {

        "#romance": [
            "romance",
            "amor",
            "love"
        ],

        "#darkromance": [
            "dark romance",
            "obsessão",
            "homem possessivo",
            "amor sombrio"
        ],

        "#mafia": [
            "máfia",
            "mafia",
            "mafioso",
            "bratva",
            "camorra"
        ],

        "#fantasia": [
            "fantasia",
            "magia",
            "dragão",
            "dragao",
            "vampiro",
            "lobisomem",
            "bruxa",
            "fae",
            "feérico"
        ]

    }

    for hashtag, palavras in banco.items():

        pontos[hashtag] = 0

        for palavra in palavras:
            pontos[hashtag] += texto.count(palavra)

    resultado = sorted(
        pontos,
        key=pontos.get,
        reverse=True
    )

    hashtags = []

    for tag in resultado:

        if pontos[tag] > 0:
            hashtags.append(tag)

        if len(hashtags) == 3:
            break

    if not hashtags:
        hashtags.append("#romance")

    return hashtags


def garantir_hashtag(lista):
    lista_final = []

    for tag in lista:

        if not tag.startswith("#"):
            tag = "#" + tag

        lista_final.append(tag)

    if not lista_final:
        lista_final.append("#romance")

    return lista_final[:3]


def analisar_livro(caminho):
    livro = epub.read_epub(caminho)

    capitulos = ler_livro_completo(caminho)

    sinopse = extrair_sinopse_metadados(livro)

    origem = "metadados"

    if not sinopse:
        sinopse = extrair_sinopse_inicio(capitulos)

        origem = "inicio"

    if not sinopse:
        sinopse = gerar_resumo(capitulos)

        origem = "resumo"

    return {

        "sinopse": sinopse,

        "origem": origem

    }