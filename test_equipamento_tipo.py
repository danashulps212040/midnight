#!/usr/bin/env python3
"""
Teste para verificar se o equipamento_tipo está sendo gravado corretamente na tabela produtos_etapas
"""

from database import Database

def test_equipamento_tipo():
    """Testa inserção de etapa com diferentes tipos de equipamento"""
    db = Database()
    
    try:
        # Primeiro, inserir um produto de teste
        produto_data = {
            'nome': 'Produto Teste Equipamento',
            'codigo': 'TEST-EQ-001',
            'categoria': 'Teste',
            'preco': 100.0,
            'margem': 0,
            'descricao': 'Produto para testar tipos de equipamento',
            'especificacoes': '',
            'custo_materiais': 0,
            'custo_etapas': 0
        }
        
        produto_id = db.inserir_produto(produto_data)
        print(f"✅ Produto de teste criado com ID: {produto_id}")
        
        # Teste 1: Etapa com máquina (formato maquina_X)
        etapa_maquina = {
            'produto_id': produto_id,
            'nome': 'Etapa com Máquina',
            'tipo': 'Processamento',
            'equipamento_id': 'maquina_1',  # Formato que vem do frontend
            'equipamento': 'Máquina Teste',
            'material_id': None,
            'material': '',
            'tempo_estimado': '01:00:00',
            'custo': 50.0
        }
        
        etapa_id_maquina = db.inserir_etapa_produto(etapa_maquina)
        print(f"✅ Etapa com máquina criada com ID: {etapa_id_maquina}")
        
        # Teste 2: Etapa com ferramenta (formato ferramenta_X)
        etapa_ferramenta = {
            'produto_id': produto_id,
            'nome': 'Etapa com Ferramenta',
            'tipo': 'Acabamento',
            'equipamento_id': 'ferramenta_1',  # Formato que vem do frontend
            'equipamento': 'Ferramenta Teste',
            'material_id': None,
            'material': '',
            'tempo_estimado': '00:30:00',
            'custo': 10.0
        }
        
        etapa_id_ferramenta = db.inserir_etapa_produto(etapa_ferramenta)
        print(f"✅ Etapa com ferramenta criada com ID: {etapa_id_ferramenta}")
        
        # Teste 3: Etapa manual (sem equipamento)
        etapa_manual = {
            'produto_id': produto_id,
            'nome': 'Etapa Manual',
            'tipo': 'Montagem',
            'equipamento_id': None,
            'equipamento': '',
            'material_id': None,
            'material': '',
            'tempo_estimado': '00:15:00',
            'custo': 5.0
        }
        
        etapa_id_manual = db.inserir_etapa_produto(etapa_manual)
        print(f"✅ Etapa manual criada com ID: {etapa_id_manual}")
        
        # Verificar os resultados no banco
        print("\n📋 Verificando os tipos de equipamento salvos no banco:")
        db.cursor.execute("""
            SELECT id, nome, equipamento_tipo, equipamento_id, equipamento_nome 
            FROM produtos_etapas 
            WHERE produto_id = %s
            ORDER BY id
        """, (produto_id,))
        
        etapas = db.cursor.fetchall()
        for etapa in etapas:
            print(f"  🔧 Etapa ID {etapa['id']}: '{etapa['nome']}'")
            print(f"      - Tipo de equipamento: '{etapa['equipamento_tipo']}'")
            print(f"      - ID do equipamento: {etapa['equipamento_id']}")
            print(f"      - Nome do equipamento: '{etapa['equipamento_nome']}'")
            print()
        
        # Limpeza: remover dados de teste
        print("🧹 Limpando dados de teste...")
        db.cursor.execute("DELETE FROM produtos_etapas WHERE produto_id = %s", (produto_id,))
        db.cursor.execute("DELETE FROM produtos WHERE id = %s", (produto_id,))
        db.connection.commit()
        print("✅ Dados de teste removidos")
        
        # Verificar resultados
        tipos_corretos = 0
        for etapa in etapas:
            if etapa['id'] == etapa_id_maquina and etapa['equipamento_tipo'] == 'maquina':
                tipos_corretos += 1
                print("✅ Etapa com máquina: tipo salvo corretamente como 'maquina'")
            elif etapa['id'] == etapa_id_ferramenta and etapa['equipamento_tipo'] == 'ferramenta':
                tipos_corretos += 1
                print("✅ Etapa com ferramenta: tipo salvo corretamente como 'ferramenta'")
            elif etapa['id'] == etapa_id_manual and etapa['equipamento_tipo'] == 'manual':
                tipos_corretos += 1
                print("✅ Etapa manual: tipo salvo corretamente como 'manual'")
            else:
                print(f"❌ Erro: Etapa ID {etapa['id']} com tipo incorreto: '{etapa['equipamento_tipo']}'")
        
        if tipos_corretos == 3:
            print("\n🎉 TESTE PASSOU! Todos os tipos de equipamento foram salvos corretamente!")
            return True
        else:
            print(f"\n❌ TESTE FALHOU! Apenas {tipos_corretos}/3 tipos foram salvos corretamente.")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Testando se os tipos de equipamento estão sendo salvos corretamente...")
    print("=" * 70)
    test_equipamento_tipo()
