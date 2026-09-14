# Analisador de Editais de Licitação

Ferramenta em Python que lê editais de licitação em PDF e gera um resumo estruturado usando a IA do Google Gemini.

O resumo é escrito na ótica de um advogado especialista em licitações públicas brasileiras e cobre identificação do certame, objeto, valor, cronograma, requisitos de habilitação, declarações obrigatórias, garantias, condições contratuais e riscos — sempre com a referência ao item/cláusula de origem no documento.

## Funcionalidades

- Lê e concatena vários PDFs de uma mesma licitação (edital, termo de referência, anexos) em uma única análise.
- Gera um resumo em texto puro, pronto para ser lido em qualquer editor, com rastreabilidade (`[Ref: Item 8.1.2]`) para cada informação extraída.
- Interface gráfica (Tkinter) com seleção de arquivos, log de andamento e configuração da chave da API.
- Modo linha de comando para processar em lote a pasta `editais/`.
- Reenvio automático com espera progressiva quando a API do Google responde `503` (servidor ocupado) ou `429` (muitas requisições).
- Alerta quando os PDFs são imagens escaneadas ou têm texto insuficiente.

## Requisitos

- Python 3.9 ou superior
- Uma chave da API do Google Gemini ([Google AI Studio](https://aistudio.google.com/app/apikey))
- Windows, para o modo gráfico com `.pyw` e o botão "Abrir resultado" (`os.startfile`). O modo linha de comando funciona em qualquer sistema.

## Instalação

```bash
git clone https://github.com/Andcaio/Resume-Licita.git
cd Resume-Licita
pip install -r requirements.txt
```

## Configuração da chave da API

Escolha uma das opções:

**Pela interface gráfica** — abra o programa e clique em "Configurar chave da API...". A chave é gravada no `.env` automaticamente.

**Manualmente** — copie `.env.example` para `.env` e preencha:

```
GEMINI_API_KEY=sua_chave_aqui
```

O arquivo `.env` está no `.gitignore` e não é enviado ao repositório.

## Uso

### Interface gráfica

```bash
python app.pyw
```

No Windows, basta dar duplo clique em `app.pyw` (abre sem janela de console).

1. Clique em "Adicionar PDFs..." e selecione os documentos da licitação.
2. Confira se a chave da API está configurada.
3. Clique em "Iniciar Análise" e acompanhe o andamento no painel de log.
4. Ao terminar, use "Abrir resultado" para ver o resumo.

### Linha de comando

Coloque os PDFs na pasta `editais/` e execute:

```bash
python analisador.py
```

Em ambos os modos o resumo é salvo em `resumo/resumo_final.txt`.

## Estrutura do projeto

| Arquivo | Função |
| --- | --- |
| `app.pyw` | Interface gráfica Tkinter; roda a análise em thread separada para não travar a janela |
| `analisador.py` | Execução em linha de comando sobre a pasta `editais/` |
| `leitor_pdf.py` | Extração e concatenação do texto dos PDFs (pypdf) |
| `analisador_ia.py` | Prompt de análise e chamada à API Gemini, com retentativas |
| `config.py` | Leitura e gravação da chave da API no `.env`; modelo Gemini usado |
| `editais/` | Pasta de entrada dos PDFs (modo linha de comando) |
| `resumo/` | Pasta de saída do resumo gerado |

O modelo usado é definido em `GEMINI_MODEL`, em [config.py](config.py) — altere ali se quiser outro modelo.

## Limitações

- PDFs escaneados (imagem) não são reconhecidos: o programa avisa quando o texto extraído é curto demais. É preciso passar o documento por OCR antes.
- Editais muito extensos podem esbarrar no limite de contexto do modelo.
- O resumo é gerado por IA e serve como apoio à leitura — não substitui a conferência do edital original antes de participar do certame.
