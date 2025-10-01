#!/usr/bin/env python3
"""
Script para debugar o cálculo de custos das etapas
"""

import requests
import json

def test_detalhes_calculo():
    """
    Testa a API /api/produtos/38/detalhes-calculo
    """
    url = 'http://localhost:8000/api/produtos/43/detalhes-calculo'
    
    try:
        print("🧪 Testando API de detalhes de cálculo do produto...")
        print(f"URL: {url}")
        print("-" * 60)
        
        response = requests.get(url)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Resposta recebida com sucesso!")
            
            # Verificar estrutura da resposta
            print(f"📊 Custo das etapas: R$ {data.get('custo_etapas', 0):.2f}")
            
            produto = data.get('produto', {})
            print(f"📋 Produto: {produto.get('nome')} (ID: {produto.get('id')})")
            
            materiais = data.get('materiais', [])
            print(f"🧱 Materiais: {len(materiais)} item(s)")
            
            for material in materiais:
                custo_atual = material.get('custo_unitario', 0)
                custo_novo = material.get('custo_unitario_novo')
                print(f"  - {material.get('nome')}: R$ {custo_atual:.2f}" + 
                      (f" → R$ {custo_novo:.2f}" if custo_novo else ""))
            
            print(f"\n📄 Resposta completa:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
        else:
            print(f"❌ Erro na requisição: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão. Certifique-se de que o servidor Flask está rodando na porta 8000")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_detalhes_calculo()
