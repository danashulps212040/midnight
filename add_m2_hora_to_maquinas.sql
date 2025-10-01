-- Adicionar coluna metros_quadrados_por_hora na tabela maquinas
ALTER TABLE maquinas ADD COLUMN metros_quadrados_por_hora DECIMAL(10,2) DEFAULT 0.00 AFTER hora_maquina;
