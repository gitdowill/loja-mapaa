from .database import conectar


def normalizar_codigo(codigo: str) -> str:
    """Remove espaços e hífens e normaliza para maiúsculas."""
    return codigo.strip().upper().replace("-", "").replace(" ", "")


def buscar_por_codigo(codigo: str):
    """Retorna todas as localizações associadas ao código."""
    codigo_busca = normalizar_codigo(codigo)

    with conectar() as conexao:
        cursor = conexao.execute(
            """
            SELECT
                id,
                codigo,
                zona,
                localizacao,
                tipo,
                material,
                cores,
                quantidade,
                observacao
            FROM produtos
            WHERE codigo_busca = ?
            ORDER BY id
            """,
            (codigo_busca,),
        )

        return [dict(row) for row in cursor.fetchall()]
