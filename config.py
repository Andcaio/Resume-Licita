import os
from pathlib import Path

from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent / ".env"
GEMINI_MODEL = "gemini-3.5-flash"

load_dotenv(ENV_PATH)


def get_api_key():
    return os.environ.get("GEMINI_API_KEY")


def save_api_key(chave):
    """Salva a chave da API no arquivo .env e a disponibiliza imediatamente na sessão atual."""
    chave = chave.strip()

    linhas = []
    if ENV_PATH.exists():
        linhas = ENV_PATH.read_text(encoding="utf-8").splitlines()
    linhas = [linha for linha in linhas if not linha.startswith("GEMINI_API_KEY=")]
    linhas.append(f"GEMINI_API_KEY={chave}")

    ENV_PATH.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    os.environ["GEMINI_API_KEY"] = chave
