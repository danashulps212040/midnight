#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database

def testar_edicao_produto_com_anexo():
    """Testa o fluxo completo de edição de produto com anexo usando requests"""
    
    # Criar um produto para teste
    db = Database()
    
    # Primeiro, criar um produto
    produto_data = {
        'nome': 'Produto Teste Edição',
        'codigo': 'TEST-EDIT-001',
        'categoria': 'Papelaria',
        'preco': 50.0,
        'margem': 30.0,
        'descricao': 'Produto para teste de edição',
        'especificacoes': 'Especificações teste',
        'custo_materiais': 20.0,
        'custo_etapas': 15.0
    }
    
    resultado = db.criar_produto(produto_data)
    if 'erro' in resultado:
        print(f"❌ Erro ao criar produto: {resultado['erro']}")
        db.close()
        return
    
    produto_id = resultado['id']
    print(f"✅ Produto criado com ID: {produto_id}")
    
    # Testar o upload via frontend (Flask)
    import requests
    import io
    
    try:
        # Preparar dados de edição
        dados_edicao = {
            'nome': 'Produto Teste Edição EDITADO',
            'codigo': 'TEST-EDIT-001',
            'categoria': 'Papelaria',
            'preco': 55.0,
            'margem': 35.0,
            'descricao': 'Produto para teste de edição EDITADO',
            'especificacoes': 'Especificações teste EDITADAS',
            'materiais': [],
            'etapas': [],
            'custoMateriais': 20.0,
            'custoEtapas': 15.0,
            'custoTotal': 35.0
        }
        
        # Criar um arquivo de teste
        arquivo_teste = io.BytesIO(b"Conteudo do arquivo de teste para edicao")
        
        # Preparar FormData como no frontend
        files = {'anexos': ('teste-edicao.txt', arquivo_teste, 'text/plain')}
        data = {
            'dados': str(dados_edicao).replace("'", '"'),  # Simular JSON string
            'anexo_categoria_0': 'layout'
        }
        
        print(f"📤 Enviando dados para edição:")
        print(f"   - Dados: {data['dados']}")
        print(f"   - Categoria anexo: {data['anexo_categoria_0']}")
        
        # Fazer a requisição de edição
        response = requests.put(
            f'http://localhost:5000/api/produtos/{produto_id}',
            files=files,
            data=data
        )
        
        print(f"📥 Resposta HTTP: {response.status_code}")
        print(f"📥 Resposta JSON: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Edição com anexo bem-sucedida!")
            
            # Verificar se o anexo foi salvo
            anexos = db.listar_anexos_produto(produto_id)
            print(f"📎 Anexos encontrados: {len(anexos)}")
            for anexo in anexos:
                print(f"   - {anexo['nome_original']} | Categoria: {anexo.get('descricao', 'Sem categoria')}")
                
        else:
            print(f"❌ Erro na edição: {response.json()}")
            
    except Exception as e:
        print(f"❌ Erro no teste: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Limpar produto de teste
        db.excluir_produto(produto_id)
        db.close()
        print(f"🧹 Produto de teste removido")

if __name__ == "__main__":
    testar_edicao_produto_com_anexo()
