#!/usr/bin/env python3

"""
Script de debug para verificar a estrutura dos orçamentos
"""

from database import Database

def debug_orcamentos():
    print("🔍 Debug dos orçamentos")
    print("=" * 50)
    
    db = Database()
    try:
        # Testar a estrutura da tabela orcamentos
        print("\n📋 Estrutura da tabela orcamentos:")
        db.cursor.execute("DESCRIBE orcamentos")
        colunas_orcamentos = db.cursor.fetchall()
        for coluna in colunas_orcamentos:
            print(f"  - {coluna['Field']}: {coluna['Type']} (NULL: {coluna['Null']})")
        
        # Testar a estrutura da tabela orcamentos_itens
        print("\n📋 Estrutura da tabela orcamentos_itens:")
        db.cursor.execute("DESCRIBE orcamentos_itens")
        colunas_itens = db.cursor.fetchall()
        for coluna in colunas_itens:
            print(f"  - {coluna['Field']}: {coluna['Type']} (NULL: {coluna['Null']})")
        
        # Listar orçamentos existentes
        print("\n📊 Orçamentos existentes:")
        orcamentos = db.listar_orcamentos()
        print(f"Total de orçamentos: {len(orcamentos)}")
        
        for i, orcamento in enumerate(orcamentos[:3]):  # Mostrar apenas os 3 primeiros
            print(f"\nOrçamento {i+1}:")
            print(f"  - ID: {orcamento.get('id')}")
            print(f"  - Número: {orcamento.get('numero')}")
            print(f"  - Cliente: {orcamento.get('cliente_nome')}")
            print(f"  - Valor Total (campo): {orcamento.get('valor_total')}")
            print(f"  - Subtotal (calculado): {orcamento.get('subtotal')}")
            print(f"  - Total (calculado): {orcamento.get('total')}")
            print(f"  - Total de itens: {orcamento.get('total_itens')}")
            
            # Verificar itens do orçamento
            if orcamento.get('id'):
                print(f"  - Itens do orçamento {orcamento.get('id')}:")
                db.cursor.execute("""
                    SELECT produto_nome, quantidade, preco_unitario, preco_total, subtotal, desconto_item
                    FROM orcamentos_itens 
                    WHERE orcamento_id = %s
                """, (orcamento.get('id'),))
                itens = db.cursor.fetchall()
                for item in itens:
                    print(f"    * {item['produto_nome']}: Qtd {item['quantidade']}, "
                          f"Preço Unit: {item['preco_unitario']}, "
                          f"Subtotal: {item['subtotal']}, "
                          f"Total: {item['preco_total']}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_orcamentos()
