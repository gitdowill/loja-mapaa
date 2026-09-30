from pathlib import Path
import sqlite3


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "loja.db"


def conectar():
    """Abre uma conexão com o banco local."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    conexao = sqlite3.connect(DB_PATH)
    conexao.row_factory = sqlite3.Row

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
