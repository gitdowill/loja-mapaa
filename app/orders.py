from datetime import datetime, timezone

from .database import conectar
from .search import normalizar_codigo


def agora_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def criar_pedido(cliente_id=None, regiao_id=None, observacao=None):
    with conectar() as conexao:
        cursor = conexao.execute(
            """
            INSERT INTO pedidos (
                cliente_id,
                regiao_id,
                iniciado_em,
                status,
                observacao
            )
            VALUES (?, ?, ?, 'aberto', ?)
            """,
            (
                cliente_id,
                regiao_id,
                agora_iso(),
                observacao,
            ),
        )

        pedido_id = cursor.lastrowid

        conexao.execute(
            """
            INSERT INTO eventos_atendimento (
                pedido_id,
                tipo,
                dados_json
            )
            VALUES (?, 'pedido_iniciado', ?)
            """,
            (pedido_id, "{}"),
        )

        return pedido_id


def adicionar_item(pedido_id, codigo, quantidade=1):
    codigo_busca = normalizar_codigo(codigo)

    if quantidade <= 0:
        raise ValueError("A quantidade deve ser maior que zero.")

    with conectar() as conexao:
        pedido = conexao.execute(
            """
            SELECT id, status
            FROM pedidos
            WHERE id = ?
            """,
            (pedido_id,),
        ).fetchone()

        if pedido is None:
            raise ValueError("Pedido não encontrado.")

        if pedido["status"] != "aberto":
            raise ValueError("O pedido não está aberto.")

        produtos = conexao.execute(
            """
            SELECT id, codigo
            FROM produtos
            WHERE codigo_busca = ?
            ORDER BY id
            """,
            (codigo_busca,),
        ).fetchall()

        encontrado = 1 if produtos else 0
        produto_id = produtos[0]["id"] if produtos else None

        cursor = conexao.execute(
            """
            INSERT INTO pedido_itens (
                pedido_id,
                produto_id,
                codigo_informado,
                quantidade_solicitada,
                encontrado
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                pedido_id,
                produto_id,
                codigo,
                quantidade,
                encontrado,
            ),
        )

        item_id = cursor.lastrowid

        conexao.execute(
            """
            INSERT INTO eventos_atendimento (
                pedido_id,
                tipo,
                codigo_informado,
                produto_id,
                dados_json
            )
            VALUES (?, 'busca_produto', ?, ?, ?)
            """,
            (
                pedido_id,
                codigo,
                produto_id,
                "{}",
            ),
        )

        return {
            "item_id": item_id,
            "codigo": codigo,
            "codigo_busca": codigo_busca,
            "encontrado": bool(encontrado),
            "resultados": [dict(produto) for produto in produtos],
        }


def finalizar_pedido(pedido_id, observacao=None):
    with conectar() as conexao:
        pedido = conexao.execute(
            """
            SELECT id, status, iniciado_em
            FROM pedidos
            WHERE id = ?
            """,
            (pedido_id,),
        ).fetchone()

        if pedido is None:
            raise ValueError("Pedido não encontrado.")

        if pedido["status"] != "aberto":
            raise ValueError("O pedido não está aberto.")

        finalizado_em = agora_iso()

        conexao.execute(
            """
            UPDATE pedidos
            SET finalizado_em = ?,
                status = 'finalizado',
                observacao = COALESCE(?, observacao)
            WHERE id = ?
            """,
            (
                finalizado_em,
                observacao,
                pedido_id,
            ),
        )

        conexao.execute(
            """
            INSERT INTO eventos_atendimento (
                pedido_id,
                tipo,
                dados_json
            )
            VALUES (?, 'pedido_finalizado', ?)
            """,
            (pedido_id, "{}"),
        )

        return resumo_pedido(pedido_id, conexao)


def resumo_pedido(pedido_id, conexao=None):
    propria_conexao = conexao is None

    if propria_conexao:
        conexao = conectar()

    try:
        pedido = conexao.execute(
            """
            SELECT
                id,
                cliente_id,
                regiao_id,
                iniciado_em,
                finalizado_em,
                status,
                observacao
            FROM pedidos
            WHERE id = ?
            """,
            (pedido_id,),
        ).fetchone()

        if pedido is None:
            raise ValueError("Pedido não encontrado.")

        metricas = conexao.execute(
            """
            SELECT
                COUNT(*) AS itens,
                COALESCE(SUM(quantidade_solicitada), 0)
                    AS quantidade_solicitada,
                COALESCE(SUM(
                    CASE WHEN encontrado = 1
                    THEN quantidade_solicitada ELSE 0 END
                ), 0) AS quantidade_encontrada,
                COALESCE(SUM(
                    CASE WHEN encontrado = 0
                    THEN quantidade_solicitada ELSE 0 END
                ), 0) AS quantidade_nao_encontrada
            FROM pedido_itens
            WHERE pedido_id = ?
            """,
            (pedido_id,),
        ).fetchone()

        resultado = {
            **dict(pedido),
            **dict(metricas),
        }

        return resultado

    finally:
        if propria_conexao:
            conexao.close()
