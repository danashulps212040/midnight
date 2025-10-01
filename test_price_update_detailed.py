#!/usr/bin/env python3
"""
Script de teste para verificar se as atualizações de preços estão atualizando
também os custos detalhados nas tabelas relacionadas
"""

import requests
import json
from database import Database

def main():
    print("=== TESTE DE ATUALIZAÇÃO DETALHADA DE PREÇOS ===\n")
    
    try:
        # 1. Verificar produto existente antes da atualização
        db = Database()
        
        print("1. Verificando produto antes da atualização:")
        produto_query = """
            SELECT p.id, p.nome, p.codigo, p.preco, p.custo_materiais, p.custo_etapas,
                   pm.material_id, pm.custo_unitario, pm.subtotal, pm.quantidade_necessaria,
                   ie.nome as material_nome, ie.custo_atual
            FROM produtos p
            LEFT JOIN produtos_materiais pm ON p.id = pm.produto_id
            LEFT JOIN itens_estoque ie ON pm.material_id = ie.id
            WHERE p.id = 32
        """
        
        db.cursor.execute(produto_query)
        dados_antes = db.cursor.fetchall()
        
        if not dados_antes:
            print("❌ Produto ID 32 não encontrado!")
            return
        
        produto_antes = dados_antes[0]
        print(f"   📦 Produto: {produto_antes['nome']} (ID: {produto_antes['id']})")
        print(f"   💰 Preço atual: R$ {produto_antes['preco']:.2f}")
        print(f"   🔧 Custo materiais: R$ {produto_antes['custo_materiais'] or 0:.2f}")
        print(f"   ⚙️  Custo etapas: R$ {produto_antes['custo_etapas'] or 0:.2f}")
        
        for i, dados in enumerate(dados_antes):
            if dados['material_id']:
                print(f"   📋 Material {i+1}: {dados['material_nome']}")
                print(f"      - Custo unitário na produtos_materiais: R$ {dados['custo_unitario'] or 0:.2f}")
                print(f"      - Subtotal na produtos_materiais: R$ {dados['subtotal'] or 0:.2f}")
                print(f"      - Custo atual no estoque: R$ {dados['custo_atual'] or 0:.2f}")
                print(f"      - Quantidade necessária: {dados['quantidade_necessaria'] or 0}")
        
        # 2. Verificar alterações de preços
        print("\n2. Verificando alterações de preços:")
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
                
                # 3. Aplicar atualização
                print("\n3. Aplicando atualização de preços:")
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
                        print(f"   📊 Produtos atualizados: {result.get('atualizados', 0)}")
                        
                        # 4. Verificar produto após a atualização
                        print("\n4. Verificando produto após a atualização:")
                        db.cursor.execute(produto_query)
                        dados_depois = db.cursor.fetchall()
                        
                        produto_depois = dados_depois[0]
                        print(f"   📦 Produto: {produto_depois['nome']} (ID: {produto_depois['id']})")
                        print(f"   💰 Preço atualizado: R$ {produto_depois['preco']:.2f}")
                        print(f"   🔧 Custo materiais atualizado: R$ {produto_depois['custo_materiais'] or 0:.2f}")
                        print(f"   ⚙️  Custo etapas atualizado: R$ {produto_depois['custo_etapas'] or 0:.2f}")
                        
                        for i, dados in enumerate(dados_depois):
                            if dados['material_id']:
                                print(f"   📋 Material {i+1}: {dados['material_nome']}")
                                print(f"      - Custo unitário na produtos_materiais: R$ {dados['custo_unitario'] or 0:.2f}")
                                print(f"      - Subtotal na produtos_materiais: R$ {dados['subtotal'] or 0:.2f}")
                                print(f"      - Custo atual no estoque: R$ {dados['custo_atual'] or 0:.2f}")
                        
                        # 5. Comparar os valores
                        print("\n5. Comparação dos valores:")
                        if produto_antes['custo_materiais'] != produto_depois['custo_materiais']:
                            print(f"   ✅ Custo de materiais foi atualizado: R$ {produto_antes['custo_materiais'] or 0:.2f} → R$ {produto_depois['custo_materiais'] or 0:.2f}")
                        else:
                            print(f"   ⚠️  Custo de materiais não foi alterado: R$ {produto_antes['custo_materiais'] or 0:.2f}")
                        
                        # Verificar se os custos unitários foram atualizados
                        for dados_antes_item in dados_antes:
                            if dados_antes_item['material_id']:
                                dados_depois_item = next(
                                    (d for d in dados_depois if d['material_id'] == dados_antes_item['material_id']), 
                                    None
                                )
                                if dados_depois_item:
                                    if dados_antes_item['custo_unitario'] != dados_depois_item['custo_unitario']:
                                        print(f"   ✅ Custo unitário do material {dados_depois_item['material_nome']} foi atualizado: R$ {dados_antes_item['custo_unitario'] or 0:.2f} → R$ {dados_depois_item['custo_unitario'] or 0:.2f}")
                                    if dados_antes_item['subtotal'] != dados_depois_item['subtotal']:
                                        print(f"   ✅ Subtotal do material {dados_depois_item['material_nome']} foi atualizado: R$ {dados_antes_item['subtotal'] or 0:.2f} → R$ {dados_depois_item['subtotal'] or 0:.2f}")
                        
                    else:
                        print(f"   ❌ Erro na atualização: {result.get('message', 'Erro desconhecido')}")
                else:
                    print(f"   ❌ Erro HTTP na atualização: {response.status_code}")
                    print(f"   📄 Resposta: {response.text}")
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
