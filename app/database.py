from pathlib import Path
import os
import sqlite3


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "loja.db"


def obter_db_path() -> Path:
    """
    Retorna o banco configurado.

    Normalmente usa data/loja.db.
    Testes podem definir LOJA_DB_PATH para usar uma
    cópia isolada sem alterar o banco real.
    """
    caminho = os.environ.get("LOJA_DB_PATH")

    if caminho:
        return Path(caminho).expanduser().resolve()

    return DB_PATH


def conectar():
    """Abre uma conexão com o banco local."""
    caminho = obter_db_path()

    caminho.parent.mkdir(parents=True, exist_ok=True)

    conexao = sqlite3.connect(caminho)
    conexao.row_factory = sqlite3.Row

    conexao.execute("PRAGMA foreign_keys = ON")

    return conexao


def criar_banco():
    """Cria a estrutura inicial do banco."""
    with conectar() as conexao:
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT NOT NULL,
                codigo_busca TEXT NOT NULL,
                zona TEXT NOT NULL,
                localizacao TEXT,
                tipo TEXT,
                material TEXT,
                cores TEXT,
                quantidade INTEGER DEFAULT 1,
                observacao TEXT
            )
            """
        )

        conexao.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_produtos_codigo_busca
            ON produtos(codigo_busca)
            """
        )

        conexao.commit()
