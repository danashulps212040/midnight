-- Criar tabela para favoritos
CREATE TABLE IF NOT EXISTS favoritos_produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    produto_id INT NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (produto_id) REFERENCES produtos(id),
    UNIQUE KEY unique_favorito (usuario_id, produto_id)
);

-- Criar tabela para vendas
CREATE TABLE IF NOT EXISTS vendas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT,
    subtotal DECIMAL(10,2) NOT NULL,
    desconto DECIMAL(10,2) DEFAULT 0.00,
    total DECIMAL(10,2) NOT NULL,
    metodo_pagamento ENUM('dinheiro', 'pix', 'debito', 'credito') NOT NULL,
    parcelas INT DEFAULT 1,
    data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Pendente', 'Concluída', 'Cancelada') DEFAULT 'Pendente',
    observacoes TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    INDEX idx_data_venda (data_venda),
    INDEX idx_usuario_id (usuario_id),
    INDEX idx_status (status)
);

-- Criar tabela para itens das vendas
CREATE TABLE IF NOT EXISTS vendas_itens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    venda_id INT NOT NULL,
    produto_id INT NOT NULL,
    quantidade INT NOT NULL,
    preco_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (venda_id) REFERENCES vendas(id) ON DELETE CASCADE,
    FOREIGN KEY (produto_id) REFERENCES produtos(id),
    INDEX idx_venda_id (venda_id),
    INDEX idx_produto_id (produto_id)
);
