#!/usr/bin/env python3
"""
Script para alterar a coluna margem_lucro para suportar valores maiores
"""

from database import Database

def alter_margem_lucro_column():
    db = Database()
    try:
        # Alterar a coluna margem_lucro para permitir valores maiores
        # decimal(8,2) permite valores até 999999.99 (quase 1 milhão por cento)
        query = "ALTER TABLE produtos MODIFY COLUMN margem_lucro DECIMAL(8,2) DEFAULT 0.00"
        
        print("Alterando coluna margem_lucro de DECIMAL(5,2) para DECIMAL(8,2)...")
        db.cursor.execute(query)
        db.connection.commit()
        print("Coluna alterada com sucesso!")
        
        # Verificar a mudança
        describe_query = "DESCRIBE produtos"
        db.cursor.execute(describe_query)
        columns = db.cursor.fetchall()
        
        for column in columns:
            if column['Field'] == 'margem_lucro':
                print(f"Nova estrutura da coluna margem_lucro:")
                print(f"  Tipo: {column['Type']}")
                print(f"  Null: {column['Null']}")
                print(f"  Default: {column['Default']}")
                break
                
    except Exception as e:
        print(f"Erro ao alterar coluna: {e}")
        import traceback
        traceback.print_exc()
        db.connection.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    alter_margem_lucro_column()
