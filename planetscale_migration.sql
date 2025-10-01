-- ====================================
-- SCRIPT DE MIGRAÇÃO PARA PLANETSCALE
-- Database: midnight
-- ====================================

-- Configurações iniciais para PlanetScale
SET foreign_key_checks = 0;

-- ====================================
-- TABELA: usuarios
-- ====================================
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    cargo VARCHAR(100),
    nivel_de_acesso INT DEFAULT 1,
    foto_de_perfil LONGBLOB,
    status ENUM('Ativo', 'Inativo') DEFAULT 'Ativo',
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ====================================
-- TABELA: unidades_de_medida
-- ====================================
CREATE TABLE IF NOT EXISTS unidades_de_medida (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) NOT NULL UNIQUE,
    is_measurement BOOLEAN DEFAULT FALSE
);

-- ====================================
-- TABELA: tipo_itens
-- ====================================
CREATE TABLE IF NOT EXISTS tipo_itens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT
);

-- ====================================
-- TABELA: categoria_itens_estoque
-- ====================================
CREATE TABLE IF NOT EXISTS categoria_itens_estoque (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE
);

-- ====================================
-- TABELA: fornecedores
-- ====================================
CREATE TABLE IF NOT EXISTS fornecedores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    cnpj VARCHAR(18),
    telefone VARCHAR(20),
    email VARCHAR(255),
    endereco TEXT,
    cidade VARCHAR(100),
    estado VARCHAR(50),
    cep VARCHAR(10),
    contato_nome VARCHAR(255),
    contato_telefone VARCHAR(20),
    contato_email VARCHAR(255),
    website VARCHAR(255),
    categoria_produtos TEXT,
    prazo_entrega VARCHAR(100),
    condicoes_pagamento TEXT,
    observacoes TEXT,
    status ENUM('Ativo', 'Inativo') DEFAULT 'Ativo',
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ====================================
-- TABELA: itens_estoque
-- ====================================
CREATE TABLE IF NOT EXISTS itens_estoque (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    codigo VARCHAR(100) UNIQUE NOT NULL,
    categoria_id INT,
    tipo_item_id INT,
    cor VARCHAR(50),
    quantidade_inicial DECIMAL(10,2) DEFAULT 0,
    quantidade_atual DECIMAL(10,2) DEFAULT 0,
    estoque_minimo DECIMAL(10,2) DEFAULT 0,
    unidades_por_pacote INT DEFAULT 1,
    unidade_medida_id INT,
    fornecedor_id INT,
    fabricante VARCHAR(255),
    localizacao_estoque VARCHAR(255),
    especificacoes_tecnicas TEXT,
    descricao TEXT,
    largura DECIMAL(10,2),
    comprimento DECIMAL(10,2),
    espessura DECIMAL(10,2),
    volume DECIMAL(10,4),
    area DECIMAL(10,4),
    peso DECIMAL(10,2),
    custo_atual DECIMAL(10,2) DEFAULT 0,
    custo_medio DECIMAL(10,2) DEFAULT 0,
    status ENUM('Ativo', 'Inativo') DEFAULT 'Ativo',
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categoria_itens_estoque(id),
    FOREIGN KEY (tipo_item_id) REFERENCES tipo_itens(id),
    FOREIGN KEY (unidade_medida_id) REFERENCES unidades_de_medida(id),
    FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id)
);

-- ====================================
-- TABELA: entradas_estoque
-- ====================================
CREATE TABLE IF NOT EXISTS entradas_estoque (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,
    quantidade DECIMAL(10,2) NOT NULL,
    data_entrada DATE NOT NULL,
    fornecedor VARCHAR(255),
    nota_fiscal VARCHAR(100),
    custo_unitario DECIMAL(10,2),
    data_validade DATE,
    lote VARCHAR(100),
    localizacao VARCHAR(255),
    observacoes TEXT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES itens_estoque(id) ON DELETE CASCADE
);

-- ====================================
-- TABELA: saidas_estoque
-- ====================================
CREATE TABLE IF NOT EXISTS saidas_estoque (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,
    quantidade DECIMAL(10,2) NOT NULL,
    data_saida DATE NOT NULL,
    motivo_saida VARCHAR(255),
    destino VARCHAR(255),
    localizacao VARCHAR(255),
    observacoes TEXT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES itens_estoque(id) ON DELETE CASCADE
);

-- ====================================
-- TABELA: clientes
-- ====================================
CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    tipo_pessoa ENUM('Física', 'Jurídica') DEFAULT 'Física',
    cpf_cnpj VARCHAR(18),
    telefone VARCHAR(20),
    whatsapp VARCHAR(20),
    email VARCHAR(255),
    endereco TEXT,
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    estado VARCHAR(50),
    pais VARCHAR(50) DEFAULT 'Brasil',
    cep VARCHAR(10),
    observacoes TEXT,
    status ENUM('Ativo', 'Inativo') DEFAULT 'Ativo',
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ====================================
-- TABELA: categoria_produtos
-- ====================================
CREATE TABLE IF NOT EXISTS categoria_produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT
);

