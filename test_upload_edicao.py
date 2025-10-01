#!/usr/bin/env python3
"""
Teste para verificar upload de anexos na edição de produto.
"""

import requests
import io
import sys

def test_upload_anexo_edicao():
    """Testa upload de anexo na edição de produto"""
    
    # Configurações
    base_url = "http://127.0.0.1:8000"
    produto_id = 68  # ID do produto que você estava editando
    
    # Criar arquivo de teste
    arquivo_teste = io.BytesIO(b"Conteudo de teste para anexo de edicao")
    arquivo_teste.name = "teste_edicao.pdf"
    
    # Dados do produto (simulando o que vem do frontend)
    dados_produto = {
        "nome": "Produto teste",
        "codigo": "TEST001",
        "categoria": "1",
        "preco": "100.00",
        "margem": "20",
        "descricao": "Teste",
        "especificacoes": "Teste",
        "materiais": [],
        "etapas": [],
        "custoMateriais": "0",
        "custoEtapas": "0",
        "custoTotal": "0"
    }
    
    # Preparar FormData
    files = {
        'anexos': ('teste_edicao.pdf', arquivo_teste, 'application/pdf')
    }
    
    form_data = {
        'dados': str(dados_produto).replace("'", '"'),  # Simular JSON.stringify
        'anexo_categoria_0': 'Layout/Design',
        'anexosParaDeletar': '[]'
    }
    
    print(f"=== TESTE DE UPLOAD DE ANEXO NA EDIÇÃO ===")
    print(f"URL: {base_url}/api/produtos/{produto_id}")
    print(f"Dados: {form_data}")
    print(f"Arquivos: {list(files.keys())}")
    
    try:
        # Fazer request
        response = requests.put(
            f"{base_url}/api/produtos/{produto_id}",
            data=form_data,
            files=files,
            timeout=30
        )
        
        print(f"\nResposta HTTP: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            print(f"JSON Response: {response.json()}")
        else:
            print(f"Response Text: {response.text[:500]}")
            
        return response.status_code == 200
        
    except Exception as e:
        print(f"Erro na requisição: {str(e)}")
        return False

def test_upload_simples():
    """Teste mais simples - apenas verificar se o endpoint responde"""
    
    base_url = "http://127.0.0.1:8000"
    produto_id = 68
    
    # Dados mínimos sem anexos
    dados_produto = {
        "nome": "Produto teste",
        "codigo": "TEST001", 
        "categoria": "1",
        "preco": "100.00"
    }
    
    print(f"\n=== TESTE SIMPLES SEM ANEXOS ===")
    
    try:
        response = requests.put(
            f"{base_url}/api/produtos/{produto_id}",
            json=dados_produto,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Erro: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testando upload de anexos na edição de produto...\n")
    
    # Teste 1: Simples sem anexos
    sucesso_simples = test_upload_simples()
    
    # Teste 2: Com anexos
    if sucesso_simples:
        print("\n" + "="*50)
        sucesso_anexo = test_upload_anexo_edicao()
        
        if sucesso_anexo:
            print("\n✅ Todos os testes passaram!")
        else:
            print("\n❌ Teste com anexo falhou")
    else:
        print("\n❌ Teste simples falhou - verifique o servidor")
