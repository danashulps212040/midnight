#!/usr/bin/env python3
"""
Análise final do produto 63 - Verificação de por que aparece na lista de atualização
"""

from database import Database
import json
from datetime import datetime

def main():
    db = Database()
    
    print("=" * 60)
    print("ANÁLISE FINAL - PRODUTO 63: Fachada ACM 100x100")
    print("=" * 60)
    
    # 1. Dados básicos do produto
    produto = db.buscar_produto_por_id(63)
    print(f"\n1. DADOS DO PRODUTO:")
    print(f"   Nome: {produto.get('nome')}")
    print(f"   Preço atual: R$ {produto.get('preco')}")
    print(f"   Margem lucro: {produto.get('margem_lucro', 0)}%")
    print(f"   Data criação: {produto.get('data_criacao')}")
    print(f"   Data atualização: {produto.get('data_atualizacao')}")
    
    # 2. Materiais e seus custos
    print(f"\n2. MATERIAIS DO PRODUTO:")
    db.cursor.execute('''
        SELECT pm.material_id, ie.nome, ie.custo_atual, ie.custo_medio, 
               pm.quantidade_necessaria, pm.area_utilizada
        FROM produtos_materiais pm
        JOIN itens_estoque ie ON pm.material_id = ie.id
        WHERE pm.produto_id = 63
    ''')
    materiais = db.cursor.fetchall()
    
    for material in materiais:
        custo_usado = material['custo_atual'] or material['custo_medio'] or 0
        print(f"   - {material['nome']} (ID: {material['material_id']})")
        print(f"     Custo atual: R$ {material['custo_atual']}")
        print(f"     Custo médio: R$ {material['custo_medio']}")
        print(f"     Custo usado: R$ {custo_usado}")
        print(f"     Quantidade: {material['quantidade_necessaria']}")
        print(f"     Área utilizada: {material['area_utilizada']}")
    
    # 3. Cálculo atual de custos
    print(f"\n3. CÁLCULO DE CUSTOS:")
    custo_materiais = db._calcular_custo_materiais_produto(63)
    custo_etapas = db._calcular_custo_etapas_produto(63)
    custo_total = float(custo_materiais) + float(custo_etapas)
    
    print(f"   Custo materiais: R$ {custo_materiais:.2f}")
    print(f"   Custo etapas: R$ {custo_etapas:.2f}")
    print(f"   Custo total: R$ {custo_total:.2f}")
    
    # 4. Preço com margem
    margem = float(produto.get('margem_lucro', 0))
    preco_calculado = custo_total * (1 + margem / 100)
    preco_atual = float(produto.get('preco', 0))
    
    print(f"\n4. ANÁLISE DE PREÇOS:")
    print(f"   Preço atual: R$ {preco_atual:.2f}")
    print(f"   Preço calculado (margem {margem}%): R$ {preco_calculado:.2f}")
    print(f"   Diferença: R$ {preco_calculado - preco_atual:.2f}")
    
    # 5. Variação percentual
    if preco_atual > 0:
        variacao = ((preco_calculado - preco_atual) / preco_atual) * 100
        print(f"   Variação: {variacao:.2f}%")
        print(f"   Variação absoluta: {abs(variacao):.2f}%")
        print(f"   Passa threshold de 1%? {abs(variacao) > 1.0}")
    
    # 6. Verificar por que está na lista
    print(f"\n5. DIAGNÓSTICO:")
    if abs(variacao) > 1.0:
        if variacao > 0:
            print(f"   ✅ PRODUTO PRECISA ATUALIZAÇÃO: Preço deve SUBIR {variacao:.2f}%")
            print(f"   📈 Custos aumentaram, produto está subprecificado")
        else:
            print(f"   ⚠️ PRODUTO PODE SER ATUALIZADO: Preço pode BAIXAR {abs(variacao):.2f}%")
            print(f"   📉 Produto está com margem excessiva ou custos diminuíram")
    else:
        print(f"   ✅ PRODUTO NÃO PRECISA ATUALIZAÇÃO: Variação {variacao:.2f}% é insignificante")
    
    # 7. Simulação com custos médios históricos
    print(f"\n6. SIMULAÇÃO COM CUSTOS MÉDIOS HISTÓRICOS:")
    
    # Simular usando custos médios ao invés de atuais
    alteracoes_historicas = {
        'materiais': [
            {'id': 99, 'nome': 'Chapa de ACM 122x500', 'custo_novo': 1073.94},  # custo_medio
            {'id': 98, 'nome': 'Parafuso Phillips 6x40mm', 'custo_novo': 13.00}   # custo_medio
        ],
        'maquinas': []
    }
    
    custo_materiais_historico = db._calcular_custo_materiais_produto(63, alteracoes_historicas['materiais'])
    custo_total_historico = float(custo_materiais_historico) + float(custo_etapas)
    preco_historico = custo_total_historico * (1 + margem / 100)
    
    print(f"   Com custos médios históricos:")
    print(f"   Custo materiais: R$ {custo_materiais_historico:.2f}")
    print(f"   Custo total: R$ {custo_total_historico:.2f}")
    print(f"   Preço sugerido: R$ {preco_historico:.2f}")
    
    if preco_atual > 0:
        variacao_historica = ((preco_historico - preco_atual) / preco_atual) * 100
        print(f"   Variação vs atual: {variacao_historica:.2f}%")
    
    # 8. Recomendações
    print(f"\n7. RECOMENDAÇÕES:")
    if abs(variacao) > 10:
        print(f"   🚨 AÇÃO URGENTE: Variação muito alta ({variacao:.1f}%)")
    elif abs(variacao) > 5:
        print(f"   ⚠️ REVISAR: Variação significativa ({variacao:.1f}%)")
    elif abs(variacao) > 1:
        print(f"   💡 CONSIDERAR: Variação moderada ({variacao:.1f}%)")
    else:
        print(f"   ✅ OK: Variação mínima ({variacao:.1f}%)")
    
    if variacao < 0:
        print(f"   💰 Produto pode ter o preço reduzido para ser mais competitivo")
        print(f"   📊 Ou manter preço atual para maior margem de lucro")
    else:
        print(f"   📈 Produto deve ter o preço aumentado para cobrir custos")
    
    db.close()

if __name__ == "__main__":
    main()