-- ====================================
-- TABELA: produtos
-- ====================================
CREATE TABLE IF NOT EXISTS produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(100) UNIQUE NOT NULL,
    nome VARCHAR(255) NOT NULL,
    categoria_id INT,
    fornecedor_id INT,
    preco DECIMAL(10,2) DEFAULT 0,
    margem_lucro DECIMAL(5,2) DEFAULT 0,
    descricao TEXT,
    especificacoes_tecnicas TEXT,
    custo_materiais DECIMAL(10,2) DEFAULT 0,
    custo_etapas DECIMAL(10,2) DEFAULT 0,
    estoque DECIMAL(10,2) DEFAULT 0,
    status ENUM('Ativo', 'Inativo') DEFAULT 'Ativo',
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categoria_produtos(id),
    FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id)
);

-- ====================================
-- TABELA: produtos_materiais
-- ====================================
CREATE TABLE IF NOT EXISTS produtos_materiais (
    id INT AUTO_INCREMENT PRIMARY KEY,
    produto_id INT NOT NULL,
    material_id INT NOT NULL,
    quantidade_necessaria DECIMAL(10,4) NOT NULL,
    custo_unitario DECIMAL(10,2) DEFAULT 0,
    subtotal DECIMAL(10,2) DEFAULT 0,
    largura DECIMAL(10,2),
    altura DECIMAL(10,2),
    area_utilizada DECIMAL(10,4),
    FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE,
    FOREIGN KEY (material_id) REFERENCES itens_estoque(id)
);

-- ====================================
-- TABELA: maquinas
-- ====================================
CREATE TABLE IF NOT EXISTS maquinas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    codigo VARCHAR(100) UNIQUE NOT NULL,
    marca VARCHAR(100),
    tipo VARCHAR(100),
    numero_serie VARCHAR(100),
    data_aquisicao DATE,
    valor_aquisicao DECIMAL(10,2) DEFAULT 0,
    hora_maquina DECIMAL(10,2) DEFAULT 0,
    metros_quadrados_por_hora DECIMAL(10,2) DEFAULT 0,
    estado ENUM('Novo', 'Usado', 'Precisa Manutenção') DEFAULT 'Novo',
    localizacao VARCHAR(255),
    responsavel VARCHAR(255),
    status ENUM('Ativa', 'Inativa', 'Manutenção') DEFAULT 'Ativa',
    especificacoes_tecnicas TEXT,
    observacoes TEXT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ====================================
-- TABELA: ferramentas
-- ====================================
CREATE TABLE IF NOT EXISTS ferramentas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    codigo VARCHAR(100),
    tipo VARCHAR(100),
    descricao TEXT,
    status ENUM('Disponível', 'Em Uso', 'Manutenção', 'Indisponível') DEFAULT 'Disponível',
    localizacao VARCHAR(255),
    estado ENUM('Novo', 'Bom', 'Regular', 'Ruim') DEFAULT 'Bom',
    responsavel VARCHAR(255),
    marca VARCHAR(100),
    modelo VARCHAR(100),
    data_aquisicao DATE,
    observacoes TEXT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ====================================
-- TABELA: produtos_etapas
-- ====================================
CREATE TABLE IF NOT EXISTS produtos_etapas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    produto_id INT NOT NULL,
    nome VARCHAR(255) NOT NULL,
    tipo VARCHAR(100) DEFAULT 'Manual',
    equipamento_tipo ENUM('maquina', 'ferramenta', 'manual') DEFAULT 'manual',
    equipamento_id INT,
    equipamento_nome VARCHAR(255),
    material_id INT,
    material_nome VARCHAR(255),
    tempo_estimado DECIMAL(10,2) DEFAULT 0,
    custo_estimado DECIMAL(10,2) DEFAULT 0,
    FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE
);

-- ====================================
-- TABELA: historico_custos_maquinas
-- ====================================
CREATE TABLE IF NOT EXISTS historico_custos_maquinas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    maquina_id INT NOT NULL,
    hora_maquina_anterior DECIMAL(10,2),
    hora_maquina_nova DECIMAL(10,2),
    metros_quadrados_anterior DECIMAL(10,2),
    metros_quadrados_nova DECIMAL(10,2),
    data_alteracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    observacoes TEXT,
    FOREIGN KEY (maquina_id) REFERENCES maquinas(id) ON DELETE CASCADE
);

-- ====================================
-- TABELA: produtos_anexos
-- ====================================
CREATE TABLE IF NOT EXISTS produtos_anexos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    produto_id INT NOT NULL,
    nome_original VARCHAR(255) NOT NULL,
    conteudo_blob LONGBLOB,
    tamanho BIGINT,
    tipo_mime VARCHAR(100),
    data_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    caminho_fisico VARCHAR(500),
    descricao VARCHAR(255),
    FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE
);

