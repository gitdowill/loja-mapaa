from app.database import conectar
from app.recommendations import recomendar_para_codigo


def _limpar_estado_recomendacoes():
    with conectar() as conexao:
        conexao.execute("DELETE FROM produto_relacoes")
        conexao.execute("DELETE FROM produto_status_historico")
        conexao.commit()


def test_nao_recomenda_sem_evidencia():
    _limpar_estado_recomendacoes()

    assert recomendar_para_codigo("HO-20987") == []


def test_recomenda_relacao_com_evidencia():
    _limpar_estado_recomendacoes()

    with conectar() as conexao:
        conexao.execute(
            """
            INSERT INTO produto_relacoes (
                produto_id,
                produto_relacionado_id,
                tipo_relacao,
                forca,
                ocorrencias
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (25, 104, "comprados_juntos", 0.90, 10),
        )
        conexao.commit()

    resultados = recomendar_para_codigo("HO-20987")

    assert len(resultados) == 1
    assert resultados[0]["produto_id"] == 104
    assert resultados[0]["tipo_relacao"] == "comprados_juntos"
    assert resultados[0]["ocorrencias"] == 10
    assert resultados[0]["score"] > 0
    assert "Comprado junto" in resultados[0]["motivo"]


def test_nao_recomenda_produto_descontinuado():
    _limpar_estado_recomendacoes()

    with conectar() as conexao:
        conexao.execute(
            """
            INSERT INTO produto_relacoes (
                produto_id,
                produto_relacionado_id,
                tipo_relacao,
                forca,
                ocorrencias
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (25, 104, "comprados_juntos", 0.90, 10),
        )

        conexao.execute(
            """
            INSERT INTO produto_status_historico (
                produto_id,
                status
            )
            VALUES (?, 'descontinuado')
            """,
            (104,),
        )

        conexao.commit()

    assert recomendar_para_codigo("HO-20987") == []


def test_prioriza_maior_evidencia():
    _limpar_estado_recomendacoes()

    with conectar() as conexao:
        conexao.execute(
            """
            INSERT INTO produto_relacoes (
                produto_id,
                produto_relacionado_id,
                tipo_relacao,
                forca,
                ocorrencias
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (25, 104, "comprados_juntos", 0.90, 10),
        )

        conexao.execute(
            """
            INSERT INTO produto_relacoes (
                produto_id,
                produto_relacionado_id,
                tipo_relacao,
                forca,
                ocorrencias
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (25, 100, "pesquisados_juntos", 0.20, 2),
        )

        conexao.commit()

    resultados = recomendar_para_codigo("HO-20987")

    assert len(resultados) == 2
    assert resultados[0]["produto_id"] == 104
    assert resultados[0]["score"] > resultados[1]["score"]


def test_nao_repete_produto_ja_pesquisado_no_pedido():
    _limpar_estado_recomendacoes()

    with conectar() as conexao:
        cursor = conexao.execute(
            """
            INSERT INTO pedidos DEFAULT VALUES
            """
        )

        pedido_id = cursor.lastrowid

        conexao.execute(
            """
            INSERT INTO pedido_itens (
                pedido_id,
                codigo_informado,
                encontrado
            )
            VALUES (?, ?, 1)
            """,
            (pedido_id, "HO-21251"),
        )

        conexao.execute(
            """
            INSERT INTO produto_relacoes (
                produto_id,
                produto_relacionado_id,
                tipo_relacao,
                forca,
                ocorrencias
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (25, 104, "comprados_juntos", 0.90, 10),
        )

        conexao.commit()

    assert recomendar_para_codigo(
        "HO-20987",
        pedido_id=pedido_id,
    ) == []


def test_gatilho_complementar():
    _limpar_estado_recomendacoes()

    with conectar() as conexao:
        conexao.execute(
            """
            INSERT INTO produto_relacoes (
                produto_id, produto_relacionado_id,
                tipo_relacao, forca, ocorrencias
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (25, 104, "complementar", 0.80, 8),
        )
        conexao.commit()

    resultados = recomendar_para_codigo("HO-20987")

    assert len(resultados) == 1
    assert resultados[0]["tipo_relacao"] == "complementar"
    assert resultados[0]["ocorrencias"] == 8
    assert "complementar" in resultados[0]["motivo"]


def test_gatilho_alternativa():
    _limpar_estado_recomendacoes()

    with conectar() as conexao:
        conexao.execute(
            """
            INSERT INTO produto_relacoes (
                produto_id, produto_relacionado_id,
                tipo_relacao, forca, ocorrencias
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (25, 104, "alternativa", 0.80, 8),
        )
        conexao.commit()

    resultados = recomendar_para_codigo("HO-20987")

    assert len(resultados) == 1
    assert resultados[0]["tipo_relacao"] == "alternativa"
    assert "alternativa" in resultados[0]["motivo"]


def test_gatilho_substituto():
    _limpar_estado_recomendacoes()

    with conectar() as conexao:
        conexao.execute(
            """
            INSERT INTO produto_relacoes (
                produto_id, produto_relacionado_id,
                tipo_relacao, forca, ocorrencias
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (25, 104, "substituto", 0.80, 8),
        )
        conexao.commit()

    resultados = recomendar_para_codigo("HO-20987")

    assert len(resultados) == 1
    assert resultados[0]["tipo_relacao"] == "substituto"
    assert "substituto" in resultados[0]["motivo"]


def test_gatilho_pesquisados_juntos():
    _limpar_estado_recomendacoes()

    with conectar() as conexao:
        conexao.execute(
            """
            INSERT INTO produto_relacoes (
                produto_id, produto_relacionado_id,
                tipo_relacao, forca, ocorrencias
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (25, 104, "pesquisados_juntos", 0.80, 8),
        )
        conexao.commit()

    resultados = recomendar_para_codigo("HO-20987")

    assert len(resultados) == 1
    assert resultados[0]["tipo_relacao"] == "pesquisados_juntos"
    assert "Pesquisado junto" in resultados[0]["motivo"]


def test_comprados_juntos_tem_prioridade_sobre_pesquisados_juntos():
    _limpar_estado_recomendacoes()

    with conectar() as conexao:
        conexao.executemany(
            """
            INSERT INTO produto_relacoes (
                produto_id, produto_relacionado_id,
                tipo_relacao, forca, ocorrencias
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (25, 104, "comprados_juntos", 0.80, 8),
                (25, 100, "pesquisados_juntos", 0.80, 8),
            ],
        )
        conexao.commit()

    resultados = recomendar_para_codigo("HO-20987")

    assert len(resultados) == 2
    assert resultados[0]["tipo_relacao"] == "comprados_juntos"
    assert resultados[0]["score"] > resultados[1]["score"]


def test_evidencia_recente_supera_evidencia_antiga():
    _limpar_estado_recomendacoes()

    with conectar() as conexao:
        conexao.executemany(
            """
            INSERT INTO produto_relacoes (
                produto_id,
                produto_relacionado_id,
                tipo_relacao,
                forca,
                ocorrencias,
                ultima_ocorrencia_em
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    25,
                    104,
                    "comprados_juntos",
                    0.80,
                    8,
                    "2026-09-25T12:00:00+00:00",
                ),
                (
                    25,
                    100,
                    "comprados_juntos",
                    0.80,
                    8,
                    "2024-01-01T12:00:00+00:00",
                ),
            ],
        )
        conexao.commit()

    resultados = recomendar_para_codigo("HO-20987")

    assert len(resultados) == 2
    assert resultados[0]["produto_id"] == 104
    assert resultados[0]["score"] > resultados[1]["score"]


def test_evidencia_sem_data_recebe_peso_conservador():
    _limpar_estado_recomendacoes()

    with conectar() as conexao:
        conexao.executemany(
            """
            INSERT INTO produto_relacoes (
                produto_id,
                produto_relacionado_id,
                tipo_relacao,
                forca,
                ocorrencias,
                ultima_ocorrencia_em
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    25,
                    104,
                    "comprados_juntos",
                    0.80,
                    8,
                    "2026-09-25T12:00:00+00:00",
                ),
                (
                    25,
                    100,
                    "comprados_juntos",
                    0.80,
                    8,
                    None,
                ),
            ],
        )
        conexao.commit()

    resultados = recomendar_para_codigo("HO-20987")

    assert len(resultados) == 2
    assert resultados[0]["produto_id"] == 104
    assert resultados[0]["score"] > resultados[1]["score"]


def test_recencia_nao_cria_evidencia():
    _limpar_estado_recomendacoes()

    with conectar() as conexao:
        conexao.execute(
            """
            INSERT INTO produto_relacoes (
                produto_id,
                produto_relacionado_id,
                tipo_relacao,
                forca,
                ocorrencias,
                ultima_ocorrencia_em
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                25,
                104,
                "comprados_juntos",
                0,
                0,
                "2026-09-25T12:00:00+00:00",
            ),
        )
        conexao.commit()

    assert recomendar_para_codigo("HO-20987") == []


def test_contexto_do_atendimento_exclui_item_ja_pesquisado():
    """
    A evidência histórica continua existindo, mas um produto que
    já apareceu no atendimento não deve ser recomendado novamente.

    Evidência:
        produto 25 -> produto 104, comprado junto.

    Gatilho:
        comprados_juntos.

    Decisão contextual:
        produto 104 já foi pesquisado neste pedido -> não recomendar.
    """
    _limpar_estado_recomendacoes()

    with conectar() as conexao:
        pedido = conexao.execute(
            """
            INSERT INTO pedidos DEFAULT VALUES
            """
        )
        pedido_id = pedido.lastrowid

        conexao.execute(
            """
            INSERT INTO pedido_itens (
                pedido_id,
                codigo_informado,
                encontrado
            )
            VALUES (?, ?, 1)
            """,
            (pedido_id, "HO-21251"),
        )

        conexao.execute(
            """
            INSERT INTO produto_relacoes (
                produto_id,
                produto_relacionado_id,
                tipo_relacao,
                forca,
                ocorrencias
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (25, 104, "comprados_juntos", 0.90, 10),
        )

        conexao.commit()

    resultados = recomendar_para_codigo(
        "HO-20987",
        pedido_id=pedido_id,
    )

    assert resultados == []


def test_contexto_nao_apaga_evidencia_historica():
    """
    Excluir uma recomendação por contexto não deve apagar a relação
    histórica que fundamentaria essa recomendação em outro atendimento.
    """
    _limpar_estado_recomendacoes()

    with conectar() as conexao:
        pedido = conexao.execute(
            """
            INSERT INTO pedidos DEFAULT VALUES
            """
        )
        pedido_id = pedido.lastrowid

        conexao.execute(
            """
            INSERT INTO pedido_itens (
                pedido_id,
                codigo_informado,
                encontrado
            )
            VALUES (?, ?, 1)
            """,
            (pedido_id, "HO-21251"),
        )

        conexao.execute(
            """
            INSERT INTO produto_relacoes (
                produto_id,
                produto_relacionado_id,
                tipo_relacao,
                forca,
                ocorrencias
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (25, 104, "comprados_juntos", 0.90, 10),
        )

        conexao.commit()

    # Neste atendimento o contexto bloqueia a sugestão.
    assert recomendar_para_codigo(
        "HO-20987",
        pedido_id=pedido_id,
    ) == []

    # Em outro atendimento, a mesma evidência continua válida.
    outro_pedido = None

    with conectar() as conexao:
        cursor = conexao.execute(
            """
            INSERT INTO pedidos DEFAULT VALUES
            """
        )
        outro_pedido = cursor.lastrowid

    resultados = recomendar_para_codigo(
        "HO-20987",
        pedido_id=outro_pedido,
    )

    assert len(resultados) == 1
    assert resultados[0]["produto_id"] == 104
    assert resultados[0]["tipo_relacao"] == "comprados_juntos"


def test_produto_indisponivel_pode_ser_substituido_por_alternativa_evidenciada():
    """
    Se o produto relacionado está indisponível, ele não deve ser
    recomendado diretamente.

    Uma alternativa explicitamente registrada na base, porém,
    continua elegível.
    """
    _limpar_estado_recomendacoes()

    with conectar() as conexao:
        # 104: relação forte, mas produto indisponível.
        conexao.execute(
            """
            INSERT INTO produto_relacoes (
                produto_id,
                produto_relacionado_id,
                tipo_relacao,
                forca,
                ocorrencias
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (25, 104, "comprados_juntos", 0.90, 10),
        )

        conexao.execute(
            """
            INSERT INTO produto_status_historico (
                produto_id,
                status
            )
            VALUES (?, 'descontinuado')
            """,
            (104,),
        )

        # 100: alternativa explicitamente registrada.
        conexao.execute(
            """
            INSERT INTO produto_relacoes (
                produto_id,
                produto_relacionado_id,
                tipo_relacao,
                forca,
                ocorrencias
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (25, 100, "alternativa", 0.70, 6),
        )

        conexao.commit()

    resultados = recomendar_para_codigo("HO-20987")

    assert len(resultados) == 1
    assert resultados[0]["produto_id"] == 100
    assert resultados[0]["tipo_relacao"] == "alternativa"


def test_indisponibilidade_nao_inventa_alternativa():
    """
    Se o produto relacionado está indisponível e não existe uma
    alternativa/substituto registrada, o motor não deve inventar uma.
    """
    _limpar_estado_recomendacoes()

    with conectar() as conexao:
        conexao.execute(
            """
            INSERT INTO produto_relacoes (
                produto_id,
                produto_relacionado_id,
                tipo_relacao,
                forca,
                ocorrencias
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (25, 104, "comprados_juntos", 0.90, 10),
        )

        conexao.execute(
            """
            INSERT INTO produto_status_historico (
                produto_id,
                status
            )
            VALUES (?, 'descontinuado')
            """,
            (104,),
        )

        conexao.commit()

    resultados = recomendar_para_codigo("HO-20987")

    assert resultados == []


def test_contexto_do_atendimento_preserva_gatilho_sem_tomar_decisao():
    _limpar_estado_recomendacoes()

    with conectar() as conexao:
        pedido = conexao.execute(
            """
            INSERT INTO pedidos DEFAULT VALUES
            """
        ).lastrowid

        conexao.execute(
            """
            INSERT INTO pedido_itens (
                pedido_id,
                codigo_informado,
                encontrado
            )
            VALUES (?, ?, 1)
            """,
            (pedido, "HO-20987"),
        )

        conexao.execute(
            """
            INSERT INTO produto_relacoes (
                produto_id,
                produto_relacionado_id,
                tipo_relacao,
                forca,
                ocorrencias
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (25, 104, "complementar", 0.90, 12),
        )

        conexao.commit()

    resultados = recomendar_para_codigo(
        "HO-20987",
        pedido_id=pedido,
    )

    assert len(resultados) == 1

    sugestao = resultados[0]

    # A evidência continua explícita.
    assert sugestao["produto_id"] == 104
    assert sugestao["tipo_relacao"] == "complementar"
    assert sugestao["forca"] == 0.90
    assert sugestao["ocorrencias"] == 12

    # O gatilho explica por que apareceu.
    assert "complementar" in sugestao["motivo"].lower()

    # A recomendação não representa uma decisão comercial.
    assert "decisao" not in sugestao
    assert "acao" not in sugestao

    # O motor não deve alterar o pedido apenas por recomendar.
    with conectar() as conexao:
        item = conexao.execute(
            """
            SELECT codigo_informado, encontrado
            FROM pedido_itens
            WHERE pedido_id = ?
            ORDER BY id
            """,
            (pedido,),
        ).fetchall()

    assert len(item) == 1
    assert item[0]["codigo_informado"] == "HO-20987"
    assert item[0]["encontrado"] == 1


def test_contexto_acumulado_filtra_gatilho_ja_apresentado():
    _limpar_estado_recomendacoes()

    with conectar() as conexao:
        pedido = conexao.execute(
            """
            INSERT INTO pedidos DEFAULT VALUES
            """
        ).lastrowid

        # Produto que iniciou o contexto do atendimento.
        conexao.execute(
            """
            INSERT INTO pedido_itens (
                pedido_id,
                codigo_informado,
                encontrado
            )
            VALUES (?, ?, 1)
            """,
            (pedido, "HO-20987"),
        )

        # Gatilho complementar já pesquisado/apresentado.
        conexao.execute(
            """
            INSERT INTO pedido_itens (
                pedido_id,
                codigo_informado,
                encontrado
            )
            VALUES (?, ?, 1)
            """,
            (pedido, "HO-21251"),
        )

        # Evidência para o produto já presente no contexto.
        conexao.execute(
            """
            INSERT INTO produto_relacoes (
                produto_id,
                produto_relacionado_id,
                tipo_relacao,
                forca,
                ocorrencias
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (25, 104, "complementar", 0.90, 12),
        )

        # Outra oportunidade ainda não apresentada.
        conexao.execute(
            """
            INSERT INTO produto_relacoes (
                produto_id,
                produto_relacionado_id,
                tipo_relacao,
                forca,
                ocorrencias
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (25, 1, "alternativa", 0.70, 8),
        )

        conexao.commit()

    resultados = recomendar_para_codigo(
        "HO-20987",
        pedido_id=pedido,
    )

    # O gatilho já presente no atendimento não deve ser repetido.
    assert all(
        resultado["produto_id"] != 104
        for resultado in resultados
    )

    # A outra oportunidade continua disponível.
    assert len(resultados) == 1
    assert resultados[0]["produto_id"] == 1
    assert resultados[0]["tipo_relacao"] == "alternativa"

    # O motor apenas sugere; não toma decisão comercial.
    assert "decisao" not in resultados[0]
    assert "acao" not in resultados[0]

    # O estado do atendimento permanece intacto.
    with conectar() as conexao:
        itens = conexao.execute(
            """
            SELECT codigo_informado, encontrado
            FROM pedido_itens
            WHERE pedido_id = ?
            ORDER BY id
            """,
            (pedido,),
        ).fetchall()

    assert len(itens) == 2
    assert [item["codigo_informado"] for item in itens] == [
        "HO-20987",
        "HO-21251",
    ]

import pytest

from app.recommendations import registrar_resposta_recomendacao


@pytest.mark.parametrize("resposta", ["aceita", "recusada", "ignorada"])
def test_resposta_comercial_nao_altera_evidencia_historica(resposta):
    """
    Uma resposta comercial pertence ao contexto do atendimento.

    Ela não pode alterar a evidência histórica registrada em
    produto_relacoes.
    """
    _limpar_estado_recomendacoes()

    with conectar() as conexao:
        pedido_id = conexao.execute(
            """
            INSERT INTO pedidos DEFAULT VALUES
            """
        ).lastrowid

        conexao.execute(
            """
            INSERT INTO pedido_itens (
                pedido_id,
                codigo_informado,
                encontrado
            )
            VALUES (?, ?, 1)
            """,
            (pedido_id, "HO-20987"),
        )

        conexao.execute(
            """
            INSERT INTO produto_relacoes (
                produto_id,
                produto_relacionado_id,
                tipo_relacao,
                forca,
                ocorrencias
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (25, 104, "comprados_juntos", 0.90, 10),
        )

        conexao.commit()

        antes = conexao.execute(
            """
            SELECT
                produto_id,
                produto_relacionado_id,
                tipo_relacao,
                forca,
                ocorrencias
            FROM produto_relacoes
            WHERE produto_id = ?
              AND produto_relacionado_id = ?
            """,
            (25, 104),
        ).fetchone()

    registrar_resposta_recomendacao(
        pedido_id=pedido_id,
        produto_id=104,
        resposta=resposta,
    )

    with conectar() as conexao:
        depois = conexao.execute(
            """
            SELECT
                produto_id,
                produto_relacionado_id,
                tipo_relacao,
                forca,
                ocorrencias
            FROM produto_relacoes
            WHERE produto_id = ?
              AND produto_relacionado_id = ?
            """,
            (25, 104),
        ).fetchone()

        quantidade_relacoes = conexao.execute(
            """
            SELECT COUNT(*)
            FROM produto_relacoes
            WHERE produto_id = ?
              AND produto_relacionado_id = ?
            """,
            (25, 104),
        ).fetchone()[0]

    assert dict(depois) == dict(antes)
    assert quantidade_relacoes == 1
    assert depois["forca"] == 0.90
    assert depois["ocorrencias"] == 10


@pytest.mark.parametrize("resposta", ["aceita", "recusada", "ignorada"])
def test_resposta_comercial_e_registrada_no_contexto_do_atendimento(resposta):
    _limpar_estado_recomendacoes()

    with conectar() as conexao:
        pedido_id = conexao.execute(
            """
            INSERT INTO pedidos DEFAULT VALUES
            """
        ).lastrowid

        conexao.commit()

    registrar_resposta_recomendacao(
        pedido_id=pedido_id,
        produto_id=104,
        resposta=resposta,
    )

    with conectar() as conexao:
        evento = conexao.execute(
            """
            SELECT
                pedido_id,
                tipo,
                produto_id,
                dados_json
            FROM eventos_atendimento
            WHERE pedido_id = ?
              AND tipo = 'resposta_recomendacao'
            ORDER BY id DESC
            LIMIT 1
            """,
            (pedido_id,),
        ).fetchone()

    assert evento is not None
    assert evento["pedido_id"] == pedido_id
    assert evento["tipo"] == "resposta_recomendacao"
    assert evento["produto_id"] == 104

    import json

    dados = json.loads(evento["dados_json"])
    assert dados["resposta"] == resposta


def test_resposta_comercial_nao_duplica_evidencia_historica():
    _limpar_estado_recomendacoes()

    with conectar() as conexao:
        pedido_id = conexao.execute(
            """
            INSERT INTO pedidos DEFAULT VALUES
            """
        ).lastrowid

        conexao.execute(
            """
            INSERT INTO produto_relacoes (
                produto_id,
                produto_relacionado_id,
                tipo_relacao,
                forca,
                ocorrencias
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (25, 104, "comprados_juntos", 0.90, 10),
        )

        conexao.commit()

    registrar_resposta_recomendacao(
        pedido_id=pedido_id,
        produto_id=104,
        resposta="aceita",
    )

    registrar_resposta_recomendacao(
        pedido_id=pedido_id,
        produto_id=104,
        resposta="aceita",
    )

    with conectar() as conexao:
        relacao = conexao.execute(
            """
            SELECT forca, ocorrencias
            FROM produto_relacoes
            WHERE produto_id = ?
              AND produto_relacionado_id = ?
            """,
            (25, 104),
        ).fetchone()

        eventos = conexao.execute(
            """
            SELECT COUNT(*)
            FROM eventos_atendimento
            WHERE pedido_id = ?
              AND tipo = 'resposta_recomendacao'
              AND produto_id = ?
            """,
            (pedido_id, 104),
        ).fetchone()[0]

    # A evidência histórica continua exatamente igual.
    assert relacao["forca"] == 0.90
    assert relacao["ocorrencias"] == 10

    # Cada resposta registrada continua sendo um evento de atendimento.
    assert eventos == 2


def test_recomendacao_nao_registra_resposta_comercial_automaticamente():
    _limpar_estado_recomendacoes()

    with conectar() as conexao:
        pedido_id = conexao.execute(
            """
            INSERT INTO pedidos DEFAULT VALUES
            """
        ).lastrowid

        conexao.execute(
            """
            INSERT INTO pedido_itens (
                pedido_id,
                codigo_informado,
                encontrado
            )
            VALUES (?, ?, 1)
            """,
            (pedido_id, "HO-20987"),
        )

        conexao.execute(
            """
            INSERT INTO produto_relacoes (
                produto_id,
                produto_relacionado_id,
                tipo_relacao,
                forca,
                ocorrencias
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (25, 104, "comprados_juntos", 0.90, 10),
        )

        conexao.commit()

    resultados = recomendar_para_codigo(
        "HO-20987",
        pedido_id=pedido_id,
    )

    assert len(resultados) == 1
    assert resultados[0]["produto_id"] == 104

    with conectar() as conexao:
        eventos = conexao.execute(
            """
            SELECT COUNT(*)
            FROM eventos_atendimento
            WHERE pedido_id = ?
              AND tipo = 'resposta_recomendacao'
              AND produto_id = ?
            """,
            (pedido_id, 104),
        ).fetchone()[0]

    # Gerar a sugestão não equivale a uma decisão comercial.
    assert eventos == 0

def test_resposta_comercial_de_um_atendimento_nao_contamina_outro():
    _limpar_estado_recomendacoes()

    with conectar() as conexao:
        pedido_a = conexao.execute(
            """
            INSERT INTO pedidos DEFAULT VALUES
            """
        ).lastrowid

        pedido_b = conexao.execute(
            """
            INSERT INTO pedidos DEFAULT VALUES
            """
        ).lastrowid

        conexao.execute(
            """
            INSERT INTO pedido_itens (
                pedido_id,
                codigo_informado,
                encontrado
            )
            VALUES (?, ?, 1)
            """,
            (pedido_a, "HO-20987"),
        )

        conexao.execute(
            """
            INSERT INTO pedido_itens (
                pedido_id,
                codigo_informado,
                encontrado
            )
            VALUES (?, ?, 1)
            """,
            (pedido_b, "HO-20987"),
        )

        conexao.execute(
            """
            INSERT INTO produto_relacoes (
                produto_id,
                produto_relacionado_id,
                tipo_relacao,
                forca,
                ocorrencias
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (25, 104, "comprados_juntos", 0.90, 10),
        )

        conexao.commit()

    # Atendimento A recebe a recomendação e o cliente recusa.
    resultados_a = recomendar_para_codigo(
        "HO-20987",
        pedido_id=pedido_a,
    )

    assert len(resultados_a) == 1
    assert resultados_a[0]["produto_id"] == 104

    registrar_resposta_recomendacao(
        pedido_id=pedido_a,
        produto_id=104,
        resposta="recusada",
    )

    # A decisão do atendimento A não deve alterar a evidência.
    with conectar() as conexao:
        relacao = conexao.execute(
            """
            SELECT
                produto_id,
                produto_relacionado_id,
                tipo_relacao,
                forca,
                ocorrencias
            FROM produto_relacoes
            WHERE produto_id = ?
              AND produto_relacionado_id = ?
            """,
            (25, 104),
        ).fetchone()

    assert relacao["produto_id"] == 25
    assert relacao["produto_relacionado_id"] == 104
    assert relacao["tipo_relacao"] == "comprados_juntos"
    assert relacao["forca"] == 0.90
    assert relacao["ocorrencias"] == 10

    # Atendimento B começa independente do atendimento A.
    resultados_b = recomendar_para_codigo(
        "HO-20987",
        pedido_id=pedido_b,
    )

    assert len(resultados_b) == 1
    assert resultados_b[0]["produto_id"] == 104
    assert resultados_b[0]["tipo_relacao"] == "comprados_juntos"

    # A recusa pertence somente ao atendimento A.
    with conectar() as conexao:
        respostas_a = conexao.execute(
            """
            SELECT COUNT(*)
            FROM eventos_atendimento
            WHERE pedido_id = ?
              AND tipo = 'resposta_recomendacao'
              AND produto_id = ?
            """,
            (pedido_a, 104),
        ).fetchone()[0]

        respostas_b = conexao.execute(
            """
            SELECT COUNT(*)
            FROM eventos_atendimento
            WHERE pedido_id = ?
              AND tipo = 'resposta_recomendacao'
              AND produto_id = ?
            """,
            (pedido_b, 104),
        ).fetchone()[0]

    assert respostas_a == 1
    assert respostas_b == 0
