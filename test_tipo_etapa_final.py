#!/usr/bin/env python3
"""
Teste simples para verificar se o tipo de etapa está sendo salvo corretamente no banco.
"""

import requests
import json

def test_tipo_etapa_salvo():
    """Testa se o tipo de etapa selecionado pelo usuário está sendo salvo no banco."""
    
    print("=== TESTE: Verificação do tipo de etapa ===")
    
    # URL base da aplicação
    base_url = "http://localhost:5000"
    
    # Criar um produto de teste com etapa específica
    print("\n1. Criando produto de teste com tipo de etapa específico...")
    
    produto_teste = {
        "nome": "Produto Teste Tipo Etapa",
        "codigo": "TEST_TIPO_001",
        "categoria": "Teste",
        "preco": 100.0,
        "margem": 30,
        "descricao": "Produto para testar tipo de etapa",
        "custoMateriais": 30.0,
        "custoEtapas": 40.0,
        "materiais": [],
        "etapas": [
            {
                "nome": "Etapa de Acabamento",
                "tipo": "Acabamento",  # Tipo específico selecionado pelo usuário
                "equipamento_id": None,  # Sem equipamento
                "equipamento_nome": "Mão de obra",
                "tempo_estimado": "00:30:00",
                "custo_estimado": 25.0
            },
            {
                "nome": "Etapa de Processamento",
                "tipo": "Processamento",  # Tipo específico selecionado pelo usuário
                "equipamento_id": None,  # Sem equipamento
                "equipamento_nome": "Mão de obra",
                "tempo_estimado": "00:45:00",
                "custo_estimado": 35.0
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/produtos",
            json=produto_teste,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 201:
            result = response.json()
            if result.get('status') == 'success':
                produto_id = result.get('produto_id')
                print(f"   ✅ Produto criado com sucesso! ID: {produto_id}")
                
                # Verificar como foi salvo no banco
                print("\n2. Verificando como as etapas foram salvas...")
                
                response_get = requests.get(f"{base_url}/api/produtos/{produto_id}")
                if response_get.status_code == 200:
                    produto_data = response_get.json()
                    if produto_data.get('status') == 'success':
                        produto = produto_data['produto']
                        etapas = produto.get('etapas', [])
                        
                        print(f"   Produto encontrado: {produto['nome']}")
                        print(f"   Número de etapas: {len(etapas)}")
                        
                        sucesso = True
                        for i, etapa in enumerate(etapas):
                            print(f"\n   Etapa {i+1}: {etapa['nome']}")
                            print(f"   - Tipo salvo: '{etapa.get('tipo', 'N/A')}'")
                            
                            # Verificar se o tipo está correto
                            if etapa['nome'] == "Etapa de Acabamento":
                                if etapa.get('tipo') == 'Acabamento':
                                    print(f"   ✅ Tipo 'Acabamento' salvo corretamente!")
                                else:
                                    print(f"   ❌ Tipo incorreto! Esperado 'Acabamento', obtido '{etapa.get('tipo')}'")
                                    sucesso = False
                            
                            elif etapa['nome'] == "Etapa de Processamento":
                                if etapa.get('tipo') == 'Processamento':
                                    print(f"   ✅ Tipo 'Processamento' salvo corretamente!")
                                else:
                                    print(f"   ❌ Tipo incorreto! Esperado 'Processamento', obtido '{etapa.get('tipo')}'")
                                    sucesso = False
                        
                        if sucesso:
                            print("\n✅ Teste passou! Tipos de etapa salvos corretamente.")
                        else:
                            print("\n❌ Teste falhou! Tipos de etapa não foram salvos corretamente.")
                        
                        return sucesso
                    else:
                        print(f"   ❌ Erro ao buscar produto: {produto_data}")
                        return False
                else:
                    print(f"   ❌ Erro ao buscar produto: {response_get.status_code}")
                    return False
            else:
                print(f"   ❌ Erro ao criar produto: {result}")
                return False
        else:
            print(f"   ❌ Erro na requisição: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
        return False

if __name__ == "__main__":
    success = test_tipo_etapa_salvo()
    if success:
        print("\n🎉 Teste de tipo de etapa passou!")
    else:
        print("\n❌ Teste de tipo de etapa falhou!")
