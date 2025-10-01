#!/usr/bin/env python3
"""
Teste para verificar se o sistema de cadastro/edição de produtos com etapas
está funcionando corretamente após a correção do erro KeyError.
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_endpoints():
    """Testa se os endpoints necessários estão funcionando"""
    print("=== Testando Endpoints ===")
    
    # Teste endpoint de máquinas
    try:
        response = requests.get(f"{BASE_URL}/api/maquinas")
        print(f"✓ /api/maquinas - Status: {response.status_code}")
        maquinas = response.json()
        print(f"  Máquinas disponíveis: {len(maquinas)}")
        if maquinas:
            print(f"  Primeira máquina: {maquinas[0]}")
    except Exception as e:
        print(f"✗ /api/maquinas - Erro: {e}")
    
    # Teste endpoint de ferramentas
    try:
        response = requests.get(f"{BASE_URL}/api/ferramentas")
        print(f"✓ /api/ferramentas - Status: {response.status_code}")
        ferramentas = response.json()
        print(f"  Ferramentas disponíveis: {len(ferramentas)}")
        if ferramentas:
            print(f"  Primeira ferramenta: {ferramentas[0]}")
    except Exception as e:
        print(f"✗ /api/ferramentas - Erro: {e}")
    
    # Teste endpoint de produtos
    try:
        response = requests.get(f"{BASE_URL}/api/produtos")
        print(f"✓ /api/produtos - Status: {response.status_code}")
        produtos = response.json()
        print(f"  Produtos disponíveis: {len(produtos)}")
    except Exception as e:
        print(f"✗ /api/produtos - Erro: {e}")

def test_criar_produto_com_etapas():
    """Testa a criação de um produto com etapas"""
    print("\n=== Testando Criação de Produto com Etapas ===")
    
    # Primeiro, obter máquinas e ferramentas disponíveis
    try:
        maquinas_response = requests.get(f"{BASE_URL}/api/maquinas")
        ferramentas_response = requests.get(f"{BASE_URL}/api/ferramentas")
        
        maquinas = maquinas_response.json()
        ferramentas = ferramentas_response.json()
        
        if not maquinas and not ferramentas:
            print("✗ Nenhuma máquina ou ferramenta disponível para teste")
            return
        
        # Usar primeira máquina ou ferramenta disponível
        equipamento = maquinas[0] if maquinas else ferramentas[0]
        equipamento_id = equipamento['id']
        equipamento_nome = equipamento['nome']
        
        print(f"  Usando equipamento: {equipamento_nome} (ID: {equipamento_id})")
        
        # Dados do produto de teste
        produto_data = {
            "nome": "Produto Teste Etapas",
            "descricao": "Produto para testar etapas com equipamentos",
            "preco": 100.00,
            "categoria": "Teste",
            "etapas": [
                {
                    "nome": "Etapa 1 - Preparação",
                    "tipo": "Automatizado",
                    "equipamento_id": equipamento_id,
                    "equipamento_nome": equipamento_nome,
                    "material_id": None,
                    "material_nome": "",
                    "tempoEstimado": 30,
                    "custo": 25.00
                },
                {
                    "nome": "Etapa 2 - Finalização",
                    "tipo": "Manual",
                    "equipamento_id": None,
                    "equipamento_nome": "",
                    "material_id": None,
                    "material_nome": "",
                    "tempoEstimado": 15,
                    "custo": 10.00
                }
            ]
        }
        
        print(f"  Dados do produto: {json.dumps(produto_data, indent=2)}")
        
        # Enviar requisição para criar produto
        response = requests.post(
            f"{BASE_URL}/api/produtos",
            json=produto_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"  Resposta: Status {response.status_code}")
        if response.status_code == 201:
            print("✓ Produto criado com sucesso!")
            produto_criado = response.json()
            print(f"  ID do produto criado: {produto_criado.get('id')}")
            return produto_criado.get('id')
        else:
            print(f"✗ Erro ao criar produto: {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ Erro no teste: {e}")
        return None

def test_editar_produto_com_etapas(produto_id):
    """Testa a edição de um produto com etapas"""
    if not produto_id:
        print("✗ ID do produto não fornecido para teste de edição")
        return
    
    print(f"\n=== Testando Edição de Produto com Etapas (ID: {produto_id}) ===")
    
    try:
        # Obter dados do produto
        response = requests.get(f"{BASE_URL}/api/produtos/{produto_id}")
        if response.status_code != 200:
            print(f"✗ Erro ao obter produto: {response.status_code}")
            return
        
        produto = response.json()
        print(f"  Produto obtido: {produto['nome']}")
        
        # Modificar dados do produto
        produto_data = {
            "nome": produto['nome'] + " (Editado)",
            "descricao": produto['descricao'] + " - Versão editada",
            "preco": float(produto['preco']) + 50.00,
            "categoria": produto['categoria'],
            "etapas": produto.get('etapas', [])
        }
        
        # Adicionar uma nova etapa
        if produto_data['etapas']:
            produto_data['etapas'].append({
                "nome": "Etapa 3 - Controle de Qualidade",
                "tipo": "Manual",
                "equipamento_id": None,
                "equipamento_nome": "",
                "material_id": None,
                "material_nome": "",
                "tempoEstimado": 10,
                "custo": 5.00
            })
        
        print(f"  Dados atualizados: {json.dumps(produto_data, indent=2)}")
        
        # Enviar requisição para atualizar produto
        response = requests.put(
            f"{BASE_URL}/api/produtos/{produto_id}",
            json=produto_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"  Resposta: Status {response.status_code}")
        if response.status_code == 200:
            print("✓ Produto editado com sucesso!")
            return True
        else:
            print(f"✗ Erro ao editar produto: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Erro no teste: {e}")
        return False

def main():
    """Função principal do teste"""
    print("Iniciando testes do sistema de produtos com etapas...")
    print("=" * 60)
    
    # Aguardar um pouco para garantir que o servidor esteja pronto
    time.sleep(2)
    
    # Testar endpoints
    test_endpoints()
    
    # Testar criação de produto
    produto_id = test_criar_produto_com_etapas()
    
    # Testar edição de produto
    if produto_id:
        test_editar_produto_com_etapas(produto_id)
    
    print("\n" + "=" * 60)
    print("Testes concluídos!")

if __name__ == "__main__":
    main()
