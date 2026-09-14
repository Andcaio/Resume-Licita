import time

from google import genai

import config

PROMPT_BASE = (
    "Você é um advogado especialista em licitações públicas brasileiras, analisando um edital para uma "
    "empresa que pretende participar do certame.\n\n"

    "O resultado será salvo direto em um arquivo .txt simples, sem nenhum processador de markdown. "
    "Por isso, siga estas regras de formatação à risca:\n"
    "- NÃO use markdown (nada de **negrito**, #, *, ```` ``` ````, etc.) — texto puro apenas.\n"
    "- Antes de cada seção numerada, escreva uma linha só com travessões (--------------------).\n"
    "- Escreva os títulos das seções e subseções em MAIÚSCULAS.\n"
    "- Use \"-\" para itens de lista e deixe uma linha em branco entre itens longos, para facilitar a leitura.\n"
    "- Parágrafos curtos, um assunto por parágrafo.\n\n"

    "DIRETRIZ CRÍTICA DE RASTREABILIDADE:\n"
    "Para CADA informação, exigência, prazo ou valor que você extrair, indique explicitamente o número do "
    "Item, Subitem, Cláusula ou Capítulo onde essa informação se encontra no texto original "
    "(Exemplo: [Ref: Item 8.1.2] ou [Ref: Cláusula 5ª, parágrafo único]). Se a informação constar no Termo "
    "de Referência, indique (Exemplo: [Ref: TR - Item 3.2]). Jamais invente uma referência.\n\n"

    "DIRETRIZ CRÍTICA DE COMPLETUDE (para não deixar nada importante passar despercebido):\n"
    "- Leia o edital e o Termo de Referência INTEIROS, incluindo anexos, antes de responder. Não resuma por amostragem.\n"
    "- Cubra TODOS os tópicos abaixo, na ordem. Se uma informação não constar no texto, escreva "
    "\"Não localizado no texto fornecido\" nesse tópico — nunca omita um tópico silenciosamente.\n"
    "- Use a seção 8 para registrar qualquer cláusula relevante que não se encaixe nos tópicos anteriores.\n\n"

    "Estruture o resumo nos seguintes tópicos:\n\n"

    "1. IDENTIFICAÇÃO DO CERTAME\n"
    "   Órgão/entidade licitante, número do edital/processo, modalidade (pregão eletrônico, concorrência, "
    "dispensa, etc.) e critério de julgamento (menor preço, técnica e preço, etc.) -> Indique a referência.\n\n"

    "2. OBJETO\n"
    "   O que exatamente está sendo contratado ou comprado? A disputa é por item, por lote ou de forma "
    "global? -> Indique a referência.\n\n"

    "3. VALOR\n"
    "   Valor estimado ou orçamento máximo, total e por item/lote quando houver -> Indique a referência.\n\n"

    "4. CRONOGRAMA\n"
    "   Data/horário da sessão pública, prazo para envio de propostas, prazo para pedidos de esclarecimento "
    "e prazo para impugnação -> Indique a referência.\n\n"

    "5. REQUISITOS OBRIGATÓRIOS DE HABILITAÇÃO (O CORAÇÃO DO EDITAL)\n"
    "   Extraia detalhadamente o que é exigido em cada subitem abaixo:\n\n"
    "   A) HABILITAÇÃO JURÍDICA\n"
    "   Quais documentos da empresa são exigidos? (Ex: Contrato social, estatuto, decreto de autorização, "
    "etc.) -> Indique a referência.\n\n"
    "   B) QUALIFICAÇÃO TÉCNICA\n"
    "   Quais atestados de capacidade técnica são pedidos? Há exigência de registro em conselho de classe "
    "(CREA, CRA, CAU, etc.)? Exige equipe mínima ou responsável técnico específico? -> Indique a referência.\n\n"
    "   C) QUALIFICAÇÃO ECONÔMICO-FINANCEIRA\n"
    "   Exige balanço patrimonial? Quais os índices de liquidez exigidos (LG, SG, LC)? Há exigência de "
    "capital mínimo ou patrimônio líquido? Pede certidão negativa de falência? -> Indique a referência.\n\n"
    "   D) REGULARIDADE FISCAL, SOCIAL E TRABALHISTA\n"
    "   Quais certidões são explicitamente cobradas? (Certidão Federal/PGFN, Estadual, Municipal, FGTS/CRF, "
    "Trabalhista/CNDT) -> Indique a referência. Há alguma menção a declarações específicas (menor de idade, "
    "trabalho escravo, etc.)?\n\n"
    "   E) DECLARAÇÕES OBRIGATÓRIAS (ATENÇÃO CRÍTICA)\n"
    "   Liste todas as declarações que a empresa deve emitir, assinar e enviar. Verifique especificamente se "
    "o edital exige:\n"
    "   1. Declaração de não emprego de menor (Art. 7º, XXXIII da CF) -> Indique a referência;\n"
    "   2. Declaração de inexistência de fatos impeditivos/supervenientes -> Indique a referência;\n"
    "   3. Declaração de elaboração independente de proposta -> Indique a referência;\n"
    "   4. Declaração de enquadramento como ME/EPP (para benefícios) -> Indique a referência;\n"
    "   5. Declaração de cumprimento dos requisitos de habilitação -> Indique a referência;\n"
    "   6. Declaração de não-nepotismo ou ausência de servidores na empresa -> Indique a referência;\n"
    "   7. Outras declarações específicas exigidas nos anexos do edital. Informe se há modelos prontos "
    "fornecidos no edital (Ex: Anexo X) -> Indique a referência.\n\n"

    "6. EXIGÊNCIAS ADICIONAIS E GARANTIAS\n"
    "   - Exige garantia de proposta para participar? Exige garantia contratual se vencer? Qual percentual/valor?\n"
    "   - Há obrigatoriedade de vistoria técnica (visita ao local)? Permite declaração substitutiva de vistoria?\n"
    "   - Exige entrega de amostras ou catálogo técnico?\n"
    "   - Permite subcontratação? Há restrição de participação (exclusivo para ME/EPP, cooperativas, "
    "consórcios)? -> Indique a referência.\n\n"

    "7. CONDIÇÕES CONTRATUAIS E PENALIDADES\n"
    "   - Prazo de vigência do contrato e prazo/forma de execução ou entrega.\n"
    "   - Condições e prazo de pagamento.\n"
    "   - Principais penalidades previstas (multas, advertência, suspensão, declaração de inidoneidade) e "
    "situações que levam à rescisão -> Indique a referência.\n\n"

    "8. RISCOS, PEGADINHAS E OUTRAS INFORMAÇÕES RELEVANTES\n"
    "   - Há alguma cláusula incomum, ambígua ou perigosa neste edital?\n"
    "   - Registre aqui qualquer outra informação importante do edital que não se encaixe nos tópicos "
    "acima, para garantir que nada relevante fique de fora deste resumo.\n\n"
)


