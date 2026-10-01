from app.database import conectar
from app.orders import (
    adicionar_item,
    criar_pedido,
    finalizar_pedido,
    resumo_pedido,
)


def test_criar_pedido():
    pedido_id = criar_pedido()

    assert pedido_id > 0

    resumo = resumo_pedido(pedido_id)

    assert resumo["status"] == "aberto"
    assert resumo["quantidade_solicitada"] == 0


def test_pedido_registra_produto_encontrado():
    pedido_id = criar_pedido()

    resultado = adicionar_item(
        pedido_id,
        "HO-21251",
    )

    assert resultado["encontrado"] is True
    assert resultado["resultados"][0]["codigo"] == "HO-21251"

    resumo = resumo_pedido(pedido_id)

    assert resumo["quantidade_solicitada"] == 1
    assert resumo["quantidade_encontrada"] == 1
    assert resumo["quantidade_nao_encontrada"] == 0


def test_pedido_registra_produto_nao_encontrado():
    pedido_id = criar_pedido()

    resultado = adicionar_item(
        pedido_id,
        "CODIGO-QUE-NAO-EXISTE",
    )

    assert resultado["encontrado"] is False
    assert resultado["resultados"] == []

    resumo = resumo_pedido(pedido_id)

    assert resumo["quantidade_solicitada"] == 1
    assert resumo["quantidade_encontrada"] == 0
    assert resumo["quantidade_nao_encontrada"] == 1


def test_finalizar_pedido_calcula_metricas():
    pedido_id = criar_pedido()

    adicionar_item(pedido_id, "HO-21251")
    adicionar_item(pedido_id, "HO-20987", quantidade=2)
    adicionar_item(pedido_id, "NAO-EXISTE")

    resumo = finalizar_pedido(pedido_id)

    assert resumo["status"] == "finalizado"
    assert resumo["finalizado_em"] is not None
    assert resumo["quantidade_solicitada"] == 4
    assert resumo["quantidade_encontrada"] == 3
    assert resumo["quantidade_nao_encontrada"] == 1


def test_eventos_do_pedido():
    pedido_id = criar_pedido()

    adicionar_item(pedido_id, "HO-21251")
    finalizar_pedido(pedido_id)

    with conectar() as conexao:
        eventos = conexao.execute(
            """
            SELECT tipo
            FROM eventos_atendimento
            WHERE pedido_id = ?
            ORDER BY id
            """,
            (pedido_id,),
        ).fetchall()

    tipos = [evento["tipo"] for evento in eventos]

    assert tipos == [
        "pedido_iniciado",
        "busca_produto",
        "pedido_finalizado",
    ]
