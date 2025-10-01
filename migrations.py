import mysql.connector
from mysql.connector import Error

def create_database():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="als32@#nss"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Criar banco de dados
            cursor.execute("CREATE DATABASE IF NOT EXISTS midnight")
            print("Banco de dados 'midnight' criado com sucesso!")
            
            # Selecionar o banco de dados
            cursor.execute("USE midnight")
            
            # Criar tabela usuarios
#            cursor.execute("""
 #               CREATE TABLE IF NOT EXISTS usuarios (
  #                  id INT AUTO_INCREMENT PRIMARY KEY,
   #                 nome VARCHAR(100) NOT NULL,
    #                email VARCHAR(100) NOT NULL UNIQUE,
     #               senha VARCHAR(255) NOT NULL,
      #              cargo VARCHAR(50) NOT NULL,
       #             nivel_de_acesso INT NOT NULL,
        #            foto_de_perfil LONGBLOB,
         #           status VARCHAR(50) DEFAULT 'active',
          #          CONSTRAINT chk_nivel_acesso CHECK (nivel_de_acesso >= 0 AND nivel_de_acesso <= 5)
           #     ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            #""")
            #print("Tabela 'usuarios' criada com sucesso!")

            # Criar tabela categoria_itens_estoque
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categoria_itens_estoque (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(255) NOT NULL UNIQUE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("Tabela 'categoria_itens_estoque' criada com sucesso!")
            
            # Criar tabela itens_estoque
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS itens_estoque (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(255) NOT NULL,
                    codigo VARCHAR(255) NOT NULL UNIQUE,
                    categoria VARCHAR(255),
                    cor VARCHAR(100),
                    quantidade_inicial INT NOT NULL,
                    quantidade_atual INT NOT NULL,
                    estoque_minimo INT NOT NULL,
                    unidade_medida VARCHAR(50),
                    fornecedor VARCHAR(255),
                    localizacao_estoque VARCHAR(255),
                    especificacoes_tecnicas TEXT,
                    descricao TEXT,
                    largura DECIMAL(10,2),
                    comprimento DECIMAL(10,2),
                    peso DECIMAL(10,2),
                    custo_medio DECIMAL(10,2) DEFAULT 0.00,
                    observacoes TEXT,
                    status VARCHAR(50) DEFAULT 'ativo',
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("Tabela 'itens_estoque' criada com sucesso!")

            # Criar tabela entradas_estoque
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entradas_estoque (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    item_id INT NOT NULL,
                    quantidade INT NOT NULL,
                    data_entrada DATE NOT NULL,
                    fornecedor VARCHAR(255),
                    nota_fiscal VARCHAR(100),
                    custo_unitario DECIMAL(10,2),
                    data_validade DATE,
                    lote VARCHAR(100),
                    localizacao VARCHAR(255),
                    observacoes TEXT,
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (item_id) REFERENCES itens_estoque(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("Tabela 'entradas_estoque' criada com sucesso!")
            
            # Criar tabela saidas_estoque
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS saidas_estoque (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    item_id INT NOT NULL,
                    quantidade INT NOT NULL,
                    data_saida DATE NOT NULL,
                    motivo_saida ENUM('Consumo Interno', 'Transferência', 'Devolução', 'Descarte', 'Outros') NOT NULL,
                    destino VARCHAR(255),
                    localizacao VARCHAR(255),
                    observacoes TEXT,
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (item_id) REFERENCES itens_estoque(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("Tabela 'saidas_estoque' criada com sucesso!")
            
            # Criar tabela notificacoes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notificacoes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    tipo VARCHAR(50) NOT NULL,
                    mensagem TEXT NOT NULL,
                    item_id INT,
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    lida BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (item_id) REFERENCES itens_estoque(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("Tabela 'notificacoes' criada com sucesso!")
            
            # Criar tabela fornecedores
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fornecedores (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(255) NOT NULL,
                    cnpj VARCHAR(18) UNIQUE,
                    telefone VARCHAR(20),
                    email VARCHAR(100),
                    endereco VARCHAR(255),
                    cidade VARCHAR(100),
                    estado VARCHAR(2),
                    cep VARCHAR(10),
                    contato_nome VARCHAR(100),
                    contato_telefone VARCHAR(20),
                    contato_email VARCHAR(100),
                    website VARCHAR(255),
                    categoria_produtos VARCHAR(255),
                    prazo_entrega VARCHAR(50),
                    condicoes_pagamento VARCHAR(100),
                    observacoes TEXT,
                    observacoes TEXT,
                    status VARCHAR(50) DEFAULT 'ativo',
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("Tabela 'fornecedores' criada com sucesso!")
            
            # Criar tabela unidades_de_medida
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS unidades_de_medida (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(50) NOT NULL UNIQUE,
                    is_measurement BOOLEAN DEFAULT FALSE,
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("Tabela 'unidades_de_medida' criada com sucesso!")

            # Criar tabela clientes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(255) NOT NULL,
                    email VARCHAR(100),
                    telefone VARCHAR(20),
                    whatsapp VARCHAR(20),
                    cpf_cnpj VARCHAR(18),
                    tipo_pessoa VARCHAR(50),
                    cep VARCHAR(9),
                    endereco VARCHAR(255),
                    bairro VARCHAR(100),
                    cidade VARCHAR(100),
                    estado VARCHAR(2),
                    pais VARCHAR(100) DEFAULT 'Brasil',
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    observacoes TEXT,
                    status VARCHAR(50) DEFAULT 'ativo'
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("Tabela 'clientes' criada com sucesso!")
            
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexão ao MySQL fechada.")

def add_custo_medio_column():
    """Adiciona a coluna custo_medio à tabela itens_estoque se ela não existir"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="als32@#nss",
            database="midnight"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Verificar se a coluna custo_medio já existe
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'midnight' 
                AND TABLE_NAME = 'itens_estoque' 
                AND COLUMN_NAME = 'custo_medio'
            """)
            
            if cursor.fetchone()[0] == 0:
                # Adicionar a coluna custo_medio
                cursor.execute("""
                    ALTER TABLE itens_estoque 
                    ADD COLUMN custo_medio DECIMAL(10,2) DEFAULT 0.00 
                    AFTER peso
                """)
                print("Coluna 'custo_medio' adicionada à tabela 'itens_estoque' com sucesso!")
                connection.commit()
            else:
                print("Coluna 'custo_medio' já existe na tabela 'itens_estoque'")
                
    except Error as e:
        print(f"Erro ao adicionar coluna custo_medio: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def add_custo_atual_column():
    """Adiciona a coluna custo_atual à tabela itens_estoque se ela não existir"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="als32@#nss",
            database="midnight"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Verificar se a coluna custo_atual já existe
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'midnight' 
                AND TABLE_NAME = 'itens_estoque' 
                AND COLUMN_NAME = 'custo_atual'
            """)
            
            if cursor.fetchone()[0] == 0:
                # Adicionar a coluna custo_atual
                cursor.execute("""
                    ALTER TABLE itens_estoque 
                    ADD COLUMN custo_atual DECIMAL(10,2) DEFAULT 0.00 
                    AFTER custo_medio
                """)
                print("Coluna 'custo_atual' adicionada à tabela 'itens_estoque' com sucesso!")
                connection.commit()
            else:
                print("Coluna 'custo_atual' já existe na tabela 'itens_estoque'")
                
    except Error as e:
        print(f"Erro ao adicionar coluna custo_atual: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def create_categoria_produtos_table():
    """Cria a tabela categoria_produtos se ela não existir"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="als32@#nss",
            database="midnight"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Criar tabela categoria_produtos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categoria_produtos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(255) NOT NULL UNIQUE,
                    descricao TEXT,
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("Tabela 'categoria_produtos' criada com sucesso!")
            connection.commit()
                
    except Error as e:
        print(f"Erro ao criar tabela categoria_produtos: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def create_produtos_table():
    """Cria a tabela produtos se ela não existir"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="als32@#nss",
            database="midnight"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Criar tabela produtos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS produtos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    codigo VARCHAR(100) NOT NULL UNIQUE,
                    nome VARCHAR(255) NOT NULL,
                    categoria_id INT,
                    preco DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                    custo_materiais DECIMAL(10,2) DEFAULT 0.00,
                    custo_etapas DECIMAL(10,2) DEFAULT 0.00,
                    margem_lucro DECIMAL(5,2) DEFAULT 0.00,
                    descricao TEXT,
                    especificacoes_tecnicas TEXT,
                    fornecedor_id INT,
                    estoque INT DEFAULT 0,
                    status VARCHAR(50) DEFAULT 'Ativo',
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (categoria_id) REFERENCES categoria_produtos(id) ON DELETE SET NULL,
                    FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("Tabela 'produtos' criada com sucesso!")
            
            # Criar tabela produtos_materiais (para relacionar produtos com materiais do estoque)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS produtos_materiais (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    produto_id INT NOT NULL,
                    material_id INT NOT NULL,
                    quantidade_necessaria DECIMAL(10,3) NOT NULL,
                    largura DECIMAL(8,2) DEFAULT NULL,
                    altura DECIMAL(8,2) DEFAULT NULL,
                    area_utilizada DECIMAL(10,4) DEFAULT NULL,
                    custo_unitario DECIMAL(10,2),
                    subtotal DECIMAL(10,2) DEFAULT 0.00,
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE,
                    FOREIGN KEY (material_id) REFERENCES itens_estoque(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_produto_material (produto_id, material_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("Tabela 'produtos_materiais' criada com sucesso!")
            
            # Criar tabela produtos_etapas (para armazenar etapas de confecção dos produtos)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS produtos_etapas (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    produto_id INT NOT NULL,
                    nome VARCHAR(255) NOT NULL,
                    tipo VARCHAR(100) NOT NULL,
                    equipamento_tipo ENUM('maquina', 'ferramenta', 'manual') DEFAULT 'manual',
                    equipamento_id INT DEFAULT NULL,
                    equipamento_nome VARCHAR(255) DEFAULT NULL,
                    material_id INT DEFAULT NULL,
                    material_nome VARCHAR(255) DEFAULT NULL,
                    tempo_estimado TIME NOT NULL,
                    custo_estimado DECIMAL(10,2) DEFAULT 0.00,
                    ordem_execucao INT DEFAULT 1,
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE,
                    FOREIGN KEY (material_id) REFERENCES itens_estoque(id) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("Tabela 'produtos_etapas' criada com sucesso!")
            
            connection.commit()
                
    except Error as e:
        print(f"Erro ao criar tabela produtos: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def create_maquinas_tables():
    """Cria as tabelas relacionadas a máquinas se elas não existirem"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="als32@#nss",
            database="midnight"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Criar tabela tipos_maquinas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tipos_maquinas (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(100) NOT NULL UNIQUE,
                    descricao TEXT,
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("Tabela 'tipos_maquinas' criada com sucesso!")
            
            # Criar tabela maquinas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS maquinas (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    codigo VARCHAR(100) NOT NULL UNIQUE,
                    nome VARCHAR(255) NOT NULL,
                    marca VARCHAR(100),
                    tipo VARCHAR(100),
                    numero_serie VARCHAR(100),
                    data_aquisicao DATE,
                    valor_aquisicao DECIMAL(10,2) DEFAULT 0.00,
                    hora_maquina DECIMAL(10,2) DEFAULT 0.00,
                    estado ENUM('Novo', 'Seminovo', 'Usado - Bom', 'Usado - Regular', 'Usado - Ruim', 'Necessita Reparo') DEFAULT 'Novo',
                    localizacao VARCHAR(255),
                    responsavel VARCHAR(255),
                    status ENUM('Ativa', 'Inativa', 'Em Manutenção', 'Aguardando Peças', 'Descartada') DEFAULT 'Ativa',
                    especificacoes_tecnicas TEXT,
                    observacoes TEXT,
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("Tabela 'maquinas' criada com sucesso!")
            
            # Criar tabela manutencoes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS manutencoes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    maquina_id INT NOT NULL,
                    tipo_manutencao ENUM('Preventiva', 'Corretiva', 'Preditiva', 'Calibração', 'Inspeção') NOT NULL,
                    data_manutencao DATE NOT NULL,
                    responsavel VARCHAR(255),
                    fornecedor_empresa VARCHAR(255),
                    descricao_servicos TEXT,
                    custo DECIMAL(10,2) DEFAULT 0.00,
                    proxima_manutencao DATE,
                    observacoes TEXT,
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (maquina_id) REFERENCES maquinas(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("Tabela 'manutencoes' criada com sucesso!")
            
            connection.commit()
                
    except Error as e:
        print(f"Erro ao criar tabelas de máquinas: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def create_ferramentas_table():
    """Cria a tabela ferramentas se ela não existir"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="als32@#nss",
            database="midnight"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Criar tabela ferramentas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ferramentas (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(255) NOT NULL,
                    codigo VARCHAR(100),
                    tipo ENUM('manual', 'eletrica', 'pneumatica', 'hidraulica', 'corte', 'medicao', 'fixacao', 'acabamento'),
                    descricao TEXT,
                    status ENUM('disponivel', 'em_uso', 'manutencao', 'danificada', 'inativa') DEFAULT 'disponivel',
                    localizacao VARCHAR(255),
                    estado ENUM('excelente', 'bom', 'regular', 'ruim', 'pessimo'),
                    responsavel VARCHAR(255),
                    marca VARCHAR(100),
                    modelo VARCHAR(100),
                    data_aquisicao DATE,
                    observacoes TEXT,
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("Tabela 'ferramentas' criada com sucesso!")
            
            connection.commit()
                
    except Error as e:
        print(f"Erro ao criar tabela ferramentas: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def create_etapas_confeccao_table():
    """Cria a tabela etapas_confeccao se ela não existir"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="als32@#nss",
            database="midnight"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Criar tabela etapas_confeccao
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS etapas_confeccao (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(255) NOT NULL,
                    tempo_estimado VARCHAR(100),
                    descricao TEXT,
                    observacoes TEXT,
                    maquina_id INT,
                    ferramenta_id INT,
                    mao_obra VARCHAR(255),
                    custo_por_hora DECIMAL(10,2) DEFAULT 0.00,
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (maquina_id) REFERENCES maquinas(id) ON DELETE SET NULL,
                    FOREIGN KEY (ferramenta_id) REFERENCES ferramentas(id) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("Tabela 'etapas_confeccao' criada com sucesso!")
            
            connection.commit()
                
    except Error as e:
        print(f"Erro ao criar tabela etapas_confeccao: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def create_tipo_itens_table():
    """Cria a tabela tipo_itens com os tipos pré-cadastrados"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="als32@#nss",
            database="midnight"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Criar tabela tipo_itens
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tipo_itens (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(100) NOT NULL UNIQUE,
                    descricao VARCHAR(255),
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("Tabela 'tipo_itens' criada com sucesso!")
            
            # Inserir os tipos de itens padrão
            cursor.execute("""
                INSERT IGNORE INTO tipo_itens (nome, descricao) VALUES
                ('Pacote Fechado', 'Item vendido em pacotes fechados'),
                ('Unidade Fracionada', 'Item que pode ser vendido em frações'),
                ('Rolo/Bobina', 'Item em formato de rolo ou bobina'),
                ('Chapa/Placa', 'Item em formato de chapa ou placa'),
                ('Embalagem', 'Materiais de embalagem'),
                ('Suporte', 'Materiais de suporte ou apoio')
            """)
            print("Tipos de itens padrão inseridos com sucesso!")
            
            connection.commit()
                
    except Error as e:
        print(f"Erro ao criar tabela tipo_itens: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def add_missing_columns_to_itens_estoque():
    """Adiciona as colunas faltantes à tabela itens_estoque"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="als32@#nss",
            database="midnight"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Lista de colunas a serem adicionadas
            columns_to_add = [
                ("tipo_item_id", "INT", "AFTER categoria", "Chave estrangeira para tipo_itens"),
                ("unidades_por_pacote", "INT DEFAULT 1", "AFTER estoque_minimo", "Quantidade de unidades por pacote"),
                ("espessura", "DECIMAL(10,3)", "AFTER comprimento", "Espessura em mm"),
                ("volume", "DECIMAL(10,2)", "AFTER espessura", "Volume em litros"),
                ("area", "DECIMAL(10,4)", "AFTER volume", "Área calculada em m²")
            ]
            
            for column_name, column_type, position, description in columns_to_add:
                # Verificar se a coluna já existe
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = 'midnight' 
                    AND TABLE_NAME = 'itens_estoque' 
                    AND COLUMN_NAME = %s
                """, (column_name,))
                
                if cursor.fetchone()[0] == 0:
                    # Adicionar a coluna
                    query = f"ALTER TABLE itens_estoque ADD COLUMN {column_name} {column_type} {position}"
                    cursor.execute(query)
                    print(f"Coluna '{column_name}' adicionada à tabela 'itens_estoque' com sucesso! ({description})")
                else:
                    print(f"Coluna '{column_name}' já existe na tabela 'itens_estoque'")
            
            # Adicionar foreign key para tipo_item_id se a coluna foi criada
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                WHERE TABLE_SCHEMA = 'midnight' 
                AND TABLE_NAME = 'itens_estoque' 
                AND COLUMN_NAME = 'tipo_item_id'
                AND REFERENCED_TABLE_NAME = 'tipo_itens'
            """)
            
            if cursor.fetchone()[0] == 0:
                try:
                    cursor.execute("""
                        ALTER TABLE itens_estoque 
                        ADD CONSTRAINT fk_itens_estoque_tipo_item 
                        FOREIGN KEY (tipo_item_id) REFERENCES tipo_itens(id) ON DELETE SET NULL
                    """)
                    print("Foreign key para tipo_item_id adicionada com sucesso!")
                except Error as fk_error:
                    print(f"Aviso: Não foi possível adicionar foreign key para tipo_item_id: {fk_error}")
            
            connection.commit()
                
    except Error as e:
        print(f"Erro ao adicionar colunas faltantes: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def update_itens_estoque_to_use_ids():
    """Atualiza a tabela itens_estoque para usar IDs em vez de nomes para categoria, unidade_medida e fornecedor"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="als32@#nss",
            database="midnight"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            print("Iniciando atualização da estrutura da tabela itens_estoque...")
            
            # 1. Adicionar novas colunas para IDs
            new_columns = [
                ("categoria_id", "INT", "AFTER categoria"),
                ("unidade_medida_id", "INT", "AFTER unidade_medida"),
                ("fornecedor_id", "INT", "AFTER fornecedor")
            ]
            
            for column_name, column_type, position in new_columns:
                # Verificar se a coluna já existe
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = 'midnight' 
                    AND TABLE_NAME = 'itens_estoque' 
                    AND COLUMN_NAME = %s
                """, (column_name,))
                
                if cursor.fetchone()[0] == 0:
                    query = f"ALTER TABLE itens_estoque ADD COLUMN {column_name} {column_type} {position}"
                    cursor.execute(query)
                    print(f"Coluna '{column_name}' adicionada com sucesso!")
                else:
                    print(f"Coluna '{column_name}' já existe")
            
            # 2. Migrar dados das colunas de texto para as colunas de ID
            print("Migrando dados de categoria...")
            cursor.execute("""
                UPDATE itens_estoque ie 
                SET categoria_id = (
                    SELECT c.id 
                    FROM categoria_itens_estoque c 
                    WHERE c.nome = ie.categoria
                    LIMIT 1
                )
                WHERE ie.categoria IS NOT NULL AND ie.categoria != ''
            """)
            
            print("Migrando dados de unidade de medida...")
            cursor.execute("""
                UPDATE itens_estoque ie 
                SET unidade_medida_id = (
                    SELECT u.id 
                    FROM unidades_de_medida u 
                    WHERE u.nome = ie.unidade_medida
                    LIMIT 1
                )
                WHERE ie.unidade_medida IS NOT NULL AND ie.unidade_medida != ''
            """)
            
            print("Migrando dados de fornecedor...")
            cursor.execute("""
                UPDATE itens_estoque ie 
                SET fornecedor_id = (
                    SELECT f.id 
                    FROM fornecedores f 
                    WHERE f.nome = ie.fornecedor
                    LIMIT 1
                )
                WHERE ie.fornecedor IS NOT NULL AND ie.fornecedor != ''
            """)
            
            # 3. Adicionar foreign keys
            foreign_keys = [
                ("fk_itens_categoria", "categoria_id", "categoria_itens_estoque", "id"),
                ("fk_itens_unidade", "unidade_medida_id", "unidades_de_medida", "id"),
                ("fk_itens_fornecedor", "fornecedor_id", "fornecedores", "id")
            ]
            
            for fk_name, column, ref_table, ref_column in foreign_keys:
                # Verificar se a foreign key já existe
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                    WHERE TABLE_SCHEMA = 'midnight' 
                    AND TABLE_NAME = 'itens_estoque' 
                    AND CONSTRAINT_NAME = %s
                """, (fk_name,))
                
                if cursor.fetchone()[0] == 0:
                    try:
                        cursor.execute(f"""
                            ALTER TABLE itens_estoque 
                            ADD CONSTRAINT {fk_name} 
                            FOREIGN KEY ({column}) REFERENCES {ref_table}({ref_column}) ON DELETE SET NULL
                        """)
                        print(f"Foreign key '{fk_name}' adicionada com sucesso!")
                    except Error as fk_error:
                        print(f"Aviso: Não foi possível adicionar foreign key '{fk_name}': {fk_error}")
                else:
                    print(f"Foreign key '{fk_name}' já existe")
            
            connection.commit()
            print("Atualização da estrutura concluída com sucesso!")
                
    except Error as e:
        print(f"Erro ao atualizar estrutura da tabela: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def add_fabricante_column():
    """Adiciona a coluna fabricante à tabela itens_estoque se ela não existir"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="als32@#nss",
            database="midnight"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Verificar se a coluna fabricante já existe
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'midnight' 
                AND TABLE_NAME = 'itens_estoque' 
                AND COLUMN_NAME = 'fabricante'
            """)
            
            if cursor.fetchone()[0] == 0:
                # Adicionar a coluna fabricante
                cursor.execute("""
                    ALTER TABLE itens_estoque 
                    ADD COLUMN fabricante VARCHAR(255) 
                    AFTER fornecedor_id
                """)
                print("Coluna 'fabricante' adicionada à tabela 'itens_estoque' com sucesso!")
                connection.commit()
            else:
                print("Coluna 'fabricante' já existe na tabela 'itens_estoque'")
                
    except Error as e:
        print(f"Erro ao adicionar coluna fabricante: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def add_metros_quadrados_por_hora_column():
    """Adiciona a coluna metros_quadrados_por_hora à tabela maquinas se ela não existir"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="als32@#nss",
            database="midnight"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Verificar se a coluna metros_quadrados_por_hora já existe
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'midnight' 
                AND TABLE_NAME = 'maquinas' 
                AND COLUMN_NAME = 'metros_quadrados_por_hora'
            """)
            
            if cursor.fetchone()[0] == 0:
                # Adicionar a coluna metros_quadrados_por_hora
                cursor.execute("""
                    ALTER TABLE maquinas 
                    ADD COLUMN metros_quadrados_por_hora DECIMAL(10,2) DEFAULT 0.00 
                    AFTER hora_maquina
                """)
                print("Coluna 'metros_quadrados_por_hora' adicionada à tabela 'maquinas' com sucesso!")
                connection.commit()
            else:
                print("Coluna 'metros_quadrados_por_hora' já existe na tabela 'maquinas'")
                
    except Error as e:
        print(f"Erro ao adicionar coluna metros_quadrados_por_hora: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def fix_motivo_saida_column():
    """Altera a coluna motivo_saida de ENUM para VARCHAR para permitir textos personalizados"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="als32@#nss",
            database="midnight"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Verificar o tipo atual da coluna motivo_saida
            cursor.execute("""
                SELECT DATA_TYPE, COLUMN_TYPE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'midnight' 
                AND TABLE_NAME = 'saidas_estoque' 
                AND COLUMN_NAME = 'motivo_saida'
            """)
            
            result = cursor.fetchone()
            if result and 'enum' in result[1].lower():
                print("Alterando coluna 'motivo_saida' de ENUM para VARCHAR...")
                
                # Alterar a coluna para VARCHAR
                cursor.execute("""
                    ALTER TABLE saidas_estoque 
                    MODIFY COLUMN motivo_saida VARCHAR(100) NOT NULL
                """)
                print("Coluna 'motivo_saida' alterada para VARCHAR(100) com sucesso!")
                connection.commit()
            else:
                print("Coluna 'motivo_saida' já está configurada corretamente")
                
    except Error as e:
        print(f"Erro ao alterar coluna motivo_saida: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def add_frasco_garrafa_tipo_item():
    """Adiciona o novo tipo de item 'Frasco/Garrafa' se não existir"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="als32@#nss",
            database="midnight"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Verificar se o tipo "Frasco/Garrafa" já existe
            cursor.execute("""
                SELECT COUNT(*) 
                FROM tipo_itens 
                WHERE nome = 'Frasco/Garrafa'
            """)
            
            if cursor.fetchone()[0] == 0:
                # Inserir o novo tipo de item
                cursor.execute("""
                    INSERT INTO tipo_itens (nome, descricao) 
                    VALUES ('Frasco/Garrafa', 'Recipientes em formato de frasco ou garrafa para armazenamento')
                """)
                print("Tipo de item 'Frasco/Garrafa' adicionado com sucesso!")
                connection.commit()
            else:
                print("Tipo de item 'Frasco/Garrafa' já existe na tabela")
                
    except Error as e:
        print(f"Erro ao adicionar tipo de item Frasco/Garrafa: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def convert_volume_to_decimal():
    """Converte a coluna volume de INT de volta para DECIMAL(10,2) para permitir casas decimais em litros"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="als32@#nss",
            database="midnight"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            print("Verificando se a conversão de volume para DECIMAL é necessária...")
            
            # Verificar o tipo atual da coluna volume
            cursor.execute("""
                SELECT DATA_TYPE, COLUMN_TYPE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'midnight' 
                AND TABLE_NAME = 'itens_estoque' 
                AND COLUMN_NAME = 'volume'
            """)
            
            result = cursor.fetchone()
            if result:
                data_type, column_type = result
                print(f"Tipo atual da coluna volume: {data_type} ({column_type})")
                
                if 'int' in data_type.lower():
                    print("Convertendo coluna 'volume' de INT para DECIMAL(10,3)...")
                    
                    # 1. Primeiro, converter valores existentes dividindo por 1000 (mililitros para litros)
                    print("Convertendo valores existentes de mililitros para litros...")
                    cursor.execute("""
                        UPDATE itens_estoque 
                        SET volume = volume / 1000.0
                        WHERE volume IS NOT NULL AND volume > 0
                    """)
                    
                    # 2. Alterar o tipo da coluna para DECIMAL(10,3)
                    print("Alterando tipo da coluna para DECIMAL(10,3)...")
                    cursor.execute("""
                        ALTER TABLE itens_estoque 
                        MODIFY COLUMN volume DECIMAL(10,3) COMMENT 'Volume em litros'
                    """)
                    
                    print("Coluna 'volume' convertida para DECIMAL(10,3) (litros) com sucesso!")
                    connection.commit();
                    
                    # 3. Verificar alguns valores convertidos
                    cursor.execute("""
                        SELECT id, nome, volume 
                        FROM itens_estoque 
                        WHERE volume IS NOT NULL 
                        LIMIT 5
                    """)
                    items = cursor.fetchall();
                    if items:
                        print("Valores convertidos (amostra):")
                        for item in items:
                            print(f"  ID: {item[0]}, Nome: {item[1]}, Volume: {item[2]}L")
                    
                elif 'decimal' in data_type.lower():
                    print("Coluna 'volume' já está no formato DECIMAL")
                    # Verificar se tem a precisão correta (10,2)
                    if 'decimal(10,2)' not in column_type.lower():
                        print("Ajustando precisão da coluna volume para DECIMAL(10,2)...")
                        cursor.execute("""
                            ALTER TABLE itens_estoque 
                            MODIFY COLUMN volume DECIMAL(10,2) COMMENT 'Volume em litros'
                        """)
                        print("Precisão da coluna 'volume' ajustada para DECIMAL(10,2)!")
                        connection.commit()
                    else:
                        print("Coluna 'volume' já está com a precisão correta DECIMAL(10,2)")
                        
            else:
                print("Coluna 'volume' não encontrada!")
                
    except Error as e:
        print(f"Erro ao converter coluna volume: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def update_produtos_tables_structure():
    """Atualiza a estrutura das tabelas de produtos se elas já existirem"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="als32@#nss",
            database="midnight"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Verificar e adicionar coluna custo_etapas na tabela produtos
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'midnight' 
                AND TABLE_NAME = 'produtos' 
                AND COLUMN_NAME = 'custo_etapas'
            """)
            
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    ALTER TABLE produtos 
                    ADD COLUMN custo_etapas DECIMAL(10,2) DEFAULT 0.00 
                    AFTER custo_materiais
                """)
                print("Coluna 'custo_etapas' adicionada à tabela 'produtos' com sucesso!")
            
            # Verificar e adicionar colunas na tabela produtos_materiais
            columns_to_add = [
                ('largura', 'DECIMAL(8,2) DEFAULT NULL AFTER quantidade_necessaria'),
                ('altura', 'DECIMAL(8,2) DEFAULT NULL AFTER largura'),
                ('area_utilizada', 'DECIMAL(10,4) DEFAULT NULL AFTER altura'),
                ('subtotal', 'DECIMAL(10,2) DEFAULT 0.00 AFTER custo_unitario')
            ]
            
            for column_name, column_definition in columns_to_add:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = 'midnight' 
                    AND TABLE_NAME = 'produtos_materiais' 
                    AND COLUMN_NAME = %s
                """, (column_name,))
                
                if cursor.fetchone()[0] == 0:
                    cursor.execute(f"ALTER TABLE produtos_materiais ADD COLUMN {column_name} {column_definition}")
                    print(f"Coluna '{column_name}' adicionada à tabela 'produtos_materiais' com sucesso!")
            
            # Criar tabela produtos_etapas se não existir
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS produtos_etapas (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    produto_id INT NOT NULL,
                    nome VARCHAR(255) NOT NULL,
                    tipo VARCHAR(100) NOT NULL,
                    equipamento_tipo ENUM('maquina', 'ferramenta', 'manual') DEFAULT 'manual',
                    equipamento_id INT DEFAULT NULL,
                    equipamento_nome VARCHAR(255) DEFAULT NULL,
                    material_id INT DEFAULT NULL,
                    material_nome VARCHAR(255) DEFAULT NULL,
                    tempo_estimado TIME NOT NULL,
                    custo_estimado DECIMAL(10,2) DEFAULT 0.00,
                    ordem_execucao INT DEFAULT 1,
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE,
                    FOREIGN KEY (material_id) REFERENCES itens_estoque(id) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("Tabela 'produtos_etapas' criada com sucesso!")
            
            connection.commit()
                
    except Error as e:
        print(f"Erro ao atualizar estrutura das tabelas de produtos: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def add_price_tracking_columns():
    """Adiciona colunas necessárias para rastreamento de alterações de preços"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="als32@#nss",
            database="midnight"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            print("Adicionando colunas para rastreamento de alterações de preços...")
            
            # Adicionar colunas na tabela produtos para rastrear preços anteriores
            produtos_columns = [
                ("preco_anterior", "DECIMAL(10,2) DEFAULT NULL COMMENT 'Preço anterior do produto'"),
                ("data_atualizacao", "DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT 'Data da última atualização'"),
                ("custo_materiais", "DECIMAL(10,2) DEFAULT 0.00 COMMENT 'Custo total dos materiais'"),
                ("custo_etapas", "DECIMAL(10,2) DEFAULT 0.00 COMMENT 'Custo total das etapas'"),
                ("custo_total", "DECIMAL(10,2) DEFAULT 0.00 COMMENT 'Custo total do produto'")
            ]
            
            for column_name, column_definition in produtos_columns:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = 'midnight' 
                    AND TABLE_NAME = 'produtos' 
                    AND COLUMN_NAME = %s
                """, (column_name,))
                
                if cursor.fetchone()[0] == 0:
                    cursor.execute(f"ALTER TABLE produtos ADD COLUMN {column_name} {column_definition}")
                    print(f"Coluna '{column_name}' adicionada à tabela 'produtos' com sucesso!")
            
            # Adicionar colunas na tabela maquinas para rastrear alterações
            maquinas_columns = [
                ("data_atualizacao", "DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT 'Data da última atualização'"),
                ("custo_anterior", "DECIMAL(10,2) DEFAULT NULL COMMENT 'Custo anterior por hora'")
            ]
            
            for column_name, column_definition in maquinas_columns:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = 'midnight' 
                    AND TABLE_NAME = 'maquinas' 
                    AND COLUMN_NAME = %s
                """, (column_name,))
                
                if cursor.fetchone()[0] == 0:
                    cursor.execute(f"ALTER TABLE maquinas ADD COLUMN {column_name} {column_definition}")
                    print(f"Coluna '{column_name}' adicionada à tabela 'maquinas' com sucesso!")
            
            # Adicionar colunas na tabela entradas_estoque para rastrear mudanças de custo
            entradas_columns = [
                ("custo_anterior", "DECIMAL(10,2) DEFAULT NULL COMMENT 'Custo anterior do material'"),
                ("variacao_percentual", "DECIMAL(5,2) DEFAULT NULL COMMENT 'Variação percentual do custo'"),
                ("impacto_produtos", "TEXT DEFAULT NULL COMMENT 'JSON com produtos afetados'")
            ]
            
            for column_name, column_definition in entradas_columns:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = 'midnight' 
                    AND TABLE_NAME = 'entradas_estoque' 
                    AND COLUMN_NAME = %s
                """, (column_name,))
                
                if cursor.fetchone()[0] == 0:
                    cursor.execute(f"ALTER TABLE entradas_estoque ADD COLUMN {column_name} {column_definition}")
                    print(f"Coluna '{column_name}' adicionada à tabela 'entradas_estoque' com sucesso!")
            
            # Criar tabela para histórico de alterações de preços
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historico_alteracoes_precos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    tipo_item ENUM('material', 'maquina', 'produto') NOT NULL,
                    item_id INT NOT NULL,
                    item_nome VARCHAR(255) NOT NULL,
                    campo_alterado VARCHAR(100) NOT NULL,
                    valor_anterior DECIMAL(10,2) DEFAULT NULL,
                    valor_novo DECIMAL(10,2) NOT NULL,
                    variacao_percentual DECIMAL(5,2) DEFAULT NULL,
                    motivo TEXT DEFAULT NULL,
                    usuario_id INT DEFAULT NULL,
                    data_alteracao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    produtos_impactados TEXT DEFAULT NULL COMMENT 'JSON com lista de produtos impactados',
                    INDEX idx_tipo_item (tipo_item, item_id),
                    INDEX idx_data_alteracao (data_alteracao),
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("Tabela 'historico_alteracoes_precos' criada com sucesso!")
            
            connection.commit()
            print("Todas as colunas para rastreamento de preços foram adicionadas com sucesso!")
                
    except Error as e:
        print(f"Erro ao adicionar colunas de rastreamento de preços: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def create_price_history_tables():
    """Cria tabelas para histórico de alterações de custos de máquinas e materiais"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="als32@#nss",
            database="midnight"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Criar tabela para histórico de alterações de custos de máquinas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historico_custos_maquinas (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    maquina_id INT NOT NULL,
                    hora_maquina_anterior DECIMAL(10,2),
                    hora_maquina_nova DECIMAL(10,2),
                    metros_quadrados_anterior DECIMAL(10,2),
                    metros_quadrados_nova DECIMAL(10,2),
                    data_alteracao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    usuario_responsavel VARCHAR(255),
                    observacoes TEXT,
                    FOREIGN KEY (maquina_id) REFERENCES maquinas(id) ON DELETE CASCADE,
                    INDEX idx_maquina_data (maquina_id, data_alteracao)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("Tabela 'historico_custos_maquinas' criada com sucesso!")
            
            # Criar tabela para rastreamento de alterações de custos de materiais (complementar)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historico_custos_materiais (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    material_id INT NOT NULL,
                    custo_anterior DECIMAL(10,2),
                    custo_novo DECIMAL(10,2),
                    fonte_alteracao ENUM('entrada_estoque', 'ajuste_manual', 'recalculo_automatico') DEFAULT 'entrada_estoque',
                    entrada_estoque_id INT NULL,
                    data_alteracao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    usuario_responsavel VARCHAR(255),
                    observacoes TEXT,
                    FOREIGN KEY (material_id) REFERENCES itens_estoque(id) ON DELETE CASCADE,
                    FOREIGN KEY (entrada_estoque_id) REFERENCES entradas_estoque(id) ON DELETE SET NULL,
                    INDEX idx_material_data (material_id, data_alteracao)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("Tabela 'historico_custos_materiais' criada com sucesso!")
            
            connection.commit()
                
    except Error as e:
        print(f"Erro ao criar tabelas de histórico de custos: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def create_produtos_anexos_table():
    """Cria a tabela produtos_anexos para armazenar arquivos anexados aos produtos"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="als32@#nss",
            database="midnight"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Criar tabela produtos_anexos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS produtos_anexos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    produto_id INT NOT NULL,
                    nome_arquivo VARCHAR(255) NOT NULL,
                    nome_original VARCHAR(255) NOT NULL,
                    caminho_arquivo VARCHAR(500) NOT NULL,
                    tipo_arquivo VARCHAR(100) NOT NULL,
                    tamanho_arquivo BIGINT NOT NULL,
                    descricao TEXT,
                    data_upload DATETIME DEFAULT CURRENT_TIMESTAMP,
                    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE,
                    INDEX idx_produto_id (produto_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("Tabela 'produtos_anexos' criada com sucesso!")
            connection.commit()
                
    except Error as e:
        print(f"Erro ao criar tabela produtos_anexos: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def add_blob_support_to_produtos_anexos():
    """Adiciona suporte a BLOB para armazenar arquivos de até 4GB na tabela produtos_anexos"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="als32@#nss",
            database="midnight"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            print("Configurando MySQL para suportar arquivos de até 4GB...")
            
            # 1. Configurar max_allowed_packet para 4GB (4294967296 bytes)
            cursor.execute("SET GLOBAL max_allowed_packet = 4294967296")
            print("max_allowed_packet configurado para 4GB")
            
            # 2. Verificar se a coluna conteudo_arquivo já existe
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'midnight' 
                AND TABLE_NAME = 'produtos_anexos' 
                AND COLUMN_NAME = 'conteudo_arquivo'
            """)
            
            if cursor.fetchone()[0] == 0:
                # 3. Adicionar coluna LONGBLOB para armazenar o conteúdo do arquivo
                cursor.execute("""
                    ALTER TABLE produtos_anexos 
                    ADD COLUMN conteudo_arquivo LONGBLOB 
                    COMMENT 'Conteúdo do arquivo (até 4GB)' 
                    AFTER caminho_arquivo
                """)
                print("Coluna 'conteudo_arquivo' (LONGBLOB) adicionada com sucesso!")
            else:
                print("Coluna 'conteudo_arquivo' já existe")
            
            # 4. Verificar se a coluna armazenar_em_blob já existe
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'midnight' 
                AND TABLE_NAME = 'produtos_anexos' 
                AND COLUMN_NAME = 'armazenar_em_blob'
            """)
            
            if cursor.fetchone()[0] == 0:
                # 5. Adicionar coluna para controlar se deve armazenar em BLOB ou arquivo
                cursor.execute("""
                    ALTER TABLE produtos_anexos 
                    ADD COLUMN armazenar_em_blob BOOLEAN DEFAULT FALSE 
                    COMMENT 'TRUE para armazenar em BLOB, FALSE para arquivo físico' 
                    AFTER conteudo_arquivo
                """)
                print("Coluna 'armazenar_em_blob' adicionada com sucesso!")
            else:
                print("Coluna 'armazenar_em_blob' já existe")
            
            # 6. Alterar o campo caminho_arquivo para permitir NULL (quando usar BLOB)
            cursor.execute("""
                ALTER TABLE produtos_anexos 
                MODIFY COLUMN caminho_arquivo VARCHAR(500) NULL 
                COMMENT 'Caminho do arquivo (NULL quando armazenado em BLOB)'
            """)
            print("Campo 'caminho_arquivo' modificado para permitir NULL")
            
            # 7. Adicionar índice para melhorar performance em consultas por produto
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.STATISTICS 
                WHERE TABLE_SCHEMA = 'midnight' 
                AND TABLE_NAME = 'produtos_anexos' 
                AND INDEX_NAME = 'idx_produto_blob'
            """)
            
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    CREATE INDEX idx_produto_blob ON produtos_anexos(produto_id, armazenar_em_blob)
                """)
                print("Índice 'idx_produto_blob' criado com sucesso!")
            else:
                print("Índice 'idx_produto_blob' já existe")
            
            connection.commit()
            print("Suporte a BLOB para arquivos de até 4GB configurado com sucesso!")
            
            # 8. Mostrar informações sobre os tipos de BLOB disponíveis
            print("\nTipos de BLOB disponíveis:")
            print("- TINYBLOB: até 255 bytes")
            print("- BLOB: até 65KB")
            print("- MEDIUMBLOB: até 16MB")
            print("- LONGBLOB: até 4GB (escolhido)")
                
    except Error as e:
        print(f"Erro ao adicionar suporte a BLOB: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def optimize_produtos_anexos_for_large_files():
    """Otimiza a tabela produtos_anexos para melhor performance com arquivos grandes"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="als32@#nss",
            database="midnight"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            print("Otimizando tabela produtos_anexos para arquivos grandes...")
            
            # 1. Configurar engine InnoDB com ROW_FORMAT=DYNAMIC para LONGBLOB
            cursor.execute("""
                ALTER TABLE produtos_anexos 
                ENGINE=InnoDB 
                ROW_FORMAT=DYNAMIC 
                COMMENT='Tabela otimizada para arquivos de até 4GB'
            """)
            print("Engine e formato de linha otimizados")
            
            # 2. Configurar innodb_log_file_size (informativo)
            cursor.execute("SHOW VARIABLES LIKE 'innodb_log_file_size'")
            log_size = cursor.fetchone()
            print(f"innodb_log_file_size atual: {log_size[1]} bytes")
            
            # 3. Verificar configurações importantes
            important_vars = [
                'innodb_buffer_pool_size',
                'tmp_table_size',
                'max_heap_table_size'
            ]
            
            print("\nConfigurações importantes do MySQL:")
            for var in important_vars:
                cursor.execute(f"SHOW VARIABLES LIKE '{var}'")
                result = cursor.fetchone()
                if result:
                    print(f"- {result[0]}: {result[1]}")
            
            connection.commit()
            print("\nOtimização concluída!")
                
    except Error as e:
        print(f"Erro ao otimizar tabela: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def fix_produtos_anexos_column_names():
    """Corrige os nomes das colunas da tabela produtos_anexos para alinhar com o código backend"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="als32@#nss",
            database="midnight"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            print("Corrigindo nomes das colunas da tabela produtos_anexos...")
            
            # Verificar se as colunas antigas existem e renomeá-las
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'midnight' 
                AND TABLE_NAME = 'produtos_anexos'
            """)
            
            existing_columns = [row[0] for row in cursor.fetchall()]
            print(f"Colunas existentes: {existing_columns}")
            
            # 1. Renomear conteudo_arquivo para conteudo_blob
            if 'conteudo_arquivo' in existing_columns and 'conteudo_blob' not in existing_columns:
                cursor.execute("""
                    ALTER TABLE produtos_anexos 
                    CHANGE COLUMN conteudo_arquivo conteudo_blob LONGBLOB 
                    COMMENT 'Conteúdo do arquivo em BLOB (até 4GB)'
                """)
                print("Coluna 'conteudo_arquivo' renomeada para 'conteudo_blob'")
            
            # 2. Renomear tamanho_arquivo para tamanho
            if 'tamanho_arquivo' in existing_columns and 'tamanho' not in existing_columns:
                cursor.execute("""
                    ALTER TABLE produtos_anexos 
                    CHANGE COLUMN tamanho_arquivo tamanho BIGINT NOT NULL 
                    COMMENT 'Tamanho do arquivo em bytes'
                """)
                print("Coluna 'tamanho_arquivo' renomeada para 'tamanho'")
            
            # 3. Renomear tipo_arquivo para tipo_mime
            if 'tipo_arquivo' in existing_columns and 'tipo_mime' not in existing_columns:
                cursor.execute("""
                    ALTER TABLE produtos_anexos 
                    CHANGE COLUMN tipo_arquivo tipo_mime VARCHAR(100) NOT NULL 
                    COMMENT 'Tipo MIME do arquivo'
                """)
                print("Coluna 'tipo_arquivo' renomeada para 'tipo_mime'")
            
            # 4. Renomear caminho_arquivo para caminho_fisico
            if 'caminho_arquivo' in existing_columns and 'caminho_fisico' not in existing_columns:
                cursor.execute("""
                    ALTER TABLE produtos_anexos 
                    CHANGE COLUMN caminho_arquivo caminho_fisico VARCHAR(500) NULL 
                    COMMENT 'Caminho físico do arquivo (NULL quando armazenado em BLOB)'
                """)
                print("Coluna 'caminho_arquivo' renomeada para 'caminho_fisico'")
            
            # 5. Adicionar colunas que podem estar faltando
            
            # Verificar se data_upload existe
            if 'data_upload' not in existing_columns:
                cursor.execute("""
                    ALTER TABLE produtos_anexos 
                    ADD COLUMN data_upload DATETIME DEFAULT CURRENT_TIMESTAMP 
                    COMMENT 'Data e hora do upload'
                """)
                print("Coluna 'data_upload' adicionada")
            
            # Verificar se armazenar_em_blob existe
            if 'armazenar_em_blob' not in existing_columns:
                cursor.execute("""
                    ALTER TABLE produtos_anexos 
                    ADD COLUMN armazenar_em_blob BOOLEAN DEFAULT TRUE 
                    COMMENT 'TRUE para armazenar em BLOB, FALSE para arquivo físico'
                """)
                print("Coluna 'armazenar_em_blob' adicionada")
            
            connection.commit()
            print("Nomes das colunas da tabela produtos_anexos corrigidos com sucesso!")
            
            # Mostrar a estrutura final da tabela
            cursor.execute("DESCRIBE produtos_anexos")
            columns = cursor.fetchall()
            print("\nEstrutura final da tabela produtos_anexos:")
            for column in columns:
                print(f"  {column[0]} - {column[1]} - {column[2]} - {column[3]} - {column[4]} - {column[5]}")
                
    except Error as e:
        print(f"Erro ao corrigir nomes das colunas produtos_anexos: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def create_usuarios_table():
    """Cria a tabela usuarios se ela não existir (necessária para foreign keys)"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="als32@#nss",
            database="midnight"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Verificar se a tabela usuarios já existe
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = 'midnight' 
                AND TABLE_NAME = 'usuarios'
            """)
            
            if cursor.fetchone()[0] == 0:
                # Criar tabela usuarios
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS usuarios (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        nome VARCHAR(100) NOT NULL,
                        email VARCHAR(100) NOT NULL UNIQUE,
                        senha VARCHAR(255) NOT NULL,
                        cargo VARCHAR(50) NOT NULL,
                        nivel_de_acesso INT NOT NULL,
                        foto_de_perfil LONGBLOB,
                        status VARCHAR(50) DEFAULT 'active',
                        data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                        data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        CONSTRAINT chk_nivel_acesso CHECK (nivel_de_acesso >= 0 AND nivel_de_acesso <= 5)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                print("Tabela 'usuarios' criada com sucesso!")
                connection.commit()
            else:
                print("Tabela 'usuarios' já existe!")
                
    except Error as e:
        print(f"Erro ao criar tabela usuarios: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def create_orcamentos_table():
    """Cria a tabela orcamentos para armazenar dados dos orçamentos"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="als32@#nss",
            database="midnight"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Criar tabela orcamentos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orcamentos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    numero VARCHAR(50) NOT NULL UNIQUE,
                    data_orcamento DATE NOT NULL,
                    cliente_id INT NOT NULL,
                    vendedor_id INT,
                    condicoes_pagamento VARCHAR(100),
                    parcelas VARCHAR(20),
                    subtotal DECIMAL(10,2) DEFAULT 0.00,
                    desconto DECIMAL(10,2) DEFAULT 0.00,
                    valor_total DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                    custo_total DECIMAL(10,2) DEFAULT 0.00,
                    margem_lucro DECIMAL(5,2) DEFAULT 0.00,
                    lucro_estimado DECIMAL(10,2) DEFAULT 0.00,
                    observacoes TEXT,
                    status VARCHAR(50) DEFAULT 'Pendente',
                    validade_dias INT DEFAULT 30,
                    data_validade DATE,
                    data_aprovacao DATE,
                    aprovado_por INT,
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    criado_por INT,
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE RESTRICT,
                    FOREIGN KEY (vendedor_id) REFERENCES usuarios(id) ON DELETE SET NULL,
                    FOREIGN KEY (aprovado_por) REFERENCES usuarios(id) ON DELETE SET NULL,
                    FOREIGN KEY (criado_por) REFERENCES usuarios(id) ON DELETE SET NULL,
                    INDEX idx_numero (numero),
                    INDEX idx_cliente (cliente_id),
                    INDEX idx_data (data_orcamento),
                    INDEX idx_status (status),
                    INDEX idx_vendedor (vendedor_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("Tabela 'orcamentos' criada com sucesso!")
            
            # Criar tabela orcamentos_itens (para armazenar os itens do orçamento)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orcamentos_itens (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    orcamento_id INT NOT NULL,
                    produto_id INT NOT NULL,
                    quantidade INT NOT NULL DEFAULT 1,
                    preco_unitario DECIMAL(10,2) NOT NULL,
                    custo_unitario DECIMAL(10,2) DEFAULT 0.00,
                    desconto_item DECIMAL(10,2) DEFAULT 0.00,
                    subtotal DECIMAL(10,2) NOT NULL,
                    observacoes_item TEXT,
                    ordem_item INT DEFAULT 1,
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (orcamento_id) REFERENCES orcamentos(id) ON DELETE CASCADE,
                    FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE RESTRICT,
                    INDEX idx_orcamento (orcamento_id),
                    INDEX idx_produto (produto_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("Tabela 'orcamentos_itens' criada com sucesso!")
            
            connection.commit()
                
    except Error as e:
        print(f"Erro ao criar tabelas de orçamentos: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def add_missing_columns_to_orcamentos():
    """Adiciona colunas que podem estar faltantes na tabela orcamentos"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="als32@#nss",
            database="midnight"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Lista de colunas para verificar e adicionar se necessário
            columns_to_check = [
                ('numero_sequencial', 'ADD COLUMN numero_sequencial INT UNIQUE'),
                ('data_aprovacao', 'ADD COLUMN data_aprovacao DATE NULL'),
                ('aprovado_por', 'ADD COLUMN aprovado_por INT NULL'),
                ('margem_lucro', 'ADD COLUMN margem_lucro DECIMAL(5,2) DEFAULT 0.00'),
                ('custo_total', 'ADD COLUMN custo_total DECIMAL(10,2) DEFAULT 0.00'),
                ('lucro_estimado', 'ADD COLUMN lucro_estimado DECIMAL(10,2) DEFAULT 0.00'),
                ('desconto', 'ADD COLUMN desconto DECIMAL(10,2) DEFAULT 0.00'),
                ('subtotal', 'ADD COLUMN subtotal DECIMAL(10,2) DEFAULT 0.00')
            ]
            
            for column_name, alter_statement in columns_to_check:
                # Verificar se a coluna existe
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = 'midnight' 
                    AND TABLE_NAME = 'orcamentos' 
                    AND COLUMN_NAME = %s
                """, (column_name,))
                
                if cursor.fetchone()[0] == 0:
                    try:
                        cursor.execute(f"ALTER TABLE orcamentos {alter_statement}")
                        print(f"Coluna '{column_name}' adicionada à tabela orcamentos!")
                    except Error as e:
                        print(f"Erro ao adicionar coluna '{column_name}': {e}")
            
            # Adicionar foreign keys se necessário
            try:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                    WHERE TABLE_SCHEMA = 'midnight' 
                    AND TABLE_NAME = 'orcamentos' 
                    AND CONSTRAINT_NAME = 'fk_orcamentos_aprovado_por'
                """)
                
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        ALTER TABLE orcamentos 
                        ADD CONSTRAINT fk_orcamentos_aprovado_por 
                        FOREIGN KEY (aprovado_por) REFERENCES usuarios(id) ON DELETE SET NULL
                    """)
                    print("Foreign key 'aprovado_por' adicionada!")
            except Error as e:
                print(f"Foreign key 'aprovado_por' pode já existir ou erro: {e}")
            
            connection.commit()
                
    except Error as e:
        print(f"Erro ao adicionar colunas faltantes aos orçamentos: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def create_kits_tables():
    """Cria as tabelas para o sistema de kits"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="als32@#nss",
            database="midnight"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Criar tabela kits
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS kits (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    codigo VARCHAR(100) NOT NULL UNIQUE,
                    nome VARCHAR(255) NOT NULL,
                    descricao TEXT,
                    status VARCHAR(50) DEFAULT 'Ativo',
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("Tabela 'kits' criada com sucesso!")
            
            # Criar tabela kits_produtos (relação entre kits e produtos)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS kits_produtos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    kit_id INT NOT NULL,
                    produto_id INT NOT NULL,
                    quantidade INT NOT NULL DEFAULT 1,
                    ordem INT DEFAULT NULL,
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (kit_id) REFERENCES kits(id) ON DELETE CASCADE,
                    FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_kit_produto (kit_id, produto_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("Tabela 'kits_produtos' criada com sucesso!")
            
            connection.commit()
                
    except Error as e:
        print(f"Erro ao criar tabelas de kits: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def create_vendas_tables():
    """Criar tabelas para sistema de vendas"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="als32@#nss",
            database="midnight"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Criar tabela vendas
            cursor.execute("""
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
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("Tabela 'vendas' criada com sucesso!")
            
            # Criar tabela vendas_itens
            cursor.execute("""
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
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("Tabela 'vendas_itens' criada com sucesso!")
            
            connection.commit()
            
    except Error as e:
        print(f"Erro ao criar tabelas de vendas: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    print("=== EXECUTANDO MIGRAÇÕES DO BANCO DE DADOS ===")
    create_database()
    create_usuarios_table()  # Criar tabela usuarios primeiro (para foreign keys)
    add_custo_medio_column()
    add_custo_atual_column()
    create_categoria_produtos_table()
    create_produtos_table()
    update_produtos_tables_structure()  # Nova função para atualizar estrutura
    create_maquinas_tables()
    create_ferramentas_table()
    create_etapas_confeccao_table()
    create_tipo_itens_table()
    add_missing_columns_to_itens_estoque()
    update_itens_estoque_to_use_ids()
    add_fabricante_column()
    add_metros_quadrados_por_hora_column()
    fix_motivo_saida_column()
    add_frasco_garrafa_tipo_item()
    convert_volume_to_decimal()  # Convert volume back to DECIMAL(10,3) to allow decimal places
    update_produtos_tables_structure()
    add_price_tracking_columns()  # Nova função para rastreamento de preços
    create_price_history_tables()  # Nova função para tabelas de histórico
    create_produtos_anexos_table()  # Nova função para tabela de anexos de produtos
    add_blob_support_to_produtos_anexos()
    optimize_produtos_anexos_for_large_files()
    fix_produtos_anexos_column_names()
    create_orcamentos_table()  # Criar tabelas de orçamentos
    add_missing_columns_to_orcamentos()  # Adicionar colunas faltantes aos orçamentos
    create_kits_tables()  # Criar tabelas para sistema de kits
    create_vendas_tables()  # Criar tabelas para sistema de vendas
    print("=== MIGRAÇÕES CONCLUÍDAS ===")
