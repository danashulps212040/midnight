#!/usr/bin/env python3
"""Teste da API de produtos para verificar se a margem está sendo retornada"""

import sys
import os
import json

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database

def test_api_produtos():
    """Testa se a API de produtos retorna a margem"""
    try:
        db = Database()
        produtos = db.listar_produtos()
        db.close()
        
        if isinstance(produtos, list) and len(produtos) > 0:
            print("✅ Produtos encontrados:")
            for i, produto in enumerate(produtos[:3]):  # Mostrar apenas os primeiros 3
                margem = produto.get('margem', 'N/A')
                print(f"  {i+1}. {produto.get('nome', 'Nome não disponível')}")
                print(f"     Código: {produto.get('codigo', 'N/A')}")
                print(f"     Preço: R$ {produto.get('preco', 0)}")
                print(f"     Margem: {margem}%")
                print(f"     Categoria: {produto.get('categoria', 'N/A')}")
                print()
            
            # Verificar se pelo menos um produto tem margem definida
            produtos_com_margem = [p for p in produtos if p.get('margem') is not None and p.get('margem') != 0]
            print(f"📊 Total de produtos: {len(produtos)}")
            print(f"📈 Produtos com margem definida: {len(produtos_com_margem)}")
            
            if len(produtos_com_margem) > 0:
                print("✅ A coluna margem está sendo retornada corretamente pela API!")
            else:
                print("⚠️  Nenhum produto tem margem definida no banco de dados.")
                
        else:
            print("❌ Nenhum produto encontrado ou erro na consulta.")
            print(f"Resultado: {produtos}")
            
    except Exception as e:
        print(f"❌ Erro ao testar API: {e}")

if __name__ == '__main__':
    print("🔍 Testando API de produtos...")
    test_api_produtos()
