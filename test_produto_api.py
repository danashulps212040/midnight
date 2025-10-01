#!/usr/bin/env python3
"""
Script para testar a API de busca de produto por ID
"""

import requests
import json

def testar_api_produto():
    # Primeiro, vamos listar os produtos disponíveis
    print("=== Listando produtos disponíveis ===")
    try:
        response = requests.get('http://localhost:5000/api/produtos')
        if response.status_code == 200:
            data = response.json()
            # Verificar se a resposta é uma lista direta ou um objeto com produtos
            if isinstance(data, list):
                produtos = data[:3]  # Resposta direta como lista
                print(f"Encontrados {len(data)} produtos. Testando os primeiros 3:")
            elif data.get('status') == 'success' and data.get('produtos'):
                produtos = data['produtos'][:3]  # Resposta como objeto com produtos
                print(f"Encontrados {len(data['produtos'])} produtos. Testando os primeiros 3:")
            else:
                produtos = []
                print("Formato de resposta não reconhecido")
            
            if produtos:
                for produto in produtos:
                    print(f"  ID: {produto['id']}, Nome: {produto['nome']}, Categoria: {produto.get('categoria', 'N/A')}")
                
                # Testar API de busca por ID com o primeiro produto
                produto_id = produtos[0]['id']
                print(f"\n=== Testando busca do produto ID {produto_id} ===")
                
                response = requests.get(f'http://localhost:5000/api/produtos/{produto_id}')
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print("Dados retornados:")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                    
                    if data.get('status') == 'success':
                        produto = data['produto']
                        print(f"\n=== Análise dos dados do produto ===")
                        print(f"Nome: {produto.get('nome')}")
                        print(f"Categoria ID: {produto.get('categoria_id')}")
                        print(f"Categoria Nome: {produto.get('categoria')}")
                        print(f"Preço: {produto.get('preco')}")
                        print(f"Margem: {produto.get('margem')}")
                        print(f"Custo Materiais: {produto.get('custoMateriais')}")
                        print(f"Custo Etapas: {produto.get('custoEtapas')}")
                        print(f"Materiais: {len(produto.get('materiais', []))}")
                        print(f"Etapas: {len(produto.get('etapas', []))}")
                else:
                    print(f"Erro: {response.text}")
            else:
                print("Nenhum produto encontrado ou erro na API")
        else:
            print(f"Erro ao listar produtos: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Erro ao conectar com a API: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    testar_api_produto()
