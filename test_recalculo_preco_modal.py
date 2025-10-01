#!/usr/bin/env python3
"""
Teste para verificar o recálculo automático do preço no modal de edição
quando um novo material é adicionado.

Este teste executa o Flask para permitir teste manual da funcionalidade.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask_gui import app
import threading
import time
import webbrowser

def print_test_instructions():
    print("=" * 60)
    print("TESTE: Recálculo de Preço no Modal de Edição")
    print("=" * 60)
    print()
    print("CENÁRIO DE TESTE:")
    print("1. Abrir a página de produtos")
    print("2. Editar um produto existente")
    print("3. Adicionar um novo material no modal de edição")
    print("4. Verificar se o preço final é recalculado automaticamente")
    print()
    print("PASSOS DETALHADOS:")
    print("1. Clique no botão 'Produtos' no menu lateral")
    print("2. Clique no ícone de edição (lápis) de qualquer produto")
    print("3. No modal de edição, clique em 'Adicionar Material'")
    print("4. Selecione qualquer material da lista")
    print("5. Observe o campo 'Preço Final' - deve ser atualizado automaticamente")
    print()
    print("RESULTADO ESPERADO:")
    print("- O preço final deve ser recalculado imediatamente após adicionar o material")
    print("- O novo preço deve refletir o custo do material adicionado + margem de lucro")
    print()
    print("VALIDAÇÃO:")
    print("- Se o preço for recalculado automaticamente: TESTE PASSOU ✓")
    print("- Se o preço não for atualizado: TESTE FALHOU ✗")
    print()
    print("=" * 60)
    print("Servidor Flask iniciado em: http://localhost:5000")
    print("A página será aberta automaticamente em 3 segundos...")
    print("Pressione Ctrl+C para parar o servidor")
    print("=" * 60)

def open_browser():
    time.sleep(3)
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    print_test_instructions()
    
    # Abrir o navegador após 3 segundos
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\nTeste finalizado.")
        print("Obrigado por testar o sistema de recálculo de preços!")
