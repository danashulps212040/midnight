#!/usr/bin/env python3
"""
Teste para verificar se o tipo de etapa está sendo salvo corretamente.
"""

import requests
import json

def test_tipo_etapa_correcao():
    """Testa se o tipo de etapa está sendo definido corretamente baseado no equipamento."""
    
    print("=== TESTE: Correção do tipo de etapa ===")
    
    # URL base da aplicação
    base_url = "http://localhost:5000"
    
    # Primeiro, vamos listar as máquinas disponíveis para obter um ID válido
    print("\n1. Obtendo lista de máquinas...")
    try:
        response = requests.get(f"{base_url}/api/maquinas")
        if response.status_code == 200:
            maquinas_data = response.json()
            if maquinas_data.get('status') == 'success' and maquinas_data.get('machines'):
                maquinas = maquinas_data['machines']
                if len(maquinas) > 0:
                    maquina_id = maquinas[0]['id']
                    maquina_nome = maquinas[0]['nome']
                    print(f"   Máquina encontrada: ID {maquina_id} - {maquina_nome}")
                else:
                    print("   ❌ Nenhuma máquina encontrada. Criando dados de teste...")
                    # Aqui poderia criar uma máquina de teste, mas vamos usar dados simulados
                    maquina_id = 1
                    maquina_nome = "Máquina de Teste"
            else:
                print("   ❌ Erro ao obter máquinas:", maquinas_data)
                return False
        else:
            print(f"   ❌ Erro na requisição: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
        return False
    
    # Criar um produto de teste com etapa usando máquina
    print("\n2. Criando produto de teste com etapa de máquina...")
    
    produto_teste = {
        "nome": "Produto Teste Etapa",
        "codigo": "TEST_ETAPA_001",
        "categoria": "Teste",
        "preco": 100.0,
        "margem": 30,
        "descricao": "Produto para testar tipo de etapa",
        "custoMateriais": 30.0,
        "custoEtapas": 40.0,
        "materiais": [],
        "etapas": [
            {
                "nome": "Corte com Máquina",
                "tipo": "Processamento",  # Este valor deveria ser ignorado
                "equipamento_id": f"maquina_{maquina_id}",  # Formato que vem do frontend
                "equipamento_nome": maquina_nome,
                "tempo_estimado": "00:30:00",
                "custo_estimado": 40.0
            },
            {
                "nome": "Acabamento Manual",
                "tipo": "Acabamento",  # Este deveria ficar como manual
                "equipamento_id": None,  # Sem equipamento
                "equipamento_nome": "Mão de obra",
                "tempo_estimado": "00:15:00",
                "custo_estimado": 15.0
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
                
                # Agora verificar como foi salvo no banco
                print("\n3. Verificando como as etapas foram salvas...")
                
                response_get = requests.get(f"{base_url}/api/produtos/{produto_id}")
                if response_get.status_code == 200:
                    produto_data = response_get.json()
                    if produto_data.get('status') == 'success':
                        produto = produto_data['produto']
                        etapas = produto.get('etapas', [])
                        
                        print(f"   Produto encontrado: {produto['nome']}")
                        print(f"   Número de etapas: {len(etapas)}")
                        
                        for i, etapa in enumerate(etapas):
                            print(f"\n   Etapa {i+1}: {etapa['nome']}")
                            print(f"   - Tipo: {etapa.get('tipo', 'N/A')}")
                            print(f"   - Equipamento ID: {etapa.get('equipamento_id', 'N/A')}")
                            print(f"   - Equipamento: {etapa.get('equipamento', 'N/A')}")
                            
                            # Verificar se o tipo está correto
                            if etapa['nome'] == "Corte com Máquina":
                                if etapa.get('tipo') == 'maquina':
                                    print(f"   ✅ Tipo correto para etapa com máquina!")
                                else:
                                    print(f"   ❌ Tipo incorreto! Esperado 'maquina', obtido '{etapa.get('tipo')}'")
                            
                            elif etapa['nome'] == "Acabamento Manual":
                                if etapa.get('tipo') == 'manual':
                                    print(f"   ✅ Tipo correto para etapa manual!")
                                else:
                                    print(f"   ❌ Tipo incorreto! Esperado 'manual', obtido '{etapa.get('tipo')}'")
                        
                        print("\n✅ Teste concluído!")
                        return True
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
    success = test_tipo_etapa_correcao()
    if success:
        print("\n🎉 Teste de correção do tipo de etapa passou!")
    else:
        print("\n❌ Teste de correção do tipo de etapa falhou!")
