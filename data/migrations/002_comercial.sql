PRAGMA foreign_keys = ON;

BEGIN;

CREATE TABLE IF NOT EXISTS regioes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cidade TEXT,
    estado TEXT,
    observacao TEXT,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_regioes_nome
    ON regioes(nome);


CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    regiao_id INTEGER,
    observacao TEXT,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TEXT,
    FOREIGN KEY (regiao_id)
        REFERENCES regioes(id)
        ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_clientes_regiao
    ON clientes(regiao_id);

CREATE INDEX IF NOT EXISTS idx_clientes_nome
    ON clientes(nome);


CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER,
    regiao_id INTEGER,
    iniciado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finalizado_em TEXT,
    status TEXT NOT NULL DEFAULT 'aberto',
    observacao TEXT,
    FOREIGN KEY (cliente_id)
        REFERENCES clientes(id)
        ON DELETE SET NULL,
    FOREIGN KEY (regiao_id)
        REFERENCES regioes(id)
        ON DELETE SET NULL,
    CHECK (
        status IN (
            'aberto',
            'finalizado',
            'cancelado'
        )
    )
);

CREATE INDEX IF NOT EXISTS idx_pedidos_cliente
    ON pedidos(cliente_id);

CREATE INDEX IF NOT EXISTS idx_pedidos_regiao
    ON pedidos(regiao_id);

CREATE INDEX IF NOT EXISTS idx_pedidos_iniciado
    ON pedidos(iniciado_em);

CREATE INDEX IF NOT EXISTS idx_pedidos_status
    ON pedidos(status);


CREATE TABLE IF NOT EXISTS pedido_itens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER NOT NULL,
    produto_id INTEGER,
    codigo_informado TEXT NOT NULL,
    quantidade_solicitada INTEGER NOT NULL DEFAULT 1,
    encontrado INTEGER NOT NULL DEFAULT 0,
    localizado_em TEXT,
    observacao TEXT,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (pedido_id)
        REFERENCES pedidos(id)
        ON DELETE CASCADE,

    FOREIGN KEY (produto_id)
        REFERENCES produtos(id)
        ON DELETE SET NULL,

    CHECK (quantidade_solicitada > 0),
    CHECK (encontrado IN (0, 1))
);

CREATE INDEX IF NOT EXISTS idx_pedido_itens_pedido
    ON pedido_itens(pedido_id);

CREATE INDEX IF NOT EXISTS idx_pedido_itens_produto
    ON pedido_itens(produto_id);

CREATE INDEX IF NOT EXISTS idx_pedido_itens_codigo
    ON pedido_itens(codigo_informado);


CREATE TABLE IF NOT EXISTS eventos_atendimento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER NOT NULL,
    tipo TEXT NOT NULL,
    codigo_informado TEXT,
    produto_id INTEGER,
    dados_json TEXT,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (pedido_id)
        REFERENCES pedidos(id)
        ON DELETE CASCADE,

    FOREIGN KEY (produto_id)
        REFERENCES produtos(id)
        ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_eventos_pedido
    ON eventos_atendimento(pedido_id);

CREATE INDEX IF NOT EXISTS idx_eventos_tipo
    ON eventos_atendimento(tipo);

CREATE INDEX IF NOT EXISTS idx_eventos_codigo
    ON eventos_atendimento(codigo_informado);

CREATE INDEX IF NOT EXISTS idx_eventos_criado
    ON eventos_atendimento(criado_em);


CREATE TABLE IF NOT EXISTS produto_status_historico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    inicio_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fim_em TEXT,
    motivo TEXT,
    observacao TEXT,

    FOREIGN KEY (produto_id)
        REFERENCES produtos(id)
        ON DELETE CASCADE,

    CHECK (
        status IN (
            'ativo',
            'novidade',
            'descontinuado',
            'fora_de_linha',
            'temporariamente_indisponivel'
        )
    )
);

CREATE INDEX IF NOT EXISTS idx_produto_status_produto
    ON produto_status_historico(produto_id);

CREATE INDEX IF NOT EXISTS idx_produto_status_status
    ON produto_status_historico(status);

CREATE INDEX IF NOT EXISTS idx_produto_status_periodo
    ON produto_status_historico(inicio_em, fim_em);


CREATE TABLE IF NOT EXISTS produto_relacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    produto_relacionado_id INTEGER NOT NULL,
    tipo_relacao TEXT NOT NULL,
    forca REAL NOT NULL DEFAULT 0,
    ocorrencias INTEGER NOT NULL DEFAULT 0,
    ultima_ocorrencia_em TEXT,
    observacao TEXT,

    FOREIGN KEY (produto_id)
        REFERENCES produtos(id)
        ON DELETE CASCADE,

    FOREIGN KEY (produto_relacionado_id)
        REFERENCES produtos(id)
        ON DELETE CASCADE,

    CHECK (produto_id <> produto_relacionado_id),

    CHECK (
        tipo_relacao IN (
            'comprados_juntos',
            'pesquisados_juntos',
            'alternativa',
            'substituto',
            'complementar'
        )
    ),

    CHECK (forca >= 0),
    CHECK (ocorrencias >= 0)
);

CREATE INDEX IF NOT EXISTS idx_relacoes_produto
    ON produto_relacoes(produto_id);

CREATE INDEX IF NOT EXISTS idx_relacoes_relacionado
    ON produto_relacoes(produto_relacionado_id);

CREATE INDEX IF NOT EXISTS idx_relacoes_tipo
    ON produto_relacoes(tipo_relacao);

CREATE UNIQUE INDEX IF NOT EXISTS uq_produto_relacao
    ON produto_relacoes(
        produto_id,
        produto_relacionado_id,
        tipo_relacao
    );

COMMIT;
