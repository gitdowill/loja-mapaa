from __future__ import annotations

from datetime import datetime, timezone

from .database import conectar


STATUS_INDISPONIVEIS = {
    "descontinuado",
    "fora_de_linha",
    "temporariamente_indisponivel",
}

TIPOS_PRIORIDADE = {
    "comprados_juntos": 1.00,
    "complementar": 0.90,
    "alternativa": 0.85,
    "substituto": 0.85,
    "pesquisados_juntos": 0.70,
}


def _agora():
    return datetime.now(timezone.utc)


def _recencia(ultima_ocorrencia_em):
    """
    Retorna um fator entre 0 e 1.
    Relações recentes recebem maior peso.
    """
    if not ultima_ocorrencia_em:
        return 0.5

    try:
        data = datetime.fromisoformat(
            ultima_ocorrencia_em.replace("Z", "+00:00")
        )

        if data.tzinfo is None:
            data = data.replace(tzinfo=timezone.utc)

        dias = max((_agora() - data).days, 0)

        if dias <= 30:
            return 1.00
        if dias <= 90:
            return 0.90
        if dias <= 180:
            return 0.75
        if dias <= 365:
            return 0.55

        return 0.35

    except (ValueError, TypeError):
        return 0.5


def _status_atual(conexao, produto_id):
    """
    Consulta o último status registrado do produto.
    Produto sem histórico de status é tratado como ativo.
    """
    row = conexao.execute(
        """
        SELECT status
        FROM produto_status_historico
        WHERE produto_id = ?
          AND inicio_em <= CURRENT_TIMESTAMP
          AND (fim_em IS NULL OR fim_em > CURRENT_TIMESTAMP)
        ORDER BY inicio_em DESC, id DESC
        LIMIT 1
        """,
        (produto_id,),
    ).fetchone()

    if row is None:
        return "ativo"

    return row["status"]


def _evidencia_suficiente(relacao):
    """
    Relação precisa possuir evidência histórica real.
    """
    ocorrencias = relacao["ocorrencias"] or 0
    forca = relacao["forca"] or 0

    return ocorrencias > 0 and forca > 0


