-- ===== SCRIPT DE MIGRAÇÃO MYSQL PARA POSTGRESQL =====
-- Execute este script no seu banco PostgreSQL no Render

-- Configurar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ===== TABELA USUARIOS =====
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    cargo VARCHAR(50),
    nivel_de_acesso INTEGER DEFAULT 1,
    foto_de_perfil BYTEA,
    status VARCHAR(20) DEFAULT 'Ativo',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===== TABELA CATEGORIA_PRODUTOS =====
CREATE TABLE IF NOT EXISTS categoria_produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===== TABELA FORNECEDORES =====
CREATE TABLE IF NOT EXISTS fornecedores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    cnpj VARCHAR(18) UNIQUE,
    telefone VARCHAR(20),
    email VARCHAR(150),
    endereco TEXT,
    cidade VARCHAR(100),
    estado VARCHAR(50),
    cep VARCHAR(10),
    contato_nome VARCHAR(100),
    contato_telefone VARCHAR(20),
    contato_email VARCHAR(150),
    website VARCHAR(200),
    categoria_produtos TEXT,
    prazo_entrega VARCHAR(50),
    condicoes_pagamento TEXT,
    observacoes TEXT,
    status VARCHAR(20) DEFAULT 'Ativo',
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===== TABELA PRODUTOS =====
CREATE TABLE IF NOT EXISTS produtos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nome VARCHAR(200) NOT NULL,
    descricao TEXT,
    especificacoes_tecnicas TEXT,
    categoria_id INTEGER REFERENCES categoria_produtos(id),
    fornecedor_id INTEGER REFERENCES fornecedores(id),
    preco DECIMAL(10,2) DEFAULT 0.00,
    custo_materiais DECIMAL(10,2) DEFAULT 0.00,
    custo_etapas DECIMAL(10,2) DEFAULT 0.00,
    margem_lucro DECIMAL(5,2) DEFAULT 0.00,
    estoque INTEGER DEFAULT 0,
    estoque_minimo INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'Ativo',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===== TABELA UNIDADES_DE_MEDIDA =====