def resumir_edital(texto_edital, tentativas_maximas=3, log=print):
    log("Enviando texto para analize de IA")

    client = genai.Client()
    prompt = f"{PROMPT_BASE}--- TEXTO DO EDITAL ---\n{texto_edital}"

    for tentativa in range(1, tentativas_maximas + 1):
        try:
            resposta = client.models.generate_content(
                model=config.GEMINI_MODEL,
                contents=prompt,
            )
            return resposta.text
        except Exception as erro:
            mensagem_erro = str(erro)

            # Verifica se o erro é o 503 (Servidor ocupado) ou 429 (Muitos pedidos)
            if "503" in mensagem_erro or "429" in mensagem_erro:
                tempo_espera = 5 * tentativa  # Espera 5s, depois 10s, depois 15s...
                log(
                    f"⏳ Servidor do Google ocupado (Tentativa {tentativa}/{tentativas_maximas}). "
                    f"Aguardando {tempo_espera} segundos para tentar de novo..."
                )
                time.sleep(tempo_espera)

                if tentativa == tentativas_maximas:
                    return (
                        f"❌ Falha: O servidor do Google continuou ocupado após {tentativas_maximas} "
                        "tentativas. Tente rodar o script novamente em alguns minutos."
                    )
            else:
                # Se for outro tipo de erro (ex: internet caiu, erro de código), ele mostra na tela
                raise erro
