import mysql.connector
from mysql.connector import Error

def check_database():
    try:
        # Conecta ao banco
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='als32@#nss',
            database='midnight'
        )
        cursor = connection.cursor()
        
        print("Conexão com banco estabelecida com sucesso!")
        
        # Verifica se a tabela existe
        cursor.execute("SHOW TABLES LIKE 'itens_estoque'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("Tabela 'itens_estoque' existe.")
            
            # Verifica a estrutura da tabela
            cursor.execute("DESCRIBE itens_estoque")
            columns = cursor.fetchall()
            print("\nEstrutura da tabela:")
            for column in columns:
                print(f"  {column[0]} - {column[1]}")
            
            # Verifica quantos registros existem
            cursor.execute("SELECT COUNT(*) FROM itens_estoque")
            count = cursor.fetchone()[0]
            print(f"\nNúmero de registros: {count}")
            
            if count > 0:
                cursor.execute("SELECT id, nome, codigo FROM itens_estoque LIMIT 5")
                items = cursor.fetchall()
                print("\nPrimeiros 5 itens:")
                for item in items:
                    print(f"  ID: {item[0]}, Nome: {item[1]}, Código: {item[2]}")
        else:
            print("Tabela 'itens_estoque' NÃO existe!")
            print("Criando tabela...")
            
            create_table_sql = """
            CREATE TABLE itens_estoque (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                codigo VARCHAR(100) UNIQUE NOT NULL,
                categoria VARCHAR(100),
                cor VARCHAR(50),
                quantidade_atual INT DEFAULT 0,
                estoque_minimo INT DEFAULT 0,
                unidade_medida VARCHAR(20),
                fornecedor VARCHAR(255),
                localizacao_estoque VARCHAR(255),
                status VARCHAR(50) DEFAULT 'Ativo',
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            cursor.execute(create_table_sql)
            connection.commit()
            print("Tabela criada com sucesso!")
            
            # Insere um item de teste
            insert_sql = """
            INSERT INTO itens_estoque (nome, codigo, categoria, cor, quantidade_atual, estoque_minimo, unidade_medida, fornecedor, localizacao_estoque)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            test_item = ('Material Teste', 'MT001', 'Categoria Teste', 'Azul', 10, 5, 'UN', 'Fornecedor Teste', 'Estoque A')
            cursor.execute(insert_sql, test_item)
            connection.commit()
            print("Item de teste inserido!")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")

if __name__ == "__main__":
    check_database()