CREATE TABLE IF NOT EXISTS unidades_de_medida (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(50) NOT NULL UNIQUE,
    is_measurement BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===== TABELA TIPO_ITENS =====
CREATE TABLE IF NOT EXISTS tipo_itens (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===== TABELA CATEGORIA_ITENS_ESTOQUE =====
CREATE TABLE IF NOT EXISTS categoria_itens_estoque (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===== TABELA ITENS_ESTOQUE =====
CREATE TABLE IF NOT EXISTS itens_estoque (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    codigo VARCHAR(100) UNIQUE NOT NULL,
    categoria_id INTEGER REFERENCES categoria_itens_estoque(id),
    tipo_item_id INTEGER REFERENCES tipo_itens(id),
    cor VARCHAR(50),
    quantidade_inicial DECIMAL(10,3) DEFAULT 0.000,
    quantidade_atual DECIMAL(10,3) DEFAULT 0.000,
    estoque_minimo DECIMAL(10,3) DEFAULT 0.000,
    unidades_por_pacote INTEGER,
    unidade_medida_id INTEGER REFERENCES unidades_de_medida(id),
    fornecedor_id INTEGER REFERENCES fornecedores(id),
    fabricante VARCHAR(150),
    localizacao_estoque VARCHAR(100),
    especificacoes_tecnicas TEXT,
    descricao TEXT,
    largura DECIMAL(10,3),
    comprimento DECIMAL(10,3),
    espessura DECIMAL(10,3),
    volume DECIMAL(10,3),
    area DECIMAL(10,3),
    peso DECIMAL(10,3),
    custo_medio DECIMAL(10,2) DEFAULT 0.00,
    custo_atual DECIMAL(10,2) DEFAULT 0.00,
    status VARCHAR(20) DEFAULT 'Ativo',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===== TABELA MAQUINAS =====
CREATE TABLE IF NOT EXISTS maquinas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    codigo VARCHAR(100) UNIQUE,
    marca VARCHAR(100),
    tipo VARCHAR(100),
    numero_serie VARCHAR(100),
    data_aquisicao DATE,
    valor_aquisicao DECIMAL(12,2) DEFAULT 0.00,
    hora_maquina DECIMAL(10,2) DEFAULT 0.00,
    metros_quadrados_por_hora DECIMAL(10,3) DEFAULT 0.000,
    estado VARCHAR(50) DEFAULT 'Novo',
    localizacao VARCHAR(100),
    responsavel VARCHAR(100),
    status VARCHAR(20) DEFAULT 'Ativa',
    especificacoes_tecnicas TEXT,
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===== TABELA PRODUTOS_MATERIAIS =====
CREATE TABLE IF NOT EXISTS produtos_materiais (
    id SERIAL PRIMARY KEY,
    produto_id INTEGER REFERENCES produtos(id) ON DELETE CASCADE,
    item_estoque_id INTEGER REFERENCES itens_estoque(id),
    quantidade_necessaria DECIMAL(10,3) NOT NULL,
    area_utilizada DECIMAL(10,3) DEFAULT 0.000,
    custo_unitario DECIMAL(10,2) DEFAULT 0.00,
    custo_total DECIMAL(10,2) DEFAULT 0.00,
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===== TABELA ETAPAS_CONFECCAO =====
CREATE TABLE IF NOT EXISTS etapas_confeccao (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    tempo_estimado INTEGER, -- em minutos
    descricao TEXT,
    observacoes TEXT,
    maquina_id INTEGER REFERENCES maquinas(id),
    ferramenta_id INTEGER,
    mao_obra VARCHAR(100),
    custo_por_hora DECIMAL(10,2) DEFAULT 0.00,
    status VARCHAR(20) DEFAULT 'Ativa',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===== TABELA PRODUTOS_ETAPAS =====
CREATE TABLE IF NOT EXISTS produtos_etapas (
    id SERIAL PRIMARY KEY,
    produto_id INTEGER REFERENCES produtos(id) ON DELETE CASCADE,
    etapa_confeccao_id INTEGER REFERENCES etapas_confeccao(id),
    ordem INTEGER DEFAULT 1,
    tempo_estimado INTEGER, -- em minutos
    quantidade_necessaria DECIMAL(10,3) DEFAULT 1.000,
    custo_unitario DECIMAL(10,2) DEFAULT 0.00,
    custo_total DECIMAL(10,2) DEFAULT 0.00,
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===== TABELA CLIENTES =====
CREATE TABLE IF NOT EXISTS clientes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    tipo_pessoa VARCHAR(20) DEFAULT 'Física', -- 'Física' ou 'Jurídica'
    cpf_cnpj VARCHAR(18),
    telefone VARCHAR(20),
    whatsapp VARCHAR(20),
    email VARCHAR(150),
    endereco TEXT,
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    estado VARCHAR(50),
    pais VARCHAR(50) DEFAULT 'Brasil',
    cep VARCHAR(10),
    observacoes TEXT,
    status VARCHAR(20) DEFAULT 'Ativo',
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===== TABELA ORCAMENTOS =====
CREATE TABLE IF NOT EXISTS orcamentos (
    id SERIAL PRIMARY KEY,
    numero VARCHAR(20) UNIQUE NOT NULL,
    cliente_id INTEGER REFERENCES clientes(id),
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_validade DATE,
    valor_total DECIMAL(12,2) DEFAULT 0.00,
    desconto DECIMAL(10,2) DEFAULT 0.00,
    valor_final DECIMAL(12,2) DEFAULT 0.00,
    observacoes TEXT,
    status VARCHAR(20) DEFAULT 'Pendente',
    usuario_id INTEGER REFERENCES usuarios(id),
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===== TABELA ORCAMENTOS_ITENS =====
CREATE TABLE IF NOT EXISTS orcamentos_itens (
    id SERIAL PRIMARY KEY,
    orcamento_id INTEGER REFERENCES orcamentos(id) ON DELETE CASCADE,
    tipo_item VARCHAR(20) DEFAULT 'produto', -- 'produto' ou 'kit'
    produto_id INTEGER REFERENCES produtos(id),
    kit_id INTEGER,
    quantidade INTEGER DEFAULT 1,
    preco_unitario DECIMAL(10,2) DEFAULT 0.00,
    preco_total DECIMAL(10,2) DEFAULT 0.00,
    descricao_personalizada TEXT,
    observacoes TEXT
);

-- ===== TABELA NOTIFICACOES =====
CREATE TABLE IF NOT EXISTS notificacoes (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    mensagem TEXT NOT NULL,
    item_id INTEGER,
    lida BOOLEAN DEFAULT FALSE,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===== TABELA ENTRADAS_ESTOQUE =====
CREATE TABLE IF NOT EXISTS entradas_estoque (
    id SERIAL PRIMARY KEY,
    item_id INTEGER REFERENCES itens_estoque(id),
    quantidade DECIMAL(10,3) NOT NULL,
    data_entrada DATE NOT NULL,
    fornecedor VARCHAR(200),
    nota_fiscal VARCHAR(50),
    custo_unitario DECIMAL(10,2),
    data_validade DATE,
    lote VARCHAR(50),
    localizacao VARCHAR(100),
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===== TABELA SAIDAS_ESTOQUE =====
CREATE TABLE IF NOT EXISTS saidas_estoque (
    id SERIAL PRIMARY KEY,
    item_id INTEGER REFERENCES itens_estoque(id),
    quantidade DECIMAL(10,3) NOT NULL,
    data_saida DATE NOT NULL,
    motivo_saida VARCHAR(100),
    destino VARCHAR(200),
    localizacao VARCHAR(100),
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===== ÍNDICES PARA PERFORMANCE =====
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_produtos_codigo ON produtos(codigo);
CREATE INDEX IF NOT EXISTS idx_produtos_categoria ON produtos(categoria_id);
CREATE INDEX IF NOT EXISTS idx_itens_estoque_codigo ON itens_estoque(codigo);
CREATE INDEX IF NOT EXISTS idx_itens_estoque_categoria ON itens_estoque(categoria_id);
CREATE INDEX IF NOT EXISTS idx_produtos_materiais_produto ON produtos_materiais(produto_id);
CREATE INDEX IF NOT EXISTS idx_produtos_etapas_produto ON produtos_etapas(produto_id);
CREATE INDEX IF NOT EXISTS idx_orcamentos_cliente ON orcamentos(cliente_id);
CREATE INDEX IF NOT EXISTS idx_orcamentos_itens_orcamento ON orcamentos_itens(orcamento_id);

-- ===== DADOS INICIAIS =====
-- Inserir unidades de medida básicas
INSERT INTO unidades_de_medida (nome, is_measurement) VALUES 
('Metros', TRUE),
('Centímetros', TRUE),
('Metros Quadrados', TRUE),
('Litros', TRUE),
('Quilos', TRUE),
('Unidades', FALSE),
('Pacotes', FALSE)
ON CONFLICT (nome) DO NOTHING;

-- Inserir tipos de itens básicos
INSERT INTO tipo_itens (nome, descricao) VALUES 
('Material', 'Material para produção'),
('Ferramenta', 'Ferramenta de trabalho'),
('Equipamento', 'Equipamento de produção'),
('Consumível', 'Item consumível')
ON CONFLICT (nome) DO NOTHING;

-- Inserir categorias básicas
INSERT INTO categoria_itens_estoque (nome) VALUES 
('Matéria Prima'),
('Ferramentas'),
('Equipamentos'),
('Consumíveis'),
('Acabamentos')
ON CONFLICT (nome) DO NOTHING;

INSERT INTO categoria_produtos (nome, descricao) VALUES 
('Produtos Personalizados', 'Produtos feitos sob medida'),
('Produtos em Série', 'Produtos padronizados'),
('Serviços', 'Serviços oferecidos')
ON CONFLICT (nome) DO NOTHING;

-- Criar usuário administrador padrão (senha: admin123)
INSERT INTO usuarios (nome, email, senha, cargo, nivel_de_acesso) VALUES 
('Administrador', 'admin@midnight.com', 'scrypt:32768:8:1$nQ8zXvEykqHgfsjo$8f7f6b6d6e5c4e4e6d7c9b8a7e6f5d4c3b2a1f0e9d8c7b6a5e4d3c2b1a0f9e8d7c6b5a4e3d2c1b0a9f8e7d6c5b4a3e2d1c0b9a8f7e6d5c4b3a2e1d0c9b8a7f6e5d4c3b2a1e0d9c8b7a6f5e4d3c2b1a0f9e8d7c6b5a4e3d2c1b0a', 'Administrador', 3)
ON CONFLICT (email) DO NOTHING;

-- ===== FIM DO SCRIPT =====