#!/usr/bin/env python3
"""
Script para criar uma entrada de estoque com custo diferente e testar a atualização
"""

from database import Database
import requests
import json

def main():
    print("=== TESTE: CRIANDO ENTRADA COM CUSTO DIFERENTE ===\n")
    
    try:
        db = Database()
        
        # 1. Verificar estado atual
        print("1. Estado atual do produto:")
        produto_query = """
            SELECT p.id, p.nome, p.preco, p.custo_materiais, p.custo_etapas,
                   pm.material_id, pm.custo_unitario, pm.subtotal, pm.quantidade_necessaria,
                   ie.nome as material_nome, ie.custo_atual
            FROM produtos p
            LEFT JOIN produtos_materiais pm ON p.id = pm.produto_id
            LEFT JOIN itens_estoque ie ON pm.material_id = ie.id
            WHERE p.id = 32
        """
        
        db.cursor.execute(produto_query)
        dados_antes = db.cursor.fetchall()
        produto_antes = dados_antes[0]
        
        print(f"   📦 Produto: {produto_antes['nome']}")
        print(f"   💰 Preço: R$ {produto_antes['preco']:.2f}")
        print(f"   🔧 Custo materiais: R$ {produto_antes['custo_materiais'] or 0:.2f}")
        print(f"   📋 Material: {produto_antes['material_nome']}")
        print(f"   📋 Custo unitário produtos_materiais: R$ {produto_antes['custo_unitario'] or 0:.2f}")
        print(f"   📋 Custo atual no estoque: R$ {produto_antes['custo_atual'] or 0:.2f}")
        
        # 2. Criar entrada com custo significativamente diferente
        novo_custo = 35.99
        print(f"\n2. Criando entrada de estoque com custo R$ {novo_custo:.2f}:")
        
        resultado = db.criar_entrada_estoque(
            item_id=produto_antes['material_id'],
            quantidade=25,
            data_entrada='2025-07-02',
            fornecedor='Fornecedor Premium',
            nota_fiscal='NF-99999',
            custo_unitario=novo_custo,
            data_validade=None,
            lote='LOTE-PREMIUM',
            localizacao='Estoque A',
            observacoes='Teste de atualização com custo mais alto'
        )
        
        if 'sucesso' in resultado:
            print(f"   ✅ Entrada criada com sucesso! ID: {resultado['id']}")
        else:
            print(f"   ❌ Erro ao criar entrada: {resultado}")
            return
        
        # 3. Verificar novo custo atual
        print("\n3. Verificando novo custo atual:")
        db.cursor.execute("SELECT custo_atual FROM itens_estoque WHERE id = %s", (produto_antes['material_id'],))
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
                
                # 5. Aplicar atualização
                print("\n5. Aplicando atualização de preços:")
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
                        
                        # 6. Verificar estado final
                        print("\n6. Estado final do produto:")
                        db.cursor.execute(produto_query)
                        dados_depois = db.cursor.fetchall()
                        produto_depois = dados_depois[0]
                        
                        print(f"   📦 Produto: {produto_depois['nome']}")
                        print(f"   💰 Preço: R$ {produto_depois['preco']:.2f}")
                        print(f"   🔧 Custo materiais: R$ {produto_depois['custo_materiais'] or 0:.2f}")
                        print(f"   📋 Material: {produto_depois['material_nome']}")
                        print(f"   📋 Custo unitário produtos_materiais: R$ {produto_depois['custo_unitario'] or 0:.2f}")
                        print(f"   📋 Custo atual no estoque: R$ {produto_depois['custo_atual'] or 0:.2f}")
                        
                        # 7. Resumo das alterações
                        print("\n7. Resumo das alterações:")
                        print(f"   📈 Preço: R$ {produto_antes['preco']:.2f} → R$ {produto_depois['preco']:.2f}")
                        print(f"   🔧 Custo materiais: R$ {produto_antes['custo_materiais'] or 0:.2f} → R$ {produto_depois['custo_materiais'] or 0:.2f}")
                        print(f"   📋 Custo unitário: R$ {produto_antes['custo_unitario'] or 0:.2f} → R$ {produto_depois['custo_unitario'] or 0:.2f}")
                        
                        if produto_antes['preco'] != produto_depois['preco']:
                            print("   ✅ Preço foi atualizado corretamente!")
                        if produto_antes['custo_materiais'] != produto_depois['custo_materiais']:
                            print("   ✅ Custo de materiais foi atualizado corretamente!")
                        if produto_antes['custo_unitario'] != produto_depois['custo_unitario']:
                            print("   ✅ Custo unitário foi atualizado corretamente!")
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