-- ====================================
-- TABELA: kits
-- ====================================
CREATE TABLE IF NOT EXISTS kits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(100) UNIQUE NOT NULL,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    status ENUM('Ativo', 'Inativo') DEFAULT 'Ativo',
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ====================================
-- TABELA: kits_produtos
-- ====================================
CREATE TABLE IF NOT EXISTS kits_produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kit_id INT NOT NULL,
    produto_id INT NOT NULL,
    quantidade DECIMAL(10,2) DEFAULT 1,
    ordem INT DEFAULT 1,
    FOREIGN KEY (kit_id) REFERENCES kits(id) ON DELETE CASCADE,
    FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE
);

-- ====================================
-- TABELA: orcamentos
-- ====================================
CREATE TABLE IF NOT EXISTS orcamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero VARCHAR(100) UNIQUE NOT NULL,
    data_orcamento DATE NOT NULL,
    cliente_id INT NOT NULL,
    vendedor_id INT,
    data_validade DATE,
    validade_dias INT DEFAULT 30,
    prazo_entrega VARCHAR(100),
    data_hora_entrega DATETIME,
    condicoes_pagamento TEXT,
    parcelas INT DEFAULT 1,
    observacoes TEXT,
    valor_total DECIMAL(10,2) DEFAULT 0,
    subtotal DECIMAL(10,2) DEFAULT 0,
    desconto DECIMAL(10,2) DEFAULT 0,
    custo_total DECIMAL(10,2) DEFAULT 0,
    margem_lucro DECIMAL(5,2) DEFAULT 0,
    lucro_estimado DECIMAL(10,2) DEFAULT 0,
    status ENUM('Pendente', 'Aprovado', 'Rejeitado', 'Expirado') DEFAULT 'Pendente',
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (vendedor_id) REFERENCES usuarios(id)
);

-- ====================================
-- TABELA: orcamentos_itens
-- ====================================
CREATE TABLE IF NOT EXISTS orcamentos_itens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    orcamento_id INT NOT NULL,
    produto_id INT,
    produto_nome VARCHAR(255) NOT NULL,
    quantidade DECIMAL(10,2) NOT NULL,
    preco_unitario DECIMAL(10,2) DEFAULT 0,
    preco_total DECIMAL(10,2) DEFAULT 0,
    descricao TEXT,
    kit_origem VARCHAR(100),
    kit_id INT,
    custo_unitario DECIMAL(10,2) DEFAULT 0,
    desconto_item DECIMAL(10,2) DEFAULT 0,
    subtotal DECIMAL(10,2) DEFAULT 0,
    FOREIGN KEY (orcamento_id) REFERENCES orcamentos(id) ON DELETE CASCADE,
    FOREIGN KEY (produto_id) REFERENCES produtos(id),
    FOREIGN KEY (kit_id) REFERENCES kits(id)
);

-- ====================================
-- TABELA: notificacoes
-- ====================================
CREATE TABLE IF NOT EXISTS notificacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo VARCHAR(100) NOT NULL,
    mensagem TEXT NOT NULL,
    item_id INT,
    lida BOOLEAN DEFAULT FALSE,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES itens_estoque(id)
);

-- ====================================
-- TABELA: favoritos_produtos
-- ====================================
CREATE TABLE IF NOT EXISTS favoritos_produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    produto_id INT NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE,
    UNIQUE KEY unique_favorito (usuario_id, produto_id)
);

-- ====================================
-- INSERIR DADOS BÁSICOS
-- ====================================

-- Unidades de medida básicas
INSERT IGNORE INTO unidades_de_medida (nome, is_measurement) VALUES 
('Unidade', 0),
('Metro', 1),
('Metro²', 1),
('Litro', 1),
('Quilograma', 1),
('Peça', 0),
('Pacote', 0),
('Caixa', 0);

-- Tipos de itens básicos
INSERT IGNORE INTO tipo_itens (nome, descricao) VALUES 
('Material Básico', 'Materiais básicos para produção'),
('Pacote Fechado', 'Materiais vendidos em pacotes fechados'),
('Frasco', 'Frascos e recipientes'),
('Garrafa', 'Garrafas e recipientes líquidos'),
('Embalagem', 'Embalagens e materiais de acondicionamento'),
('Unidade Fracionada', 'Unidades individuais fracionadas'),
('Porção Fracionada', 'Porções fracionadas por volume ou peso');

-- Usuário administrador padrão (senha: admin123)
INSERT IGNORE INTO usuarios (nome, email, senha, cargo, nivel_de_acesso) VALUES 
('Administrador', 'admin@midnight.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewBVr5XUE.oz5XHy', 'Administrador', 5);

-- Reativar verificações de chave estrangeira
SET foreign_key_checks = 1;

-- ====================================
-- VERIFICAÇÃO FINAL
-- ====================================
SELECT 'Migração concluída com sucesso!' as status;