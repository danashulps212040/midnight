#!/usr/bin/env python3
"""Script para verificar se a coluna margem está sendo exibida corretamente"""

import webbrowser
import time
import os

def test_margem_column():
    """Abre a página de produtos no navegador para teste manual"""
    
    print("🧪 Teste da coluna Margem nos Produtos")
    print("=" * 50)
    print()
    print("Passos para testar:")
    print("1. ✅ Coluna 'Margem' deve aparecer no cabeçalho da tabela")
    print("2. ✅ Margem deve ser exibida em % para cada produto")
    print("3. ✅ Teste: Digite algo na barra de pesquisa")
    print("4. ✅ Teste: Adicione um novo produto")
    print("5. ✅ Verificar: O filtro de pesquisa deve ser mantido após adicionar o produto")
    print()
    print("🚀 Abrindo página de produtos no navegador...")
    
    # Abrir página de produtos
    url = "http://localhost:8000/produtos"
    webbrowser.open(url)
    
    print(f"📱 Página aberta: {url}")
    print()
    print("💡 Dicas para o teste:")
    print("   - Verifique se a coluna 'Margem' aparece entre 'Preço' e 'Etapas'")
    print("   - Teste pesquisar por um produto")
    print("   - Adicione um novo produto e veja se o filtro é mantido")
    print("   - A margem deve aparecer em formato de porcentagem (ex: 25.5%)")

if __name__ == '__main__':
    test_margem_column()
