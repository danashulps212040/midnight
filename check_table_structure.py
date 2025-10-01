#!/usr/bin/env python3
"""
Script para verificar a estrutura da tabela produtos
"""

from database import Database

def check_table_structure():
    db = Database()
    try:
        # Verificar estrutura da tabela produtos
        query = "DESCRIBE produtos"
        db.cursor.execute(query)
        columns = db.cursor.fetchall()
        
        print("Estrutura da tabela produtos:")
        print("-" * 50)
        print(f"Resultado: {columns}")
        print(f"Tipo do resultado: {type(columns)}")
        
        if columns:
            print(f"Primeiro item: {columns[0]}")
            print(f"Tipo do primeiro item: {type(columns[0])}")
            
        for i, column in enumerate(columns):
            print(f"Coluna {i}: {column}")
            if hasattr(column, 'keys'):
                print(f"  Chaves: {list(column.keys())}")
            elif isinstance(column, (list, tuple)):
                print(f"  Como lista/tupla: {column}")
                if len(column) >= 6:
                    print(f"  Campo: {column[0]}")
                    print(f"  Tipo: {column[1]}")
                    print(f"  Null: {column[2]}")
                    print(f"  Key: {column[3]}")
                    print(f"  Default: {column[4]}")
                    print(f"  Extra: {column[5]}")
            print("-" * 30)
                
    except Exception as e:
        print(f"Erro ao verificar estrutura: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_table_structure()
