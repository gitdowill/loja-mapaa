from app.database import conectar, criar_banco


def test_banco_e_tabela_produtos():
    criar_banco()

    with conectar() as conexao:
        tabela = conexao.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name = 'produtos'
            """
        ).fetchone()

    assert tabela is not None
    assert tabela["name"] == "produtos"