def recomendar_para_codigo(
    codigo: str,
    limite: int = 5,
    pedido_id: int | None = None,
):
    """
    Gera recomendações baseadas exclusivamente em evidências registradas.

    Não cria relações novas.
    Não recomenda produtos indisponíveis.
    """

    codigo_busca = (
        codigo.strip()
        .upper()
        .replace("-", "")
        .replace(" ", "")
    )

    if limite <= 0:
        return []

    with conectar() as conexao:
        produtos_base = conexao.execute(
            """
            SELECT id, codigo, codigo_busca
            FROM produtos
            WHERE codigo_busca = ?
            ORDER BY id
            """,
            (codigo_busca,),
        ).fetchall()

        if not produtos_base:
            return []

        ids_base = [produto["id"] for produto in produtos_base]

        placeholders = ",".join("?" for _ in ids_base)

        relacoes = conexao.execute(
            f"""
            SELECT
                pr.id,
                pr.produto_id,
                pr.produto_relacionado_id,
                pr.tipo_relacao,
                pr.forca,
                pr.ocorrencias,
                pr.ultima_ocorrencia_em,

                p.codigo,
                p.codigo_busca,
                p.zona,
                p.localizacao,
                p.tipo,
                p.material,
                p.cores,
                p.quantidade,
                p.observacao

            FROM produto_relacoes pr

            JOIN produtos p
              ON p.id = pr.produto_relacionado_id

            WHERE pr.produto_id IN ({placeholders})
            ORDER BY pr.forca DESC, pr.ocorrencias DESC
            """,
            ids_base,
        ).fetchall()

        recomendacoes = []

        # Evita sugerir duas vezes o mesmo produto.
        vistos = set()

        # Se o pedido já possui itens, evitamos recomendar
        # produtos que já foram pesquisados naquele atendimento.
        itens_pedido = set()

        if pedido_id is not None:
            itens = conexao.execute(
                """
                SELECT codigo_informado
                FROM pedido_itens
                WHERE pedido_id = ?
                """,
                (pedido_id,),
            ).fetchall()

            itens_pedido = {
                item["codigo_informado"]
                .strip()
                .upper()
                .replace("-", "")
                .replace(" ", "")
                for item in itens
            }

        for relacao in relacoes:
            if not _evidencia_suficiente(relacao):
                continue

            produto_id = relacao["produto_relacionado_id"]

            if produto_id in vistos:
                continue

            codigo_destino = relacao["codigo_busca"]

            if codigo_destino in itens_pedido:
                continue

            status = _status_atual(conexao, produto_id)

            if status in STATUS_INDISPONIVEIS:
                continue

            prioridade_tipo = TIPOS_PRIORIDADE.get(
                relacao["tipo_relacao"],
                0.50,
            )

            recencia = _recencia(
                relacao["ultima_ocorrencia_em"]
            )

            forca = max(float(relacao["forca"] or 0), 0.0)
            ocorrencias = int(relacao["ocorrencias"] or 0)

            # A força histórica é o principal componente.
            # A recência ajusta a força.
            score = (
                forca
                * prioridade_tipo
                * recencia
            )

            # Novidade recebe pequeno bônus,
            # mas nunca supera a ausência de evidência.
            if status == "novidade":
                score *= 1.10

            if score <= 0:
                continue

            if relacao["tipo_relacao"] == "comprados_juntos":
                motivo = (
                    f"Comprado junto em {ocorrencias} "
                    f"atendimento(s)."
                )
            elif relacao["tipo_relacao"] == "pesquisados_juntos":
                motivo = (
                    f"Pesquisado junto em {ocorrencias} "
                    f"atendimento(s)."
                )
            elif relacao["tipo_relacao"] == "alternativa":
                motivo = (
                    f"Registrado como alternativa em "
                    f"{ocorrencias} ocorrência(s)."
                )
            elif relacao["tipo_relacao"] == "substituto":
                motivo = (
                    f"Registrado como substituto em "
                    f"{ocorrencias} ocorrência(s)."
                )
            else:
                motivo = (
                    f"Registrado como complementar em "
                    f"{ocorrencias} ocorrência(s)."
                )

            if status == "novidade":
                motivo += " Produto marcado como novidade."

            recomendacoes.append(
                {
                    "produto_id": produto_id,
                    "codigo": relacao["codigo"],
                    "zona": relacao["zona"],
                    "localizacao": relacao["localizacao"],
                    "tipo": relacao["tipo"],
                    "material": relacao["material"],
                    "cores": relacao["cores"],
                    "quantidade": relacao["quantidade"],
                    "status": status,
                    "tipo_relacao": relacao["tipo_relacao"],
                    "forca": forca,
                    "ocorrencias": ocorrencias,
                    "ultima_ocorrencia_em": (
                        relacao["ultima_ocorrencia_em"]
                    ),
                    "score": round(score, 6),
                    "motivo": motivo,
                }
            )

            vistos.add(produto_id)

        recomendacoes.sort(
            key=lambda item: (
                -item["score"],
                -item["ocorrencias"],
                item["codigo"],
            )
        )

        return recomendacoes[:limite]


def registrar_resposta_recomendacao(
    pedido_id: int,
    produto_id: int,
    resposta: str,
):
    """
    Registra a resposta comercial a uma recomendação.

    Este evento pertence ao contexto do atendimento e não altera
    a evidência histórica armazenada em produto_relacoes.
    """
    respostas_validas = {"aceita", "recusada", "ignorada"}

    if resposta not in respostas_validas:
        raise ValueError(
            f"Resposta inválida: {resposta!r}. "
            f"Use: {', '.join(sorted(respostas_validas))}."
        )

    import json

    with conectar() as conexao:
        conexao.execute(
            """
            INSERT INTO eventos_atendimento (
                pedido_id,
                tipo,
                produto_id,
                dados_json
            )
            VALUES (?, 'resposta_recomendacao', ?, ?)
            """,
            (
                pedido_id,
                produto_id,
                json.dumps(
                    {"resposta": resposta},
                    ensure_ascii=False,
                ),
            ),
        )

        conexao.commit()
