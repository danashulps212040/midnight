#!/usr/bin/env python3
"""
Script para criar uma nova entrada de estoque e testar a atualização de preços
"""

from database import Database
import requests
import json

def main():
    print("=== TESTE: CRIANDO ENTRADA DE ESTOQUE E TESTANDO ATUALIZAÇÃO ===\n")
    
    try:
        db = Database()
        
        # 1. Verificar material existente (papel A4)
        print("1. Verificando material existente:")
        db.cursor.execute("SELECT id, nome, custo_atual FROM itens_estoque WHERE nome LIKE '%papel%'")
        materiais = db.cursor.fetchall()
        
        if not materiais:
            print("❌ Nenhum material encontrado!")
            return
        
        material = materiais[0]
        print(f"   📋 Material: {material['nome']} (ID: {material['id']})")
        print(f"   💰 Custo atual: R$ {material['custo_atual'] or 0:.2f}")
        
        # 2. Criar nova entrada com custo diferente
        novo_custo = 32.50
        print(f"\n2. Criando entrada de estoque com custo R$ {novo_custo:.2f}:")
        
        resultado = db.criar_entrada_estoque(
            item_id=material['id'],
            quantidade=50,
            data_entrada='2025-07-02',
            fornecedor='Fornecedor Teste',
            nota_fiscal='NF-12345',
            custo_unitario=novo_custo,
            data_validade=None,
            lote='LOTE-TEST',
            localizacao='Estoque A',
            observacoes='Teste de atualização de preços'
        )
        
        if 'sucesso' in resultado:
            print(f"   ✅ Entrada criada com sucesso! ID: {resultado['id']}")
        else:
            print(f"   ❌ Erro ao criar entrada: {resultado}")
            return
        
        # 3. Verificar se o custo foi atualizado
        print("\n3. Verificando se o custo foi atualizado:")
        db.cursor.execute("SELECT custo_atual FROM itens_estoque WHERE id = %s", (material['id'],))
        custo_atualizado = db.cursor.fetchone()
        print(f"   💰 Novo custo atual: R$ {custo_atualizado['custo_atual'] or 0:.2f}")
        
        # 4. Verificar alterações de preços
        print("\n4. Verificando alterações de preços:")
        response = requests.post(
            'http://localhost:5000/api/produtos/verificar-alteracoes-precos',
            json={},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            produtos_afetados = data.get('produtos_afetados', [])
            
            if produtos_afetados:
                produto_teste = produtos_afetados[0]
                print(f"   ✅ Alteração detectada!")
                print(f"   📦 Produto: {produto_teste['nome']}")
                print(f"   💰 Preço atual: R$ {produto_teste['preco_atual']:.2f}")
                print(f"   💰 Novo preço: R$ {produto_teste['novo_preco']:.2f}")
                print(f"   📈 Variação: {produto_teste['variacao_percentual']:.2f}%")
                
                # 5. Verificar produto antes da atualização
                print("\n5. Verificando produto antes da atualização:")
                produto_query = """
                    SELECT p.id, p.nome, p.preco, p.custo_materiais, p.custo_etapas,
                           pm.material_id, pm.custo_unitario, pm.subtotal, pm.quantidade_necessaria
                    FROM produtos p
                    LEFT JOIN produtos_materiais pm ON p.id = pm.produto_id
                    WHERE p.id = %s
                """
                
                db.cursor.execute(produto_query, (produto_teste['id'],))
                dados_antes = db.cursor.fetchall()
                produto_antes = dados_antes[0]
                
                print(f"   📦 Produto: {produto_antes['nome']}")
                print(f"   💰 Preço: R$ {produto_antes['preco']:.2f}")
                print(f"   🔧 Custo materiais: R$ {produto_antes['custo_materiais'] or 0:.2f}")
                print(f"   📋 Custo unitário produtos_materiais: R$ {produto_antes['custo_unitario'] or 0:.2f}")
                print(f"   📋 Subtotal produtos_materiais: R$ {produto_antes['subtotal'] or 0:.2f}")
                
                # 6. Aplicar atualização
                print("\n6. Aplicando atualização de preços:")
                update_data = {
                    'produtos': [{
                        'id': produto_teste['id'],
                        'novo_preco': produto_teste['novo_preco'],
                        'preco_anterior': produto_teste['preco_atual']
                    }]
                }
                
                response = requests.post(
                    'http://localhost:5000/api/precos/atualizar',
                    json=update_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('status') == 'success':
                        print(f"   ✅ Atualização aplicada com sucesso!")
                        
                        # 7. Verificar produto após a atualização
                        print("\n7. Verificando produto após a atualização:")
                        db.cursor.execute(produto_query, (produto_teste['id'],))
                        dados_depois = db.cursor.fetchall()
                        produto_depois = dados_depois[0]
                        
                        print(f"   📦 Produto: {produto_depois['nome']}")
                        print(f"   💰 Preço: R$ {produto_depois['preco']:.2f}")
                        print(f"   🔧 Custo materiais: R$ {produto_depois['custo_materiais'] or 0:.2f}")
                        print(f"   📋 Custo unitário produtos_materiais: R$ {produto_depois['custo_unitario'] or 0:.2f}")
                        print(f"   📋 Subtotal produtos_materiais: R$ {produto_depois['subtotal'] or 0:.2f}")
                        
                        # 8. Comparar os valores
                        print("\n8. Resultado da atualização:")
                        if produto_antes['custo_materiais'] != produto_depois['custo_materiais']:
                            print(f"   ✅ Custo de materiais foi atualizado: R$ {produto_antes['custo_materiais'] or 0:.2f} → R$ {produto_depois['custo_materiais'] or 0:.2f}")
                        else:
                            print(f"   ⚠️  Custo de materiais não foi alterado: R$ {produto_antes['custo_materiais'] or 0:.2f}")
                        
                        if produto_antes['custo_unitario'] != produto_depois['custo_unitario']:
                            print(f"   ✅ Custo unitário foi atualizado: R$ {produto_antes['custo_unitario'] or 0:.2f} → R$ {produto_depois['custo_unitario'] or 0:.2f}")
                        else:
                            print(f"   ⚠️  Custo unitário não foi alterado: R$ {produto_antes['custo_unitario'] or 0:.2f}")
                        
                        if produto_antes['subtotal'] != produto_depois['subtotal']:
                            print(f"   ✅ Subtotal foi atualizado: R$ {produto_antes['subtotal'] or 0:.2f} → R$ {produto_depois['subtotal'] or 0:.2f}")
                        else:
                            print(f"   ⚠️  Subtotal não foi alterado: R$ {produto_antes['subtotal'] or 0:.2f}")
                    else:
                        print(f"   ❌ Erro na atualização: {result.get('message', 'Erro desconhecido')}")
                else:
                    print(f"   ❌ Erro HTTP na atualização: {response.status_code}")
            else:
                print("   ℹ️  Nenhuma alteração de preço detectada")
        else:
            print(f"   ❌ Erro ao verificar alterações: {response.status_code}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
