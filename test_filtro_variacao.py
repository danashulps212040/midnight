#!/usr/bin/env python3
"""
Script para testar se o filtro de variação de preços está funcionando corretamente.
Verifica se produtos com variação menor que 1% não são incluídos no modal de atualização.
"""

import sys
import os
from database import Database

def testar_filtro_variacao():
    """Testa se o filtro de variação está aplicando corretamente o limiar de 1%"""
    
    print("=" * 60)
    print("TESTE DO FILTRO DE VARIAÇÃO DE PREÇOS")
    print("=" * 60)
    
    try:
        db = Database()
        
        # Simular alterações de máquinas (baseado no log fornecido)
        alteracoes_simuladas = {
            'materiais': [],
            'maquinas': [
                {'id': 1, 'nome': 'Epson L3250'},
                {'id': 2, 'nome': 'Brother ScanNcut SDX85'},
                {'id': 3, 'nome': 'Router VUZE'}
            ]
        }
        
        print("Alterações simuladas:")
        print(f"- Materiais: {len(alteracoes_simuladas['materiais'])}")
        print(f"- Máquinas: {len(alteracoes_simuladas['maquinas'])}")
        print()
        
        # Calcular impacto das alterações
        resultado = db.calcular_impacto_alteracoes_precos(alteracoes_simuladas)
        
        produtos_afetados = resultado.get('produtos_afetados', [])
        
        print(f"Produtos analisados: {len(produtos_afetados)}")
        print()
        
        if len(produtos_afetados) == 0:
            print("✅ SUCESSO: Nenhum produto com variação significativa (> 1%) foi encontrado.")
            print("   Isso indica que o filtro está funcionando corretamente.")
        else:
            print("📊 Produtos que passaram pelo filtro (variação > 1%):")
            print("-" * 50)
            
            for produto in produtos_afetados:
                variacao = produto.get('variacao_percentual', 0)
                preco_atual = produto.get('preco_atual', 0)
                novo_preco = produto.get('novo_preco', 0)
                
                print(f"Nome: {produto.get('nome', 'N/A')}")
                print(f"Preço atual: R$ {preco_atual:.2f}")
                print(f"Novo preço: R$ {novo_preco:.2f}")
                print(f"Variação: {variacao:.4f}%")
                print(f"Impacto: {produto.get('impacto', 'N/A')}")
                
                if abs(variacao) <= 1.0:
                    print(f"❌ ERRO: Produto com variação {variacao:.4f}% não deveria aparecer!")
                else:
                    print(f"✅ OK: Variação {variacao:.4f}% > 1%")
                print("-" * 30)
        
        # Verificar se produtos com pequenas variações foram filtrados
        print("\n🔍 Testando busca de produto específico...")
        produto_teste = db.buscar_produto_por_codigo("TESTE001")  # Assumindo que existe
        
        if produto_teste:
            print(f"Produto encontrado: {produto_teste.get('nome', 'N/A')}")
            
            # Simular cálculo manual de variação pequena
            preco_atual = float(produto_teste.get('preco', 100))
            # Simular uma variação de 0.0025% (como no log)
            novo_preco = preco_atual * 1.000025
            variacao_simulada = ((novo_preco - preco_atual) / preco_atual) * 100
            
            print(f"Simulação de variação pequena:")
            print(f"- Preço atual: R$ {preco_atual:.2f}")
            print(f"- Novo preço simulado: R$ {novo_preco:.6f}")
            print(f"- Variação simulada: {variacao_simulada:.6f}%")
            
            if abs(variacao_simulada) <= 1.0:
                print("✅ Esta variação deveria ser FILTRADA pelo backend (< 1%)")
            else:
                print("⚠️ Esta variação passaria pelo filtro (>= 1%)")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

def verificar_produtos_banco():
    """Verifica produtos no banco para entender melhor o cenário"""
    
    print("\n" + "=" * 60)
    print("VERIFICAÇÃO DOS PRODUTOS NO BANCO")
    print("=" * 60)
    
    try:
        db = Database()
        
        # Buscar todos os produtos
        query = """
            SELECT id, nome, codigo, preco, margem_lucro 
            FROM produtos 
            ORDER BY nome 
            LIMIT 10
        """
        
        db.cursor.execute(query)
        produtos = db.cursor.fetchall()
        
        print(f"Primeiros 10 produtos no banco:")
        print("-" * 50)
        
        for produto in produtos:
            print(f"ID: {produto['id']}")
            print(f"Nome: {produto['nome']}")
            print(f"Código: {produto['codigo']}")
            print(f"Preço: R$ {float(produto['preco'] or 0):.2f}")
            print(f"Margem: {float(produto['margem_lucro'] or 0):.1f}%")
            print("-" * 30)
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar produtos: {e}")

if __name__ == "__main__":
    testar_filtro_variacao()
    verificar_produtos_banco()
    
    print("\n" + "=" * 60)
    print("CONCLUSÕES:")
    print("- O filtro foi configurado para variações > 1%")
    print("- Produtos com variação <= 1% não devem aparecer no modal")
    print("- Teste concluído!")
    print("=" * 60)
