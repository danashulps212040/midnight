#!/usr/bin/env python3
"""
Teste para verificar se a categoria dos anexos está sendo salva corretamente.
"""

import os
import sys
import tempfile
from database import Database

def test_anexo_com_categoria():
    """Teste de inserção de anexo com categoria"""
    
    # Dados de teste
    produto_id = 63  # Usando produto existente
    nome_arquivo = "teste_layout.pdf"
    categoria = "Layout/Design"
    conteudo_teste = b"Conteudo de teste do PDF"
    tamanho = len(conteudo_teste)
    tipo_mime = "application/pdf"
    
    # Conectar ao banco
    db = Database()
    
    try:
        print("=== TESTE DE ANEXO COM CATEGORIA ===")
        print(f"Produto ID: {produto_id}")
        print(f"Nome do arquivo: {nome_arquivo}")
        print(f"Categoria: {categoria}")
        print(f"Tamanho: {tamanho} bytes")
        print(f"Tipo MIME: {tipo_mime}")
        print()
        
        # Inserir anexo com categoria
        print("1. Inserindo anexo com categoria...")
        anexo_id = db.inserir_anexo_produto(
            produto_id=produto_id,
            nome_original=nome_arquivo,
            conteudo_blob=conteudo_teste,
            tamanho=tamanho,
            tipo_mime=tipo_mime,
            descricao=categoria
        )
        
        if anexo_id:
            print(f"✅ Anexo inserido com sucesso! ID: {anexo_id}")
        else:
            print("❌ Erro ao inserir anexo")
            return False
        
        # Listar anexos do produto para verificar se a categoria foi salva
        print("2. Verificando se a categoria foi salva...")
        anexos = db.listar_anexos_produto(produto_id)
        
        anexo_encontrado = None
        for anexo in anexos:
            if anexo['id'] == anexo_id:
                anexo_encontrado = anexo
                break
        
        if anexo_encontrado:
            print(f"✅ Anexo encontrado: {anexo_encontrado['nome_original']}")
            print(f"✅ Categoria salva: {anexo_encontrado.get('descricao', 'VAZIO')}")
            
            if anexo_encontrado.get('descricao') == categoria:
                print("✅ Categoria salva corretamente!")
                resultado = True
            else:
                print(f"❌ Categoria incorreta. Esperado: {categoria}, Obtido: {anexo_encontrado.get('descricao')}")
                resultado = False
        else:
            print("❌ Anexo não encontrado na listagem")
            resultado = False
        
        # Remover anexo de teste
        print("3. Removendo anexo de teste...")
        if db.remover_anexo_produto(anexo_id):
            print("✅ Anexo removido com sucesso")
        else:
            print("❌ Erro ao remover anexo")
        
        return resultado
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        return False
    finally:
        db.close()

def test_multiple_categories():
    """Teste com múltiplas categorias"""
    
    db = Database()
    produto_id = 63  # Usando produto existente
    
    categorias_teste = [
        ("arquivo_corte.dwg", "Arquivo de Corte"),
        ("layout_final.pdf", "Layout/Design"),
        ("mockup_cliente.jpg", "Mockup/Prova"),
        ("especificacoes.doc", "Especificações Técnicas"),
        ("orcamento.xlsx", "Orçamento/Cotação")
    ]
    
    anexos_criados = []
    
    try:
        print("\n=== TESTE DE MÚLTIPLAS CATEGORIAS ===")
        
        for nome_arquivo, categoria in categorias_teste:
            print(f"Testando: {nome_arquivo} -> {categoria}")
            
            conteudo_teste = f"Conteudo de teste para {nome_arquivo}".encode()
            
            anexo_id = db.inserir_anexo_produto(
                produto_id=produto_id,
                nome_original=nome_arquivo,
                conteudo_blob=conteudo_teste,
                tamanho=len(conteudo_teste),
                tipo_mime="application/octet-stream",
                descricao=categoria
            )
            
            if anexo_id:
                anexos_criados.append(anexo_id)
                print(f"  ✅ Inserido com ID: {anexo_id}")
            else:
                print(f"  ❌ Erro ao inserir {nome_arquivo}")
        
        # Verificar todos os anexos
        print("\nVerificando categorias salvas...")
        anexos = db.listar_anexos_produto(produto_id)
        
        for anexo in anexos:
            if anexo['id'] in anexos_criados:
                categoria_salva = anexo.get('descricao', 'VAZIO')
                print(f"  {anexo['nome_original']} -> {categoria_salva}")
        
        # Limpar anexos de teste
        print("\nLimpando anexos de teste...")
        for anexo_id in anexos_criados:
            db.remover_anexo_produto(anexo_id)
        
        print("✅ Teste de múltiplas categorias concluído")
        
    except Exception as e:
        print(f"❌ Erro no teste de múltiplas categorias: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Testando sistema de categorias de anexos...")
    
    # Teste básico
    sucesso = test_anexo_com_categoria()
    
    if sucesso:
        # Teste com múltiplas categorias
        test_multiple_categories()
        print("\n🎉 Todos os testes concluídos!")
    else:
        print("\n❌ Teste básico falhou. Verifique o banco de dados.")
