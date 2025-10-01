#!/usr/bin/env python3

"""
Teste completo para verificar o processamento de categorias durante edição
"""

import requests
import json
from io import BytesIO
import time

def test_edit_with_attachment():
    """Testa edição de produto com adição de anexo"""
    
    base_url = "http://127.0.0.1:8000"
    produto_id = 69
    
    print("🔧 Teste: Edição de produto com novo anexo")
    print(f"Produto ID: {produto_id}")
    print()
    
    # Primeiro, vamos verificar o estado atual dos anexos
    print("1. Verificando anexos existentes...")
    response = requests.get(f"{base_url}/api/produtos/{produto_id}/anexos")
    if response.status_code == 200:
        current_attachments = response.json()
        print(f"   Anexos atuais: {len(current_attachments.get('anexos', []))}")
        for i, anexo in enumerate(current_attachments.get('anexos', [])):
            print(f"   [{i}] {anexo.get('nome_original', 'N/A')} (Categoria: {anexo.get('descricao', 'N/A')})")
    else:
        print(f"   Erro ao buscar anexos: {response.status_code}")
    print()
    
    # Preparar dados do produto
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
    
    # Criar arquivo de teste único
    timestamp = int(time.time())
    filename = f"test_categoria_{timestamp}.txt"
    file_content = f"Arquivo de teste criado em {timestamp}".encode('utf-8')
    
    print("2. Enviando produto com novo anexo...")
    print(f"   Arquivo: {filename}")
    print(f"   Categoria: 'Layout/Design'")
    print()
    
    # Preparar FormData exatamente como o frontend faz
    files = {
        'anexos': (filename, BytesIO(file_content), 'text/plain')
    }
    
    data = {
        'dados': json.dumps(produto_data),
        'anexo_categoria_0': 'Layout/Design',  # Categoria para o primeiro (e único) novo anexo
    }
    
    print("3. Dados enviados:")
    print(f"   FormData keys: {list(data.keys())}")
    print(f"   Files keys: {list(files.keys())}")
    print(f"   anexo_categoria_0 = '{data['anexo_categoria_0']}'")
    print()
    
    # Fazer a requisição
    response = requests.put(f"{base_url}/api/produtos/{produto_id}", files=files, data=data)
    
    print("4. Resposta do servidor:")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            result = response.json()
            print(f"   Resultado: {result}")
            
            # Verificar anexos após a operação
            print("\n5. Verificando anexos após edição...")
            response = requests.get(f"{base_url}/api/produtos/{produto_id}/anexos")
            if response.status_code == 200:
                updated_attachments = response.json()
                print(f"   Total anexos: {len(updated_attachments.get('anexos', []))}")
                for i, anexo in enumerate(updated_attachments.get('anexos', [])):
                    print(f"   [{i}] {anexo.get('nome_original', 'N/A')} (Categoria: {anexo.get('descricao', 'N/A')})")
                    
                # Verificar se o novo arquivo foi adicionado com a categoria correta
                new_attachment = None
                for anexo in updated_attachments.get('anexos', []):
                    if anexo.get('nome_original') == filename:
                        new_attachment = anexo
                        break
                
                if new_attachment:
                    if new_attachment.get('descricao') == 'Layout/Design':
                        print(f"   ✅ Anexo '{filename}' adicionado com categoria correta: '{new_attachment.get('descricao')}'")
                    else:
                        print(f"   ❌ Anexo '{filename}' tem categoria incorreta: '{new_attachment.get('descricao')}' (esperado: 'Layout/Design')")
                else:
                    print(f"   ❌ Anexo '{filename}' não foi encontrado nos anexos do produto")
            else:
                print(f"   Erro ao buscar anexos: {response.status_code}")
                
        except Exception as e:
            print(f"   Erro ao processar resposta: {e}")
            print(f"   Resposta texto: {response.text}")
    else:
        print(f"   Erro: {response.status_code}")
        print(f"   Resposta: {response.text}")

if __name__ == "__main__":
    test_edit_with_attachment()
