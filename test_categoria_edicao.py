#!/usr/bin/env python3

"""
Teste específico para verificar o processamento de categorias de anexos
durante a edição de produto
"""

import requests
import json
from io import BytesIO

def test_attachment_categories():
    """Testa o envio de categorias para anexos na edição de produto"""
    
    # URL do backend
    base_url = "http://127.0.0.1:8000"
    produto_id = 69  # ID do produto teste
    
    print("🔍 Testando categorias de anexos na edição de produto...")
    print(f"Produto ID: {produto_id}")
    print()
    
    # Preparar dados do produto (simplificados)
    produto_data = {
        "nome": "teste",
        "codigo": "1", 
        "categoria": "Adesivo em recorte eletrônico",
        "preco": 344.46,
        "margem": 4,
        "descricao": "",
        "especificacoes": "",
        "materiais": [],
        "etapas": [],
        "custoMateriais": 0,
        "custoEtapas": 0,
        "custoTotal": 0
    }
    
    # Simular arquivo de teste
    test_file_content = b"Conteudo do arquivo de teste"
    
    # Preparar FormData
    files = {
        'anexos': ('teste_categoria.txt', BytesIO(test_file_content), 'text/plain')
    }
    
    data = {
        'dados': json.dumps(produto_data),
        'anexo_categoria_0': 'Material de Impressão',  # Categoria para o primeiro anexo
    }
    
    print("📤 Enviando dados:")
    print(f"  - dados: {produto_data['nome']}")
    print(f"  - anexo_categoria_0: {data['anexo_categoria_0']}")
    print(f"  - arquivo: teste_categoria.txt")
    print()
    
    try:
        # Fazer a requisição
        response = requests.put(f"{base_url}/api/produtos/{produto_id}", files=files, data=data)
        
        print(f"📥 Resposta do servidor:")
        print(f"  - Status: {response.status_code}")
        print(f"  - Headers: {dict(response.headers)}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            result = response.json()
            print(f"  - JSON: {result}")
        else:
            print(f"  - Texto: {response.text[:200]}...")
        
        print()
        
        if response.status_code == 200:
            print("✅ Requisição bem-sucedida!")
            
            # Verificar se o anexo foi salvo com a categoria correta
            anexos_response = requests.get(f"{base_url}/api/produtos/{produto_id}/anexos")
            if anexos_response.status_code == 200:
                anexos_data = anexos_response.json()
                print(f"📎 Anexos do produto após edição:")
                for anexo in anexos_data.get('anexos', []):
                    print(f"  - {anexo.get('nome_original', 'N/A')} (Categoria: {anexo.get('descricao', 'N/A')})")
            
        else:
            print(f"❌ Erro na requisição: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exceção: {str(e)}")

if __name__ == "__main__":
    test_attachment_categories()
