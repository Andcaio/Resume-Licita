import glob
import os

import config
from leitor_pdf import extrair_texto_documentos
from analisador_ia import resumir_edital

PASTA_SAIDA = "resumo"
ARQUIVO_SAIDA = os.path.join(PASTA_SAIDA, "resumo_final.txt")


def main():
    if not config.get_api_key():
        print(
            "❌ GEMINI_API_KEY não configurada. Crie um arquivo .env (veja .env.example) "
            "ou abra app.pyw para configurar a chave pela interface gráfica."
        )
        return

    documentos = sorted(glob.glob("editais/*.pdf"))
    if not documentos:
        print("❌ Nenhum arquivo .pdf encontrado nesta pasta.")
        return

    print("🚀 Iniciando análise combinada de documentos...")

    try:
        texto_total_licitacao = extrair_texto_documentos(documentos)
    except FileNotFoundError as erro:
        print(f"❌ Erro: O arquivo '{erro}' não foi encontrado na pasta.")
        return

    if len(texto_total_licitacao.strip()) < 150:
        print("⚠️ Alerta: Os documentos parecem ser imagens escaneadas ou estão muito curtos.")
        return

    try:
        resultado_resumo = resumir_edital(texto_total_licitacao)
    except Exception as erro:
        print(f"💥 Ocorreu um erro inesperado durante a execução: {erro}")
        return

    if "❌ Falha" in resultado_resumo:
        print(resultado_resumo)
        return

    print("\n✨ --- RESUMO GERADO COM SUCESSO --- ✨\n")
    os.makedirs(PASTA_SAIDA, exist_ok=True)
    with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
        f.write(resultado_resumo)
    print(f"\n💾 Sucesso! Salvo em '{ARQUIVO_SAIDA}'.")


if __name__ == "__main__":
    main()
