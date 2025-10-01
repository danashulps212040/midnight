#!/usr/bin/env python3
"""
Teste para verificar se o frontend está usando o custo_etapas correto da API
"""
import requests
import json

# Produto que sabemos ter problemas com custo de etapas
produto_id = 1

try:
    # Testar a API que o frontend chama
    response = requests.get(f'http://localhost:5000/api/produtos/{produto_id}/detalhes-calculo')
    
    if response.status_code == 200:
        data = response.json()
        print("=== Dados retornados pela API ===")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # Verificar especificamente o custo das etapas
        custo_etapas = data.get('custo_etapas', 0)
        print(f"\n=== CUSTO ETAPAS ===")
        print(f"Valor retornado pela API: R$ {custo_etapas:.2f}")
        
        # Simular o cálculo que o frontend faz
        custo_materiais = sum(material.get('custo_unitario_novo', material.get('custo_unitario', 0)) * 
                            material.get('quantidade_necessaria', 0) 
                            for material in data.get('materiais', []))
        
        custo_total = custo_materiais + custo_etapas
        margem_lucro = data.get('produto', {}).get('margem_lucro', 0)
        preco_final = custo_total * (1 + margem_lucro / 100)
        
        print(f"\n=== SIMULAÇÃO DO CÁLCULO FRONTEND ===")
        print(f"Custo materiais: R$ {custo_materiais:.2f}")
        print(f"Custo etapas: R$ {custo_etapas:.2f}")
        print(f"Custo total: R$ {custo_total:.2f}")
        print(f"Margem de lucro: {margem_lucro}%")
        print(f"Preço final: R$ {preco_final:.2f}")
        
    else:
        print(f"Erro na API: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"Erro: {e}")
