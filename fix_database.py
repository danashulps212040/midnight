import mysql.connector
from mysql.connector import Error

def fix_database():
    try:
        # Conecta ao banco
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='als32@#nss',
            database='midnight'
        )
        cursor = connection.cursor()
        
        print("Limpando dados corrompidos...")
        
        # Remove todos os registros existentes
        cursor.execute("DELETE FROM itens_estoque")
        connection.commit()
        print("Dados antigos removidos.")
        
        # Insere dados válidos de teste
        insert_sql = """
        INSERT INTO itens_estoque (nome, codigo, categoria, cor, quantidade_inicial, quantidade_atual, estoque_minimo, unidade_medida, fornecedor, localizacao_estoque, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        test_items = [
            ('Parafuso Phillips 6x40mm', 'PAR001', 'Fixação', 'Prateado', 100, 100, 20, 'UN', 'Fornecedor ABC', 'Estoque A', 'Ativo'),
            ('Tinta Acrílica Branca', 'TIN001', 'Tintas', 'Branco', 50, 50, 10, 'LT', 'Tintas XYZ', 'Estoque B', 'Ativo'),
            ('Cabo Elétrico 2.5mm', 'CAB001', 'Elétrica', 'Azul', 200, 200, 50, 'MT', 'Elétrica 123', 'Estoque C', 'Ativo')
        ]
        
        for item in test_items:
            cursor.execute(insert_sql, item)
        
        connection.commit()
        print(f"Inseridos {len(test_items)} itens de teste.")
        
        # Verifica os dados inseridos
        cursor.execute("SELECT id, nome, codigo FROM itens_estoque")
        items = cursor.fetchall()
        print("\nItens inseridos:")
        for item in items:
            print(f"  ID: {item[0]}, Nome: {item[1]}, Código: {item[2]}")
        
        cursor.close()
        connection.close()
        print("\nBanco de dados corrigido com sucesso!")
        
    except Error as e:
        print(f"Erro ao corrigir banco: {e}")

if __name__ == "__main__":
    fix_database()