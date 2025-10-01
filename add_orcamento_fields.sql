-- Script para adicionar colunas de subtotal, desconto e custo_total na tabela orcamentos

-- Adicionar coluna subtotal (ignorar se já existir)
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE table_name = 'orcamentos' 
     AND table_schema = 'midnight' 
     AND column_name = 'subtotal') = 0,
    'ALTER TABLE orcamentos ADD COLUMN subtotal DECIMAL(10,2) DEFAULT 0.00 COMMENT "Subtotal do orçamento sem desconto"',
    'SELECT "Coluna subtotal já existe"'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Adicionar coluna desconto (ignorar se já existir)
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE table_name = 'orcamentos' 
     AND table_schema = 'midnight' 
     AND column_name = 'desconto') = 0,
    'ALTER TABLE orcamentos ADD COLUMN desconto DECIMAL(5,2) DEFAULT 0.00 COMMENT "Desconto proporcional aplicado em %"',
    'SELECT "Coluna desconto já existe"'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Adicionar coluna custo_total (ignorar se já existir)
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE table_name = 'orcamentos' 
     AND table_schema = 'midnight' 
     AND column_name = 'custo_total') = 0,
    'ALTER TABLE orcamentos ADD COLUMN custo_total DECIMAL(10,2) DEFAULT 0.00 COMMENT "Custo total dos itens do orçamento"',
    'SELECT "Coluna custo_total já existe"'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
