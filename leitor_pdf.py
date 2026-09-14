import os

from pypdf import PdfReader


def extrair_texto_pdf(caminho_pdf, log=print):
    log(f"Lendo arquivo: {caminho_pdf}")
    reader = PdfReader(caminho_pdf)
    texto_completo = ""

    for pagina in reader.pages:
        texto_pagina = pagina.extract_text()
        if texto_pagina:
            texto_completo += texto_pagina + "\n"
    return texto_completo


def extrair_texto_documentos(lista_de_documentos, log=print):
    """Lê e concatena o texto de vários PDFs. Lança FileNotFoundError se algum arquivo não existir."""
    texto_total = ""
    for arquivo in lista_de_documentos:
        if not os.path.exists(arquivo):
            raise FileNotFoundError(arquivo)
        texto_total += f"\n\n=== CONTEÚDO DO ARQUIVO: {arquivo} ===\n"
        texto_total += extrair_texto_pdf(arquivo, log=log)
    return texto_total
